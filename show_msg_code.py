#! /usr/bin/env python
""" Print out NEXRAD Level 3 message codes in files. """
import sys
import nexrad_level3
import numpy as np


def main():
    """ main function. """
    if len(sys.argv) == 1:
        print "Usage: show_msg_code.py file1 [file2 file3 ...]"
        print "Show the NEXRAD Level 3 message code for one or more files"
        sys.exit()

    all_codes = []
    for f in sys.argv[1:]:
        if f.endswith('.nc'):   # skip .nc files
            continue
        code = nexrad_level3.nexrad_level3_message_code(f)
        print f, code
        all_codes.append(code)

    print "Unique codes seen:"
    print np.unique(all_codes)

if __name__ == "__main__":
    main()
