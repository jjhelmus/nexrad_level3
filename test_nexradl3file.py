
import numpy as np
import netCDF4

import nexrad_level3

def test_message_19_file():
    n3file = 'current_files/KBMX_SDUS54_N0RBMX_201501020205'
    ncfile = 'current_files/KBMX_SDUS54_N0RBMX_201501020205.nc'
    dset = netCDF4.Dataset(ncfile)
    nfile = nexrad_level3.NexradLevel3File(n3file)

    # elevation
    check_elevation.description = 'check_elevation'
    yield check_elevation, nfile, dset

    # azimuth
    check_azimuth.description = 'check_azimuth'
    yield check_azimuth, nfile, dset

    # gate
    check_gate.description = 'check_gate'
    yield check_gate, nfile, dset

    # latitude, longitude
    check_location.description = 'check_location'
    yield check_location, nfile, dset

    # altitude
    # cannot check this variable, looked up from database by Java tool

    # rays_time
    # this is set to product_date + product_time with floating point
    # arithematic errors
    # we do not want to repoduct this.

    # raw field data
    # BaseReflectivityDR_RAW
    check_raw.description = 'check_raw'
    yield check_raw, nfile, dset, 'BaseReflectivity_RAW'

    # raw field data
    # BaseReflectivityDR_RAW
    check_data.description = 'check_data'
    yield check_data, nfile, dset, 'BaseReflectivity'

    # global attributes
    # time_coverage_start, time_coverage_end
    check_time.description = 'check_time'
    yield check_time, nfile, dset

    dset.close()


def test_message_94_file():
    n3file = 'current_files/KBMX_SDUS54_N0QBMX_201501020205'
    ncfile = 'current_files/KBMX_SDUS54_N0QBMX_201501020205.nc'
    dset = netCDF4.Dataset(ncfile)
    nfile = nexrad_level3.NexradLevel3File(n3file)

    # elevation
    check_elevation.description = 'check_elevation'
    yield check_elevation, nfile, dset

    # azimuth
    check_azimuth.description = 'check_azimuth'
    yield check_azimuth, nfile, dset

    # gate
    check_gate.description = 'check_gate'
    yield check_gate, nfile, dset

    # latitude, longitude
    check_location.description = 'check_location'
    yield check_location, nfile, dset

    # altitude
    # cannot check this variable, looked up from database by Java tool

    # rays_time
    # this is set to product_date + product_time with floating point
    # arithematic errors
    # we do not want to repoduct this.

    # raw field data
    # BaseReflectivityDR_RAW
    check_raw.description = 'check_raw'
    yield check_raw, nfile, dset, 'BaseReflectivityDR_RAW'


    # raw field data
    # BaseReflectivityDR_RAW
    check_data.description = 'check_data'
    yield check_data, nfile, dset, 'BaseReflectivityDR'

    # global attributes
    # time_coverage_start, time_coverage_end
    check_time.description = 'check_time'
    yield check_time, nfile, dset

    dset.close()

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

