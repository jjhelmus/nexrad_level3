
import struct
import datetime
import bz2

import numpy as np


_8_OR_16_LEVELS = [19, 20, 25, 27, 28, 30, 56, 78, 79, 80, 169, 171, 181]

PRODUCT_RANGE_RESOLUTION = {
    19: 1.,     # 124 nm
    20: 2.,     # 248 nm
    25: 0.25,   # 32 nm
    27: 1.,
    28: 0.25,
    30: 1.,
    32: 1.,
    34: 1.,     # Java uses 0.
    56: 1.,
    78: 1.,
    79: 1.,
    80: 1.,
    94: 1.,
    99: 0.25,
    134: 1.,
    135: 1.,
    138: 1.,
    159: 0.25,
    161: 0.25,
    163: 0.25,
    165: 0.25,
    169: 1.,
    170: 1.,
    171: 1.,
    172: 1.,
    173: 1.,
    174: 1.,
    175: 1.,
    177: 0.25,
    181: 150.,
    182: 150.,
    186: 300.,
}


class NexradLevel3File():
    """
    A Class for accessing data in NEXRAD Level III (3) files.

    Attributes
    ----------
    text_header : dic
        File textual header.
    msg_header : dic
        Message header.
    prod_descr : dic
        Product description.
    symbology_header : dict
        Symbology header.
    packet_header : dict
        Radial data array packet header.
    radial_headers : list of dicts
        List of radials headers
    raw_data : array
        Raw unscaled, unmasked data.
    data : array
        Scaled, masked radial data.

    """

    def __init__(self, filename):
        """ initalize the object. """
        # read the entire file into memory
        fh = open(filename, 'rb')
        buf = fh.read()     # string buffer containing file data
        fh.close()

        # Text header
        # Format of Text header is SDUSXX KYYYY DDHHMM\r\r\nAAABBB\r\r\n
        self.text_header = buf[:30]
        bpos = 30       # current reading position in buffer

        # Read and decode 18 byte Message Header Block
        self.msg_header = _unpack_from_buf(buf, bpos, MESSAGE_HEADER)
        if self.msg_header['code'] not in SUPPORTED_PRODUCTS:
            code = self.msg_header['code']
            raise NotImplementedError(
                'Level3 product with code %i is not supported' % (code))
        bpos += 18

        # Read and decode 102 byte Product Description Block
        self.prod_descr = _unpack_from_buf(buf, bpos, PRODUCT_DESCRIPTION)
        bpos += 102

        # uncompressed symbology Block if necessary
        if buf[bpos:bpos+2] == 'BZ':
            buf2 = bz2.decompress(buf[bpos:])
        else:
            buf2 = buf[bpos:]

        # Read and decode symbology header
        self.symbology_header = _unpack_from_buf(buf2, 0, SYMBOLOGY_HEADER)
        packet_code = struct.unpack('>h', buf2[16:18])[0]
        if packet_code not in SUPPORTED_PACKET_CODES:
            print buf2[16:18].encode('hex')
            raise NotImplementedError('Packet code: %i' % (packet_code))

        # Read radial packets
        if packet_code == 16:
            self.packet_header = _unpack_from_buf(buf2, 16,
                                                  PACKET_TYPE16_HEADER)
            rh = []
            nbins = self.packet_header['nbins']
            nradials = self.packet_header['nradials']
            raw_data = np.empty((nradials, nbins), dtype='uint8')
            pos = 30
            for i in range(nradials):
                rh.append(_unpack_from_buf(buf2, pos,
                                           PACKET_TYPE16_RADIAL_HEADER))
                pos += 6
                raw_data[i] = np.fromstring(buf2[pos:pos+nbins], '>u1')
                pos += nbins
            self.radial_headers = rh
            self.raw_data = raw_data
        else:
            assert packet_code == AF1F
            self.packet_header = _unpack_from_buf(buf2, 16,
                                                  PACKET_TYPE_AF1F_HEADER)
            rh = []
            self.foo = []
            nbins = self.packet_header['nbins']
            nradials = self.packet_header['nradials']
            raw_data = np.empty((nradials, nbins), dtype='uint8')
            pos = 30
            for i in range(nradials):
                radial_header = _unpack_from_buf(
                    buf2, pos, PACKET_TYPE_AF1F_RADIAL_HEADER)
                pos += 6
                # decode RLE
                rle_size = radial_header['nbytes'] * 2
                rle = np.fromstring(buf2[pos:pos+rle_size], dtype='>u1')
                colors = np.bitwise_and(rle, 0b00001111)
                runs = np.bitwise_and(rle, 0b11110000) / 16
                raw_data[i] = np.repeat(colors, runs)
                pos += rle_size
                rh.append(radial_header)
            self.radial_headers = rh
            self.raw_data = raw_data

    def get_location(self):
        """ Return the latitude, longitude and height of the radar. """
        latitude = self.prod_descr['latitude'] * 0.001
        longitude = self.prod_descr['longitude'] * 0.001
        height = self.prod_descr['height']
        return latitude, longitude, height

    def get_azimuth(self):
        """ Return an array of starting azimuth angles in degrees. """
        azimuths = [d['angle_start'] for d in self.radial_headers]
        return np.array(azimuths, dtype='float32') * 0.1

    def get_range(self):
        """ Return an array of gate range spacing in meters. """
        nbins = self.packet_header['nbins']
        first_bin = self.packet_header['first_bin']
        range_scale = self.packet_header['range_scale']
        range_resolution = PRODUCT_RANGE_RESOLUTION[self.msg_header['code']]
        range_scale *= range_resolution
        msg_code = self.msg_header['code']
        if msg_code in [134, 135]:
            range_scale *= 1000.
        return np.arange(nbins, dtype='float32') * range_scale + first_bin

    def get_elevation(self):
        """ Return the sweep elevation angle in degrees. """
        w30 = self.prod_descr['halfwords_30']
        elevation = struct.unpack('>h', w30)[0] * 0.1
        return elevation

    def get_volume_start_datetime(self):
        """ Return a datetime of the start of the radar volume. """
        return datetime_from_mdate_mtime(self.prod_descr['vol_scan_date'],
                                         self.prod_descr['vol_scan_time'])

    def get_data(self):
        """ Return an masked array containing the field data. """
        msg_code = self.msg_header['code']
        if msg_code in [32, 94, 99, 182, 186]:
            # scale and mask according to threshold_data
            # this should be valid for products 32, 94, 153, 194, 195
            s = self.prod_descr['threshold_data']
            hw31, hw32, hw33 = np.fromstring(s[:6], '>i2')
            if msg_code in [94, 99, 182, 186]:
                data = (self.raw_data - 2) * (hw32/10.) + hw31/10.
            elif msg_code in [32]:
                data = (self.raw_data) * (hw32/10.) + hw31/10.
            mdata = np.ma.array(data, mask=self.raw_data < 2)
            return mdata
        elif msg_code in _8_OR_16_LEVELS:
            # XXX could use some clean up
            t = np.fromstring(self.prod_descr['threshold_data'], '>B')
            flags = t[::2]
            values = t[1::2]

            sign = np.choose(np.bitwise_and(flags, 0x01), [1, -1])
            bad = (np.bitwise_and(flags, 0x80) == 128)
            scale = 1.
            if (flags[0] & 2**5):
                scale = 1/20.
            if (flags[0] & 2**4):
                scale = 1/10.

            data_levels = values * sign * scale
            data_levels[bad] = -999

            data = np.choose(self.raw_data, data_levels)
            mdata = np.ma.masked_equal(data, -999)
            return mdata
        elif msg_code in [138]:
            data = self.raw_data * 0.01
            mdata = np.ma.array(data)
            return mdata
        elif msg_code in [159, 161, 163, 170, 171, 172, 173, 174, 175]:
            # scale and mask according to threshold_data
            # this should be valid for products 159, 161, 163, 170, ...
            s = self.prod_descr['threshold_data']
            scale, offset = np.fromstring(s[:8], '>f4')
            data = (self.raw_data - offset) / (scale)
            if msg_code in [159, 161, 163]:
                # XXX this should be < 2, but Java masked = 2
                mdata = np.ma.array(data, mask=self.raw_data <= 2)
            if msg_code in [170, 171, 172, 173, 174, 175]:
                data *= 0.01    # units are 0.01 inches
                # XXX this should be < 1, but Java masked = 1
                mdata = np.ma.array(data, mask=self.raw_data <= 1)
            return mdata
        elif msg_code in [165, 177]:
            # Correspond to classification in table on page 3-37
            mdata = np.ma.masked_equal(self.raw_data, 0)
            return mdata
        elif msg_code in [34]:
            # XXX unknown units
            return np.ma.masked_array(self.raw_data.copy())
        elif msg_code in [134]:

            hw31, hw32, hw33, hw34, hw35 = np.fromstring(
                self.prod_descr['threshold_data'][:10], '>i2')
            linear_scale = _int16_to_float16(hw31)
            linear_offset = _int16_to_float16(hw32)
            log_start = hw33
            log_scale = _int16_to_float16(hw34)
            log_offset = _int16_to_float16(hw35)

            # linear scale data
            data = np.zeros(self.raw_data.shape, dtype=np.float32)
            s = self.raw_data < log_start
            data[s] = ((self.raw_data[s] - linear_offset) / (linear_scale))
            # log scale data
            s = self.raw_data >= log_start
            data[s] = np.exp((self.raw_data[s] - log_offset) / (log_scale))
            mdata = np.ma.masked_array(data, mask=self.raw_data < 2)
            return mdata
        else:
            raise NotImplementedError


def _int16_to_float16(v):
    """ Convert a 16 bit interger into a 16 bit float. """
    # NEXRAD Level III float16 format defined on page 3-33.
    s = (v & 0b1000000000000000) / 0b1000000000000000
    e = (v & 0b0111110000000000) / 0b0000010000000000
    f = (v & 0b0000001111111111)
    if e == 0:
        return (-1)**s * 2 * (0 + (f/2**10.))
    else:
        return (-1)**s * 2**(e-16) * (1 + f/2**10.)


def datetime_from_mdate_mtime(mdate, mtime):
    """ Returns a datetime for a given message date and time. """
    epoch = datetime.datetime.utcfromtimestamp(0)
    return epoch + datetime.timedelta(days=mdate - 1, seconds=mtime)


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

    # extract halfwords 27, 28, 30, 47-53.
    s = prod_descr['halfwords_27_28']
    w27, w28 = s[0:2], s[2:4]
    w30 = prod_descr['halfwords_30']
    s = prod_descr['halfwords_47_53']
    w47, w48, w49, w50, w51, w52, w53 = [s[2*i:2*i+2] for i in range(7)]

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
    else:
        return {}

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
    ('operational_mode', INT2),  # 0 = Maintenance, 1 = Clean Air, 2 = Precip
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
    ('halfwords_47_53', '14s'),  # Product dependent parameters 4-10
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


# Radial Data Packet - Packet Code AF1F
# Figure 3-10 (Sheet 1 and 2), page 3-113.
PACKET_TYPE_AF1F_HEADER = (
    ('packet_code', INT2),      # Packet Code, Type 16
    ('first_bin', INT2),        # Location of first range bin.
    ('nbins', INT2),            # Number of range bins.
    ('i_sweep_center', INT2),   # I coordinate of center of sweep.
    ('j_sweep_center', INT2),   # J coordinate of center of sweep.
    ('range_scale', INT2),      # Range Scale factor
    ('nradials', INT2)          # Total number of radials in the product
)

PACKET_TYPE_AF1F_RADIAL_HEADER = (
    ('nbytes', INT2),           # Number of bytes in the radial.
    ('angle_start', INT2),      # Starting angle at which data was collected.
    ('angle_delta', INT2)       # Delta angle from previous radial.
)


AF1F = -20705       # struct.unpack('>h', 'AF1F'.decode('hex'))
SUPPORTED_PACKET_CODES = [16, AF1F]       # elsewhere

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

# TDWR products
    186,     # 1    Base Reflectivity       Radial Image
    187,     # 1    Base Reflectivity       Radial Image
    180,     # 1    Base Reflectivity       Radial Image
    181,     # 1    Base Reflectivity       Radial Image
    182,     # 2    Base Velocity           Radial Image
    183,     # 2    Base Velocity           Radial Image
    185,     # 5    Base Spectrum Width     Radial Image
    137,     # 40   User Select. Lay Com.   Radial Image
]
