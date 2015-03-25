""" Unit tests checking against files converted with Java netCDF library. """

import os.path

import numpy as np
import netCDF4

import nexradl3file

NFILES = [
    #('current_files/KBMX_SDUS54_N0QBMX_201501020205', 'BaseReflectivityDR'),
    #('current_files/KBMX_SDUS54_N0RBMX_201501020205', 'BaseReflectivity'),

    #('sample_data/KBMX_NXUS64_GSMBMX_201501020258', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N1QBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N1SBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N1UBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N2QBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N2SBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N2UBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N3QBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS24_N3UBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_N1PBMX_201501020205', 'Precip1hr'),
    #('sample_data/KBMX_SDUS34_N3SBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_NMDBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_NSTBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_NVWBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS34_PTABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS44_RCMBMX_201501020217', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_DHRBMX_201501020205',
    # 'DigitalHybridReflectivity'),
    #('sample_data/KBMX_SDUS54_DPABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_DSPBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_DVLBMX_201501020205', 'BaseReflectivity'),
    ('sample_data/KBMX_SDUS54_N0QBMX_201501020205', 'BaseReflectivityDR'),
    ('sample_data/KBMX_SDUS54_N0RBMX_201501020205', 'BaseReflectivity'),
    ('sample_data/KBMX_SDUS54_N0SBMX_201501020205', 'StormMeanVelocity'),
    ('sample_data/KBMX_SDUS54_N0UBMX_201501020205', 'BaseVelocityDV'),
    ('sample_data/KBMX_SDUS54_N0VBMX_201501020205', 'RadialVelocity'),
    #('sample_data/KBMX_SDUS54_NCRBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_NTPBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS54_NVLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_N3PBMX_201501020211', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NCZBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NHIBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NHLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NLABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NLLBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_NMLBMX_201501020205', 'BaseReflectivity'),
    ('sample_data/KBMX_SDUS64_NSPBMX_201501020205', 'SpectrumWidth'),
    #('sample_data/KBMX_SDUS64_NSSBMX_201501020205', 'BaseReflectivity'),
    ('sample_data/KBMX_SDUS64_NSWBMX_201501020205', 'SpectrumWidth'),
    #('sample_data/KBMX_SDUS64_NTVBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS64_SPDBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS74_EETBMX_201501020205', 'BaseReflectivity'),
    ('sample_data/KBMX_SDUS74_N0ZBMX_201501020205', 'BaseReflectivity248'),
    #('sample_data/KBMX_SDUS74_NETBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DAABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DODBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DPRBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DSDBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DTABMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_DU3BMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_HHCBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N0CBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N0HBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N0KBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N0MBMX_201501020205', 'BaseReflectivity'),
    #('sample_data/KBMX_SDUS84_N0XBMX_201501020205', 'DifferentialReflectivity'),
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
    #('sample_data/KBMX_SDUS84_OHABMX_201501020205', 'BaseReflectivity'),

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
    assert np.ma.allequal(mvar, data)
    assert np.all(mvar.mask == data.mask)


def check_time(nfile, dset):
    dt = nfile.get_volume_start_datetime()
    assert dt.isoformat() + 'Z' == dset.time_coverage_start
    assert dt.isoformat() + 'Z' == dset.time_coverage_end

