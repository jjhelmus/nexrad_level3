""" Unit tests checking against files converted with Java netCDF library. """

# Bugs to report upstream
# Masking of high rain rates
# Masked of low digital dual pol moment.

import os.path

import numpy as np
import netCDF4

import nexradl3file

NFILES = [
    # 16 XXX need sample file
    # 17 XXX need sample file
    # 18 XXX need sample file
    # 19 : N0R-N3R
    ('sample_data/KBMX_SDUS54_N0RBMX_201501020205', 'BaseReflectivity'),
    # 20 : N0Z
    ('sample_data/KBMX_SDUS74_N0ZBMX_201501020205', 'BaseReflectivity248'),
    # 21 XXX need sample file
    # 22 XXX need sample file
    # 23 XXX need sample file
    # 24 XXX need sample file
    # 25 : NOW
    ('sample_data/KLOT_SDUS53_NOWLOT_199510151002', 'RadialVelocity'),
    # 26 XXX need sample file
    # 27 : N0V-N3V
    ('sample_data/KBMX_SDUS54_N0VBMX_201501020205', 'RadialVelocity'),
    # 28 : NSP
    ('sample_data/KBMX_SDUS64_NSPBMX_201501020205', 'SpectrumWidth'),
    # 29 : XXX need sample file
    # 30 : NSW
    ('sample_data/KBMX_SDUS64_NSWBMX_201501020205', 'SpectrumWidth'),
    # 31 : XXX need sample file
    # 32 : DHR
    ('sample_data/KBMX_SDUS54_DHRBMX_201501020205', 'DigitalHybridReflectivity'),
    # 33 : XXX need sample file
    # 34 : NC1-5
    # Java gives incorrect gate spacing and does not decode raw data.
    # For now skip
    #('sample_data/KAMA_SDUS64_NC1AMA_201502150549', 'error'),

    # 55 : XXX need sample file
    # 56 : N0S-N3S
    ('sample_data/KBMX_SDUS54_N0SBMX_201501020205', 'StormMeanVelocity'),

    # 78 : N1P
    ('sample_data/KBMX_SDUS34_N1PBMX_201501020205', 'Precip1hr'),
    # 79 : N3P
    ('sample_data/KBMX_SDUS64_N3PBMX_201501020211', 'Precip3hr'),
    # 80 : NTP
    ('sample_data/KBMX_SDUS54_NTPBMX_201501020205', 'PrecipAccum'),

    # 93 : XXX need sample file
    # 94 : N0Q
    ('sample_data/KBMX_SDUS54_N0QBMX_201501020205', 'BaseReflectivityDR'),

    # 99 : N0U
    ('sample_data/KBMX_SDUS54_N0UBMX_201501020205', 'BaseVelocityDV'),

    # 132 : XXX need sample file
    # 133 : XXX need sample file
    # 134 : DVL TODO See note on page 3-33
    ('sample_data/KBMX_SDUS54_DVLBMX_201501020205', 'DigitalIntegLiquid'),
    # 135 : EET TODO See note on page 3-34
    #('sample_data/KBMX_SDUS74_EETBMX_201501020205', 'EnhancedEchoTop'),

    # 138 : DSP - Works, but converted marks a gate (161, 5) as invalid whe
    # the value is in fact valid
    #('sample_data/KBMX_SDUS54_DSPBMX_201501020205', 'DigitalPrecip'),

    # 144 : XXX need sample file
    # 145 : XXX need sample file
    # 146 : XXX need sample file
    # 147 : XXX need sample file

    # 150 : XXX need sample file
    # 151 : XXX need sample file

    # 153 : XXX need sample file
    # 154 : XXX need sample file
    # 155 : XXX need sample file

    # 158 : XXX need sample file
    # 159 : N0X-N3X, NAC, NAB
    ('sample_data/KBMX_SDUS84_N0XBMX_201501020205', 'DifferentialReflectivity'),
    # 161 : XXX need sample file
    ('sample_data/KBMX_SDUS84_N0CBMX_201501020205', 'CorrelationCoefficient'),
    # 162 : XXX need sample file
    # 163 : N0K-N3L, NAK, NBK
    ('sample_data/KBMX_SDUS84_N0KBMX_201501020205', 'DifferentialPhase'),
    # 164 : XXX need sample file
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
    # 173 : DU3 TODO
    #('sample_data/KBMX_SDUS84_DU3BMX_201501020205', 'Accumulation3Hour'),
    # 174 : DOD
    ('sample_data/KBMX_SDUS84_DODBMX_201501020205', 'Digital1HourDifferenceAccumulation'),
    # 175 : DSD
    ('sample_data/KBMX_SDUS84_DSDBMX_201501020205', 'DigitalTotalDifferenceAccumulation'),
    # 177 : HHC TODO
    ('sample_data/KBMX_SDUS84_HHCBMX_201501020205', 'HypridHydrometeorClassification'),

    # 194 : XXX need sample file
    # 195 : XXX need sample file

    # 199 : XXX need sample file

    # 186 : TZL
    ('sample_data/KLOT_SDUS53_TZLORD_201501150003', 'BaseReflectivity'),
    # 187 : XXX need sample file
    # 180 : XXX need sample file
    # 181 : TR0-TR2
    ('sample_data/KLOT_SDUS53_TR0ORD_201501150004', 'BaseReflectivity'),
    # 182 : TV0-TV2
    ('sample_data/KLOT_SDUS53_TV0ORD_201501150004', 'RadialVelocity'),
    # 183 : XXX need sample file
    # 185 : XXX need sample file
    # 137 : XXX need sample file

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

    # elevation
    check_elevation.description = 'check_elevation'
    check_elevation(nfile, dset)

    # azimuth
    check_azimuth.description = 'check_azimuth'
    check_azimuth(nfile, dset)

    # gate
    check_gate.description = 'check_gate'
    check_gate(nfile, dset)

    # latitude, longitude
    check_location.description = 'check_location'
    check_location(nfile, dset)

    # altitude
    # cannot check this variable, looked up from database by Java tool

    # rays_time
    # this is set to product_date + product_time with floating point
    # arithematic errors
    # we do not want to repoduct this.

    # raw field data
    # BaseReflectivityDR_RAW
    check_raw.description = 'check_raw'
    check_raw(nfile, dset, field + '_RAW')

    # raw field data
    # BaseReflectivityDR_RAW
    check_data.description = 'check_data'
    check_data(nfile, dset, field)

    # global attributes
    # time_coverage_start, time_coverage_end
    check_time.description = 'check_time'
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


def check_data(nfile, dset, field):
    var = dset.variables[field][:]
    mvar = np.ma.masked_invalid(var)
    data = nfile.get_data()
    assert np.ma.allclose(mvar, data, atol=0.002)
    assert np.all(np.ma.getmaskarray(mvar) == np.ma.getmaskarray(data))


def check_time(nfile, dset):
    dt = nfile.get_volume_start_datetime()
    assert dt.isoformat() + 'Z' == dset.time_coverage_start

