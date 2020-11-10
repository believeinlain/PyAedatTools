# -*- coding: utf-8 -*-

"""
ImportAedat

Code contributions from Bodo Rueckhauser
"""

from PyAedatTools import ImportAedatHeaders
from PyAedatTools import ImportAedatDataVersion1or2
from PyAedatTools import ImportAedatDataVersion3

def ImportAedat(aedat):
    """
    Parameters
    ----------
    args :

    Returns
    -------
    """

# To handle: missing args; search for file to open - request to user

    with open(aedat['importParams']['filePath'], 'rb') as aedat['importParams']['fileHandle']:
        aedat = ImportAedatHeaders.ImportAedatHeaders(aedat)
        print("Importing aedat version ", aedat['info']['fileFormat'])
        if aedat['info']['fileFormat'] < 3:
            return ImportAedatDataVersion1or2.ImportAedatDataVersion1or2(aedat)
        else:
            return ImportAedatDataVersion3.ImportAedatDataVersion3(aedat)
