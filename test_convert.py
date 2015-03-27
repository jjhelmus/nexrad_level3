""" Unit tests checking against files converted with Java netCDF library. """

# DIFFERENCE marks differences between data from files converted with
# the netCDF Java library from Unidata and the data from the Python
# nexradl3file module.  These do not appear to be bugs in the Java library.
# BUG marks difference cause by bugs in the netCDF Java library.

import os.path

import numpy as np
import netCDF4

import nexradl3file

NFILES = [
    # 19 : N0R-N3R
    ('sample_data/KBMX_SDUS54_N0RBMX_201501020205', 'BaseReflectivity'),
    # 20 : N0Z
    ('sample_data/KBMX_SDUS74_N0ZBMX_201501020205', 'BaseReflectivity248'),
    # 25 : NOW
    ('sample_data/KLOT_SDUS53_NOWLOT_199510151002', 'RadialVelocity'),
    # 27 : N0V-N3V
    ('sample_data/KBMX_SDUS54_N0VBMX_201501020205', 'RadialVelocity'),
    # 28 : NSP
    ('sample_data/KBMX_SDUS64_NSPBMX_201501020205', 'SpectrumWidth'),
    # 30 : NSW
    ('sample_data/KBMX_SDUS64_NSWBMX_201501020205', 'SpectrumWidth'),
    # 32 : DHR
    ('sample_data/KBMX_SDUS54_DHRBMX_201501020205', 'DigitalHybridReflectivity'),
    # 34 : NC1-5
    ('sample_data/KAMA_SDUS64_NC1AMA_201502150549', 'error'),
    # 56 : N0S-N3S
    ('sample_data/KBMX_SDUS54_N0SBMX_201501020205', 'StormMeanVelocity'),
    # 78 : N1P
    ('sample_data/KBMX_SDUS34_N1PBMX_201501020205', 'Precip1hr'),
    # 79 : N3P
    ('sample_data/KBMX_SDUS64_N3PBMX_201501020211', 'Precip3hr'),
    # 80 : NTP
    ('sample_data/KBMX_SDUS54_NTPBMX_201501020205', 'PrecipAccum'),
    # 94 : N0Q
    ('sample_data/KBMX_SDUS54_N0QBMX_201501020205', 'BaseReflectivityDR'),
    # 99 : N0U
    ('sample_data/KBMX_SDUS54_N0UBMX_201501020205', 'BaseVelocityDV'),
    # 134 : DVL
    ('sample_data/KBMX_SDUS54_DVLBMX_201501020205', 'DigitalIntegLiquid'),
    # 135 : EET
    ('sample_data/KBMX_SDUS74_EETBMX_201501020205', 'EnhancedEchoTop'),
    # 138 : DSP
    ('sample_data/KBMX_SDUS54_DSPBMX_201501020205', 'DigitalPrecip'),
    # 159 : N0X-N3X, NAX, NBX
    ('sample_data/KBMX_SDUS84_N0XBMX_201501020205', 'DifferentialReflectivity'),
    # 161 : N0C-N3C, NAC, NBC
    ('sample_data/KBMX_SDUS84_N0CBMX_201501020205', 'CorrelationCoefficient'),
    # 163 : N0K-N3L, NAK, NBK
    ('sample_data/KBMX_SDUS84_N0KBMX_201501020205', 'DifferentialPhase'),
    # 165 : N0H-N3H, NAH, NBH
    ('sample_data/KBMX_SDUS84_N0HBMX_201501020205', 'HydrometeorClassification'),
    # 169 : OHA
    ('sample_data/KBMX_SDUS84_OHABMX_201501020205', 'OneHourAccumulation'),
    # 170 : DAA
    ('sample_data/KBMX_SDUS84_DAABMX_201501020205', 'DigitalAccumulationArray'),
    # 171 : PTA
    ('sample_data/KBMX_SDUS34_PTABMX_201501020205', 'StormTotalAccumulation'),
    # 172 : DTA
    ('sample_data/KBMX_SDUS84_DTABMX_201501020205', 'DigitalStormTotalAccumulation'),
    # 173 : DU3
    ('sample_data/KBMX_SDUS84_DU3BMX_201501020205', 'Accumulation3Hour'),
    # 174 : DOD
    ('sample_data/KBMX_SDUS84_DODBMX_201501020205', 'Digital1HourDifferenceAccumulation'),
    # 175 : DSD
    ('sample_data/KBMX_SDUS84_DSDBMX_201501020205', 'DigitalTotalDifferenceAccumulation'),
    # 177 : HHC
    ('sample_data/KBMX_SDUS84_HHCBMX_201501020205', 'HypridHydrometeorClassification'),
    # 186 : TZL
    ('sample_data/KLOT_SDUS53_TZLORD_201501150003', 'BaseReflectivity'),
    # 181 : TR0-TR2
    ('sample_data/KLOT_SDUS53_TR0ORD_201501150004', 'BaseReflectivity'),
    # 182 : TV0-TV2
    ('sample_data/KLOT_SDUS53_TV0ORD_201501150004', 'RadialVelocity'),

    # Unsorted
    #('sample_data/KBMX_NXUS64_GSMBMX_201501020258', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N1QBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N1SBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N1UBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N2QBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N2SBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N2UBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N3QBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N3UBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_N3SBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_NMDBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_NSTBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_NVWBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS44_RCMBMX_201501020217', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_DPABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_NCRBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_NVLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NCZBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NHIBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NHLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NLABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NLLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NMLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NSSBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NTVBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_SPDBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS74_NETBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DPRBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N0MBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N1CBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N1HBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N1KBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N1MBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N1XBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N2CBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N2HBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N2KBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N2MBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N2XBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N3CBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N3HBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N3KBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N3MBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N3XBMX_201501020205', 'BaseReflectivity'),

    #('sample_data/KOKX_NXUS61_GSMOKX_201108280700', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N1QOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N1SOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N1UOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N2QOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N2SOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N2UOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N3QOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_N3UOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_NBQOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS21_NBUOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS31_N1POKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS31_N3SOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS31_NMDOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS31_NSTOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS31_NVWOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS41_RCMOKX_201108280716', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS41_RSLOKX_201108280758', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_DHROKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_DPAOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_DSPOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_DVLOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_N0QOKX_201108280702', 'BaseReflectivityDR'),
    #('sample_data/KOKX_SDUS51_N0ROKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_N0SOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_N0UOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_N0VOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_NAQOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_NAUOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_NCROKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_NTPOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS51_NVLOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_N3POKX_201108280711', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NCZOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NHIOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NHLOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NLAOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NLLOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NMLOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NSPOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NSSOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NSWOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_NTVOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS61_SPDOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS71_EETOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS71_N0ZOKX_201108280702', 'BaseReflectivity'),
    #('sample_data/KOKX_SDUS71_NETOKX_201108280702', 'BaseReflectivity'),


    #('sample_data/KLOT_SDUS23_TR1ORD_201501150004', 'BaseReflectivity'),
    #('sample_data/KLOT_SDUS23_TR2ORD_201501150004', 'BaseReflectivity'),
    #('sample_data/KLOT_SDUS73_TV1ORD_201501150004', 'BaseReflectivity'),
    #('sample_data/KLOT_SDUS73_TV2ORD_201501150004', 'BaseReflectivity'),

    #('sample_data/KAMA_SDUS64_NC1AMA_201502150549', 'error'),
    #('sample_data/KAMA_SDUS64_NC2AMA_201502150549', 'error'),
    #('sample_data/KAMA_SDUS64_NC3AMA_201502150549', 'error'),
    #('sample_data/KAMA_SDUS64_NC4AMA_201502150549', 'error'),
    #('sample_data/KAMA_SDUS64_NC5AMA_201502150549', 'error'),

]


def test_files():
    for n3file, field in NFILES:
        head, tail = os.path.split(n3file)
        check_pair.description = 'Checking ' + tail
        yield check_pair, n3file, field


def check_pair(n3file, field):
    ncfile = n3file + '.nc'
    dset = netCDF4.Dataset(ncfile)
    nfile = nexradl3file.NexradLevel3File(n3file)
    msg_code = nfile.msg_header['code']

    # elevation
    check_elevation(nfile, dset)

    # azimuth
    check_azimuth(nfile, dset)

    # gate
    if field.startswith('error'):
        pass
        # DIFFERENT: Java converter sets message code 34 range to all zeros
    else:
        check_gate(nfile, dset)

    # latitude, longitude
    check_location(nfile, dset)

    # altitude
    # cannot check this variable, looked up from database by Java tool

    # rays_time
    # this is set to product_date + product_time with floating point
    # arithematic errors
    # we do not want to repoduct this.

    # raw field data
    check_raw(nfile, dset, field + '_RAW')

    # raw field data
    if field.startswith('error'):
        # DIFFERENCE: Java library does not decode the message code 34 data
        pass
    else:
        data = nfile.get_data()
        if msg_code == 138:
            # BUG: Java library treats raw data as signed 8-bit integer and
            # masks out points corrsponding to negative values. The raw data
            # should be treated as a unsigned 8-bit integer.
            # Msg 138, see page 3-37.
            data[nfile.raw_data.view('int8') < 0] = np.ma.masked
        elif msg_code in [159, 161, 163]:
            # BUG : Java library masks the lowest valid value for polarization
            # variable by interpreting a raw value equal to 2 as a mask rather
            # than a valid value.
            # Msg 159, 161, 163, see table on page 3-36.
            data[nfile.raw_data == 2] = np.ma.masked
        elif msg_code in [170, 172, 173, 174, 175]:
            # BUG : Java library masks the lowest valid value for precipitation
            # accumulation varaible # by interpreting a raw value equal to 1
            # as a mask rather than a valid value.
            # Msg 170, 172, 173, 174, 175, see table on page 3-36.
            data.mask[nfile.raw_data == 1] = True
        rtol=1e-5
        atol=1e-8
        # DIFFERENCE : Precipitation acculations are slightly difference
        # when converted with Python vs. the Java library.  This is likely due
        # to floating point round off errors although them seem larger than
        # expected.
        if msg_code in [170, 174, 175]:
            atol=0.002
        elif msg_code in [173]:
            atol=0.002
            rtol=0.008
        check_data(data, dset, field, atol=atol, rtol=rtol)
        #check_data(data, dset, field, atol=0.002, rtol=0.008)

    # global attributes
    # time_coverage_start, time_coverage_end
    check_time(nfile, dset)


def check_elevation(nfile, dset):
    var = dset.variables['elevation'][:]
    assert np.all(var == var[0])
    assert abs(nfile.get_elevation() - var[0]) < 0.1


def check_azimuth(nfile, dset):
    assert np.allclose(dset.variables['azimuth'][:], nfile.get_azimuth())


def check_gate(nfile, dset):
    assert np.allclose(dset.variables['gate'][:], nfile.get_range())


def check_location(nfile, dset):
    latitude, longitude, height = nfile.get_location()

    var = dset.variables['latitude'][:]
    assert np.all(var == var[0])
    assert abs(latitude - var[0]) < 0.001

    var = dset.variables['longitude'][:]
    assert np.all(var == var[0])
    assert abs(longitude - var[0]) < 0.001


def check_raw(nfile, dset, field):
    var = dset.variables[field][:]
    np.allclose(nfile.raw_data, var.astype('u1'))


def check_data(data, dset, field, atol, rtol):
    var = dset.variables[field][:]
    mvar = np.ma.masked_invalid(var)
    assert np.ma.allclose(mvar, data, atol=atol, rtol=rtol)
    assert np.all(np.ma.getmaskarray(mvar) == np.ma.getmaskarray(data))


def check_time(nfile, dset):
    dt = nfile.get_volume_start_datetime()
    assert dt.isoformat() + 'Z' == dset.time_coverage_start

