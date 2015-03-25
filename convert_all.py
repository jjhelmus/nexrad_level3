#! /usr/bin/env python

import glob
import subprocess


def convert_file(infile, outfile):

    cmd = ("java -Xmx1g -classpath netcdfAll-4.5.jar " +
           "ucar.nc2.dataset.NetcdfDataset -in %s -out %s")
    return subprocess.call(cmd % (infile, outfile), shell=True)


if __name__ == "__main__":

    #convert_file('sample_data/KBMX_SDUS54_N0QBMX_201501020205', 'foo.nc')
    for infile in glob.glob('sample_data/*'):
        outfile = infile + '.nc'
        convert_file(infile, outfile)
