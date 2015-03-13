Reading NEXRAD Level 3 in Python
================================

This is a repository for building a class for reading radial from NEXRAD Level
3 files for eventual inclusion in Py-ART.

Helpful links
-------------
* http://weather.unisys.com/wxp/Appendices/Formats/NIDS.html
* http://www.roc.noaa.gov/wsr88d/PublicDocs/ICDS/2620001U.pdf
* http://www.roc.noaa.gov/SPG/PublicDocs/SPG_Class1_ICD.pdf
* http://www.roc.noaa.gov/wsr88d/Level_III/Level3Info.aspx
* http://www.nws.noaa.gov/tg/radfiles.php
* ftp://tgftp.nws.noaa.gov/SL.us008001/DF.of/DC.radar/
* http://www.ncdc.noaa.gov/data-access/radar-data
* http://www1.ncdc.noaa.gov/pub/data/radar/RadarProductsDetailedTable.pdf

Samples files
-------------
Sample files ordered from NCDC:

One sample of each product can be found in the sample_data directory.

One full hour of level III data can be found in the full_hour_sample_data 
directory (not checked into repository)

Files were selected from the following locations and dates:

    * 2015-01-02 0200-0300 UTC from KBMX (in kbmx_20150102)
        
        71 unique products
        ------------------

        KBMX_SDUS74_N0ZBMX
        KBMX_SDUS64_NTVBMX
        KBMX_SDUS64_N3PBMX
        KBMX_SDUS54_NCRBMX
        KBMX_SDUS84_N0MBMX
        KBMX_SDUS84_DPRBMX
        KBMX_SDUS84_N0CBMX
        KBMX_SDUS34_N1PBMX
        KBMX_SDUS64_NCZBMX
        KBMX_SDUS24_N1UBMX
        KBMX_SDUS24_N1SBMX
        KBMX_SDUS74_NETBMX
        KBMX_SDUS24_N2UBMX
        KBMX_SDUS84_N0KBMX
        KBMX_SDUS84_N2MBMX
        KBMX_SDUS84_N3CBMX
        KBMX_SDUS64_NMLBMX
        KBMX_SDUS84_DAABMX
        KBMX_SDUS24_N2SBMX
        KBMX_SDUS64_SPDBMX
        KBMX_SDUS84_OHABMX
        KBMX_SDUS34_PTABMX
        KBMX_SDUS54_N0VBMX
        KBMX_SDUS54_DPABMX
        KBMX_SDUS24_N3QBMX
        KBMX_SDUS24_N3UBMX
        KBMX_SDUS84_N3XBMX
        KBMX_SDUS34_NMDBMX
        KBMX_SDUS54_DSPBMX
        KBMX_SDUS84_N1MBMX
        KBMX_SDUS54_N0SBMX
        KBMX_SDUS84_N2CBMX
        KBMX_SDUS84_N1KBMX
        KBMX_SDUS54_DHRBMX
        KBMX_SDUS84_N1XBMX
        KBMX_SDUS24_N1QBMX
        KBMX_SDUS54_DVLBMX
        KBMX_NXUS64_GSMBMX
        KBMX_SDUS64_NHLBMX
        KBMX_SDUS84_N2XBMX
        KBMX_SDUS84_N3KBMX
        KBMX_SDUS84_DU3BMX
        KBMX_SDUS54_N0UBMX
        KBMX_SDUS84_HHCBMX
        KBMX_SDUS44_RCMBMX
        KBMX_SDUS84_N1HBMX
        KBMX_SDUS84_N2KBMX
        KBMX_SDUS64_NSSBMX
        KBMX_SDUS34_N3SBMX
        KBMX_SDUS54_NTPBMX
        KBMX_SDUS84_DSDBMX
        KBMX_SDUS84_N1CBMX
        KBMX_SDUS84_N3HBMX
        KBMX_SDUS84_N3MBMX
        KBMX_SDUS84_DTABMX
        KBMX_SDUS64_NLABMX
        KBMX_SDUS24_N2QBMX
        KBMX_SDUS64_NHIBMX
        KBMX_SDUS84_N0XBMX
        KBMX_SDUS64_NSPBMX
        KBMX_SDUS54_N0QBMX
        KBMX_SDUS84_N0HBMX
        KBMX_SDUS34_NVWBMX
        KBMX_SDUS64_NLLBMX
        KBMX_SDUS74_EETBMX
        KBMX_SDUS84_DODBMX
        KBMX_SDUS84_N2HBMX
        KBMX_SDUS34_NSTBMX
        KBMX_SDUS64_NSWBMX
        KBMX_SDUS54_NVLBMX
        KBMX_SDUS54_N0RBMX

    * 2011-08-28 0700-0800 UTC from KOKX (in kokx_20110828)

        47 unique products
        ------------------
        
        KOKX_SDUS61_NCZOKX
        KOKX_SDUS31_N1POKX
        KOKX_SDUS21_N2SOKX
        KOKX_SDUS61_NTVOKX
        KOKX_SDUS51_NAUOKX
        KOKX_SDUS61_NSSOKX
        KOKX_SDUS51_NVLOKX
        KOKX_SDUS61_NHLOKX
        KOKX_SDUS21_N1UOKX
        KOKX_SDUS51_DPAOKX
        KOKX_SDUS61_NLLOKX
        KOKX_SDUS21_N1SOKX
        KOKX_SDUS31_N3SOKX
        KOKX_SDUS21_NBUOKX
        KOKX_SDUS21_N3QOKX
        KOKX_SDUS61_SPDOKX
        KOKX_SDUS51_NTPOKX
        KOKX_SDUS51_DSPOKX
        KOKX_SDUS61_NLAOKX
        KOKX_SDUS31_NSTOKX
        KOKX_SDUS51_NCROKX
        KOKX_SDUS51_N0VOKX
        KOKX_SDUS21_N2QOKX
        KOKX_SDUS51_N0UOKX
        KOKX_SDUS51_N0SOKX
        KOKX_SDUS51_N0QOKX
        KOKX_SDUS31_NMDOKX
        KOKX_SDUS61_NSPOKX
        KOKX_NXUS61_GSMOKX
        KOKX_SDUS51_N0ROKX
        KOKX_SDUS51_DVLOKX
        KOKX_SDUS51_NAQOKX
        KOKX_SDUS71_NETOKX
        KOKX_SDUS41_RCMOKX
        KOKX_SDUS31_NVWOKX
        KOKX_SDUS61_NMLOKX
        KOKX_SDUS51_DHROKX
        KOKX_SDUS61_NHIOKX
        KOKX_SDUS21_N1QOKX
        KOKX_SDUS61_N3POKX
        KOKX_SDUS71_EETOKX
        KOKX_SDUS21_NBQOKX
        KOKX_SDUS21_N2UOKX
        KOKX_SDUS41_RSLOKX
        KOKX_SDUS21_N3UOKX
        KOKX_SDUS61_NSWOKX
        KOKX_SDUS71_N0ZOKX
