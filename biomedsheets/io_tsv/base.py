# -*- coding: utf-8 -*-
"""Base code for reading compact TSV format
"""

from collections import OrderedDict

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Delimiter to use
DELIM = '\t'

#: Known library types
LIBRARY_TYPES = (
    'WES', 'WGS', 'Panel_seq', 'mRNA_seq', 'total_RNA_seq')

#: Map library type to extraction type
LIBRARY_TO_EXTRACTION = {
    'WES': 'DNA',
    'WGS': 'DNA',
    'Panel_seq': 'DNA',
    'mRNA_seq': 'RNA',
    'total_RNA_seq': 'RNA',
}

#: Known extraction types
EXTRACTION_TYPES = ('DNA', 'RNA')

#: Key for the TSV header, field "title"
KEY_TITLE = 'title'

#: Key for the TSV header, field "description"
KEY_DESCRIPTION = 'description'

#: Constants for interpreting booleans
BOOL_VALUES = {
    'Y': True,
    'y': True,
    'N': False,
    'n': False,
}


class SheetIOException(Exception):
    """Raised on problems with loading sample sheets"""


class TSVSheetException(SheetIOException):
    """Raised on problems with loading the compact TSV sheets"""


def std_field(name):
    """Return data structure for returning JSON pointer data structure"""
    tpl = 'resource://biomedsheets/data/std_fields.json#/extraInfoDefs/template/{}'
    return (name, OrderedDict([('$ref', tpl.format(name))]))
