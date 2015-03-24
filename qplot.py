#! /usr/bin/env python
""" Python NEXRAD Level 3 files. """
import matplotlib.pyplot as plt
import nexradl3file

SAMPLE_FILE = 'sample_data/KBMX_SDUS54_N0QBMX_201501020205'
nfile = nexradl3file.NexradLevel3File(SAMPLE_FILE)
plt.imshow(nfile.get_data())
plt.show()
