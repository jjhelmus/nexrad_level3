
import struct
import datetime
import bz2

import numpy as np

class NexradLevel3File():
    """
    """

    def __init__(self, filename):

        # read the entire file into memory
        fh = open(filename, 'rb')
        self._buf = fh.read()
        fh.close()

        # Text header, various sizes
        if self._buf.find('\n') == -1:
            bpos = 0
        else:
            last_newline = self._buf.find('\n')
            while self._buf.find('\n', last_newline + 1) != -1:
                next_newline = self._buf.find('\n', last_newline + 1)
                if next_newline - last_newline > 50:
                    break
                last_newline = next_newline
            bpos = last_newline + 1

        print "bpos:", bpos
        # 18 byte Message Header Block
        self._msg_header = _unpack_from_buf(self._buf, bpos, MESSAGE_HEADER)
        bpos += 18

        print self._msg_header
        if self._msg_header['code'] not in SUPPORTED_PRODUCTS:
            print "Code:", self._msg_header['code']
            raise NotImplemented('This Level3 product is not supported')

        # 102 byte Product Description Block
        self._prod_descr = _unpack_from_buf(self._buf, bpos,
                                            PRODUCT_DESCRIPTION)

        prod_params = _get_product_parameters(self._msg_header['code'],
                                              self._prod_descr)
        self._prod_params = prod_params
        bpos += 102

        # uncompressed Symbology Block is necessary
        if 'compressed' in prod_params and prod_params['compressed']:
            self._buf2 = bz2.decompress(self._buf[bpos:])
        else:
            self._buf2 = self._buf[bpos:]

        # symbology header
        self._symbology_header = _unpack_from_buf(self._buf2, 0,
                                                  SYMBOLOGY_HEADER)

        SUPPORTED_PACKET_CODES = [16]       # elsewhere
        packet_code = struct.unpack('>h', self._buf2[16:18])[0]
        if packet_code not in SUPPORTED_PACKET_CODES:
            raise NotImplemented('Packet code: %i' % packet_code)

        # XXX base this on the packet code
        self._packet_header = _unpack_from_buf(self._buf2, 16,
                                               PACKET_TYPE16_HEADER)
        rh = []
        #rd = []

        nbins = self._packet_header['nbins']
        nradials = self._packet_header['nradials']

        raw_data = np.empty((nradials, nbins), dtype='uint8')

        pos = 30
        for i in range(nradials):
            rh.append(_unpack_from_buf(self._buf2, pos,
                                       PACKET_TYPE16_RADIAL_HEADER))
            pos += 6
            raw_data[i] = np.fromstring(self._buf2[pos:pos+nbins], '>u1')
            #rd.append(self._buf2[pos:pos+nbins])
            #correct data = rd * 0.5 - 33.0
            pos += nbins

        print "pos:", pos
        print "len(buf2)", len(self._buf2)

        self._radial_headers = rh
        self._raw_data = raw_data

        # scale according to threshold_data
        # XXX this works for products 32, 94, 153, 194, 195
        s = self._prod_descr['threshold_data']
        hw31, hw32, hw33 = np.fromstring(s[:6], '>i2')

        data = (raw_data - 2) * (hw32/10.) + hw31/10.
        mdata = np.ma.array(data, mask=raw_data < 2)

        self.data = mdata

def datetime_from_mdate_mtime(mdate, mtime):
    """ Returns a datetime for a given message date and time. """
    epoch = datetime.datetime.utcfromtimestamp(0)
    return epoch + datetime.timedelta(days = mdate - 1, seconds=mtime)

def _structure_size(structure):
    """ Find the size of a structure in bytes. """
    return struct.calcsize('>' + ''.join([i[1] for i in structure]))


def _unpack_from_buf(buf, pos, structure):
    """ Unpack a structure from a buffer. """
    size = _structure_size(structure)
    return _unpack_structure(buf[pos:pos + size], structure)


def _unpack_structure(string, structure):
    """ Unpack a structure from a string """
    fmt = '>' + ''.join([i[1] for i in structure])  # NEXRAD is big-endian
    l = struct.unpack(fmt, string)
    return dict(zip([i[0] for i in structure], l))

def _get_product_parameters(code, prod_descr):
    """ """

    s = prod_descr['halfwords_27_28']
    w27, w28 = s[0:2], s[2:4]
    w30 = prod_descr['halfwords_30']
    s = prod_descr['halfwords_47_53']
    w47, w48, w49, w50, w51, w52, w53 = [s[2*i:2*i+2] for i in range(7)]

    #hw27, hw28 = struct.unpack('>2h', prod_descr['halfwords_27_28'])
    #hw30 = struct.unpack('>1h', prod_descr['halfwords_30'])
    #t = struct.unpack('>7h', prod_descr['halfwords_47_53'])
    #hw47, hw48, hw49, hw50, hw51, hw52, hw53 = t

    # Table V.
    # Product Dependent Halfword Definition for Product Description Block
    # pages 3-43 to 3-64
    # This full table is not implemented here
    if code == 94:   # Base Reflectivity Data Array

        return {
            'elevation_angle': struct.unpack('>h', w30)[0],     # XXX scale
            'max_reflectivity': struct.unpack('>h', w47)[0],    # XXX scale
            'compressed': struct.unpack('>h', w51)[0],
            'uncompressed_size': struct.unpack('>i', w52+w53)[0]
        }


# NEXRAD Level III file structures and sizes
# The deails on these structures are documented in:
# "INTERFACE CONTROL DOCUMENT FOR THE RPG TO CLASS 1 USER" RPG Build 13.0
# Document Number 2620001T
# Tables and page number refer to those in this document.

# format of structure elements
# Figure E-1, page E-1
BYTE = 'B'      # not in table but used in Product Description
INT2 = 'h'
INT4 = 'i'
UINT4 = 'I'
REAL4 = 'f'

# 3.3.1 Graphic Product Messages

# Graphic Product Message: Message Header Block
# 18 bytes, 9 halfwords
# Figure 3-3, page 3-7.
MESSAGE_HEADER = (
    ('code', INT2),     # message code
    ('date', INT2),     # date of message, days since 1 Jan, 1970
    ('time', INT4),     # time of message, seconds since midnight
    ('length', INT4),   # length of message in bytes
    ('source', INT2),   # Source ID
    ('dest', INT2),     # Destination ID
    ('nblocks', INT2),  # Number of blocks in the message (inclusive)
)

# Graphic Product Message: Product Description Block
# Description: section 3.3.1.1, page 3-3
# 102 bytes, 51 halfwords (halfwords 10-60)
# Figure 3-6, pages 3-31 and 3-32
PRODUCT_DESCRIPTION = (
    ('divider', INT2),          # Delineate blocks, -1
    ('latitude', INT4),         # Latitude of radar, degrees, + for north
    ('longitude', INT4),        # Longitude of radar, degrees, + for east
    ('height', INT2),           # Height of radar, feet abouve mean sea level
    ('product_code', INT2),     # NEXRAD product code
    ('operational_mode', INT2), # 0 = Maintenance, 1 = Clean Air, 2 = Precip
    ('vcp', INT2),              # Volume Coverage Pattern of scan strategy
    ('sequence_num', INT2),     # Sequence Number of the request.
    ('vol_scan_num', INT2),     # Volume Scan number, 1 to 80.
    ('vol_scan_date', INT2),    # Volume Scan start date, days since 1/1/1970
    ('vol_scan_time', INT4),    # Volume Scan start time, sec since midnight
    ('product_date', INT2),     # Product Generation Date, days since 1/1/1970
    ('product_time', INT4),     # Product Generation Time, sec since midnight
    ('halfwords_27_28', '4s'),  # Product dependent parameters 1 and 2
    ('elevation_num', INT2),    # Elevation number within volume scan
    ('halfwords_30', '2s'),     # Product dependent parameter 3
    ('threshold_data', '32s'),  # Data to determine threshold level values
    ('halfwords_47_53', '14s'), # Product dependent parameters 4-10
    ('version', BYTE),          # Version, 0
    ('spot_blank', BYTE),       # 1 = Spot blank ON, 0 = Blanking OFF
    ('offet_symbology', INT4),  # halfword offset to Symbology block
    ('offset_graphic', INT4),   # halfword offset to Graphic block
    ('offset_tabular', INT4)    # halfword offset to Tabular block
)

# Graphic Product Message: Product Symbology Block
# Description
# 16 byte header
# Figure 3-6 (Sheet 8), pages 3-40

SYMBOLOGY_HEADER = (
    ('divider', INT2),          # Delineate blocks, -1
    ('id', INT2),               # Block ID, 1
    ('block_length', INT4),     # Length of block in bytes
    ('layers', INT2),           # Number of data layers
    ('layer_divider', INT2),    # Delineate data layers, -1
    ('layer_length', INT4)      # Length of data layer in bytes
    # Display data packets
)

# Digital Radial Data Array Packet - Packet Code 16 (Sheet 2)
# Figure 3-11c (Sheet 1 and 2), page 3-120.
PACKET_TYPE16_HEADER = (
    ('packet_code', INT2),      # Packet Code, Type 16
    ('first_bin', INT2),        # Location of first range bin.
    ('nbins', INT2),            # Number of range bins.
    ('i_sweep_center', INT2),   # I coordinate of center of sweep.
    ('j_sweep_center', INT2),   # J coordinate of center of sweep.
    ('range_scale', INT2),      # Range Scale factor
    ('nradials', INT2)          # Total number of radials in the product
)

PACKET_TYPE16_RADIAL_HEADER = (
    ('nbytes', INT2),           # Number of bytes in the radial.
    ('angle_start', INT2),      # Starting angle at which data was collected.
    ('angle_delta', INT2)       # Delta angle from previous radial.
)

# Message Code for Products
# Table III pages 3-15 to 3-22
SUPPORTED_PRODUCTS = [

#   Code     # NTR  Product Name            Message format
#   ---------  ---  ----------------------- ----------------------------------
    16,      # 1    Base Reflectivity       Radial Image
    17,      # 1    Base Reflectivity       Radial Image
    18,      # 1    Base Reflectivity       Radial Image
    19,      # 1    Base Reflectivity       Radial Image
    20,      # 1    Base Reflectivity       Radial Image
    21,      # 1    Base Reflectivity       Radial Image
    22,      # 2    Base Velocity           Radial Image
    23,      # 2    Base Velocity           Radial Image
    24,      # 2    Base Velocity           Radial Image
    25,      # 2    Base Velocity           Radial Image
    26,      # 2    Base Velocity           Radial Image
    27,      # 2    Base Velocity           Radial image
    28,      # 3    Base Spectrum Width     Radial Image
    29,      # 3    Base Spectrum Width     Radial Image
    30,      # 3    Base Spectrum Width     Radial Image
#   31,      # 32   User Selectable Storm   Radial Image/Geographic Alpha
             # ...  Total Precipitation
    32,      # 33   Digital Hybrid Scan     Radial Image
             # ...  Reflectivty
    33,      # 33   Hybrid Scan             Radial Image
             # ...  Reflectivty
    34,      # 34   Clutter Filter Control  Radial Image
#   35,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
#   36,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
#   37,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
#   38,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
#   39,      #      Spare
#   40,      #      Spare
#   41,      # 8    Echo Tops               Raster Image
#   42,      #      Spare
#   43,      #      Spare
#   44,      #      Spare
#   45,      #      Spare
#   46,      #      Spare
#   47,      #      Spare
#   48,      # 12   VAD Wind Profile        Non-geographic Alphanumeric
#   49,      #      Spare
#   50,      # 14   Cross Section           Raster Image (Reflectivity)
             # ...  (Reflectivity)
#   51,      # 14   Cross Section           Raster Image (Velocity)
             # ...  (Velocity)
#   52,      #      Spare
#   53,      #      Spare
#   54,      #      Reserved
    55,      # 16   Storm Relative Mean     Radial Image (Region)
             # ...  Radial Velocity
    56,      # 16   Storm Relative Mean     Radial Image (Map)
             # ...  Radial Velocity
#   57,      # 17   Vertically Integrated   Raster Image
             # ...  Liquid
#   58,      # 18   Storm Tracking          Non-geographic Alpha
             # ...  Information
#   59,      # 19   Hail Index              Non-geographic Alpha
#   60,      #      Spare
#   61,      # 21   Tornado Vortex          Geographic and Non-geographic
             # ...  Signature               Alphanumeric
#   62,      # 22   Storm Structure         Alphanumeric
#   63,      # 23   Layer Composite         Raster Image (Layer 1 Average)
             # ...  Reflectivity
#   64,      # 23   Layer Composite         Raster Image (Layer 2 Average)
             # ...  Reflectivity
#   65,      # 23   Layer Composite         Raster Image (Layer 1 Maximum)
             # ...  Reflectivity
#   66,      # 23   Layer Composite         Raster Image (Layer 2 Maximum)
             # ...  Reflectivity
#   67,      # 23   Layer Composite         Raster Image
             # ...  Reflectivity - AP Removed
#   68,      #      Spare
#   69,      #      Spare
#   70,      #      Spare
#   71,      #      Spare
#   72,      #      Spare
#   73,      # 25   User Alert Message      Alphanumeric
#   74,      # 26   Radar Coded Message     Alphanumeric
#   75,      # 27   Free Text Message       Alphanumeric
#   76,      #      Reserved for internal PUP use.
    78,      # 28   Surface Rainfall Accum. Radial Image
             # ...  (1 hr)
    79,      # 28   Surface Rainfall Accum. Radial Image
             # ...  (3 hr)
    80,      # 29   Storm Total Rainfall    Radial Image
             # ...  Accumulation
#   81,      # 30   Hourly Digital          Raster Image / Alphanumeric
             # ...  Precipitation Array
#   82,      # 31   Supplemental            Alphanumeric
             # ...  Precipitation Data
#   83,      #      Spare
#   84,      # 12   Velocity Azimuth        Non-geographic Alphanumeric
             # ...  Display
#   85,      # 14   Cross Section           Raster Image (Reflectivity)
             # ...  Reflectivity
#   86,      # 14   Cross Section Velocity  Raster Image (Velocity)
#   87,      #      Spare
#   88,      #      Spare
#   89,      # 23   Layer Composite         Raster Image - Layer 3 Average
             # ...  Reflectivity
#   90,      # 23   Layer Composite         Raster Image - Layer 3 Maximum
             # ...  Reflectivity
#   91-92,   #      Reserved for internal PUP and RPG Use
    93,      # 35   ITWS Digital Base       Radial Image
             # ...  Velocity
    94,      # 1    Base Reflectivity Data  Radial Image
             # ...  Array
#   95,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
             # ...  Edited for AP
#   96,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
             # ...  Edited for AP
#   97,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
             # ...  Edited for AP
#   98,      # 6    Composite Reflectivity  Raster Image/Nongeographic Alpha
             # ...  Edited for AP
    99,      # 2    Base Velocity Data      Radial Image
             # ...  Array
#   100,     #      Site Adaptable parameters for VAD Wind Profile (Product 48)
#   101,     #      Storm Track             Alphanumeric Block
#   102,     #      Hail Index              Alphanumeric Block
#   103,     #      Spare
#   104,     #      TVS                     Alphanumeric Block
#   105,     #      Site Adaptable Parameters for Combined Shear
#   106,     #      Spare
#   107,     #      Surface Rainfall (1 hr) Alphanumeric Block
#   108,     #      Surface Rainfall (3 hr) Alphanumeric Block
#   109,     #      Storm Total Rainfall    Alphanumeric Block
             # ...  Accumulation
#   110,     #      Clutter Likelihood      Alphanumeric Block
             # ...  Reflectivity
#   111,     #      Clutter Likelihood      Alphanumeric Block
             # ...  Doppler
#   112-131, #      Reserved for Future Products
    132,     # 36   Clutter Likelihood      Radial Image
             # ...  Reflectivity
    133,     # 37   Clutter Likelihood      Radial Image
             # ...  Doppler
    134,     # 39   High Resolution VIL     Radial Image
    135,     # 41   Enhanced Echo Tops      Radial Image
#   136,     # 38   SuperOb Adaptable       Latitude, Longitude
             # ...                          (ICD packet code 27)
    137,     # 40   User Selectable Layer   Radial Image
             # ...  Composite Reflectivity
    138,     # 29   Digital Storm Total     Radial Image
             # ...  Precipitation
#   139,     #      Spare
#   140,     # 46   Gust Front MIGFA        Generic Data Format
#   141,     # 20   Mesocyclone Detection   Geographic and Non-geographic Alpha
#   143,     # 21   Tornado Vortex          Geographic and Non-geographic Alpha
             # ...  Signature Rapid Update
    144,     # 42   One-hour Snow Water     Radial Image
             # ...  Equivalent
    145,     # 42   One-hour Snow Depth     Radial Image
    146,     # 43   Storm Total Snow Water  Radial Image
             # ...  Equivalent
    147,     # 43   Storm Total Snow Depth  Radial Image
#   149,     # 20   Digital Mesocyclone     Generic Data Format
             # ...  Detection
    150,     # 44   User Selectable Snow    Radial Image
             # ...  Water Equivalent
    151,     # 44   User Selectable Snow    Radial Image
             # ...  Depth
#   152,     #      Archive III Status      Product Generic Data Format
    153,     # 1    Super Resolution        Radial Image
             # ...  Reflectivity Data Array
    154,     # 2    Super Resolution        Radial Image
             # ...  Velocity Data Array
    155,     # 3    Super Resolution        Radial Image
             # ...  Spectrum Width Data Array
#   156,     # 47   Eddy Dissipation Rate   Digital Radial Data Array
#   157,     # 47   Eddy Dissipation Rate   Digital Radial Data Array
             # ...  Confidence
    158,     # 48   Differential            Radial Image
             # ...  Reflectivity
    159,     # 48   Digital Differential    Radial Image
             # ...  Reflectivity
    160,     # 49   Correlation Coefficient Radial Image
    161,     # 49   Digital Correlation     Radial Image
             # ...  Coefficient
    162,     # 50   Specific Differential   Radial Image
             # ...  Phase
    163,     # 50   Digital Specific        Radial Image
             # ...  Differential Phase
    164,     # 51   Hydrometeor             Radial Image
             # ...  Classification
    165,     # 51   Digital Hydrometeor     Radial Image
             # ...  Classification
#   166,     # 52   Melting Layer           Linked Contour Vectors/
             # ...                          Set Color Level
    169,     # 53   One Hour Accumulation   Radial Image
    170,     # 54   Digital Accumulation    Radial Image
             # ...  Array
    171,     # 55   Storm Total             Radial Image
             # ...  Accumulation
    172,     # 56   Digital Storm Total     Radial Image
             # ...  Accumulation
    173,     # 57   Digital User-Selectable Radial Image
             # ...  Accumulation
    174,     # 58   Digital One-Hour        Radial Image
             # ...  Difference Accumulation
    175,     # 59   Digital Storm Total     Radial Image
             # ...  Difference Accumulation
#   176,     # 60   Digital Instantaneous   Generic Radial Product Format
             # ...  Precipitation Rate
    177,     # 51   Hybrid Hydrometeor      Radial Image
             # ...  Classification
#   178-193, #      Reserved for Future Products
    194,     # 1    Base Reflectivity Data  Radial Image
             # ...  Array (DoD Version)
    195,     # 61   Digital Reflectivity,   Radial Image
             # ..   DQA-Edited Data Array
#   196-198, #      Reserved for Future Products
    199,     # 2    Base Velocity Data      Radial Image
             # ...  Array (DoD Version)
#   200-210, #      Reserved for Future Products
#   211-220, #      Reserved for Future Products
#   221-230, #      Reserved for Future Products
#   231-240, #      Reserved for Future Products
#   241-250, #      Reserved for Future Products
#   251-260, #      Reserved for Future Products
#   261-270, #      Reserved for Future Products
#   271-280, #      Reserved for Future Products
#   281-290, #      Reserved for Future Products
#   291-296, #      Reserved for Internal RPG Use.
#   297-299, #      Reserved for Internal RPG Use.
]

