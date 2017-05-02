# -*- coding: utf-8 -*-
"""Code for reading and writing the compact generic TSV format.
"""

from collections import OrderedDict

from .base import (
    LIBRARY_TYPES, EXTRACTION_TYPES, std_field, TSVSheetException,
    BaseTSVReader)
from ..naming import name_generator_for_scheme, NAMING_DEFAULT

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Default title
GENERIC_DEFAULT_TITLE = 'Generic Sample Sheet'

#: Default description
GENERIC_DEFAULT_DESCRIPTION = (
    'Sample Sheet constructed from generic compact TSV file')

#: Generic body TSV header
GENERIC_BODY_HEADER = (
    'bioEntity', 'bioSample', 'testSample', 'ngsLibrary', 'extractionType',
    'libraryType', 'folderName')

#: Fixed "extraInfoDefs" field for generic compact TSV
GENERIC_EXTRA_INFO_DEFS = OrderedDict([
    ('bioEntity', OrderedDict([
    ])),
    ('bioSample', OrderedDict([
    ])),
    ('testSample', OrderedDict([
        std_field('extractionType'),
    ])),
    ('ngsLibrary', OrderedDict([
        std_field('seqPlatform'),
        std_field('libraryType'),
        std_field('folderName'),
    ])),
])


class GenericTSVSheetException(TSVSheetException):
    """Raised on problems with loading generic TSV sample sheets"""


class GenericTSVReader(BaseTSVReader):
    """Helper class for reading generic TSV file

    Prefer using ``read_generic_tsv_*()`` for shortcut
    """

    body_header = GENERIC_BODY_HEADER
    extra_info_defs = GENERIC_EXTRA_INFO_DEFS
    default_title = GENERIC_DEFAULT_TITLE
    default_description = GENERIC_DEFAULT_DESCRIPTION
    bio_entity_name_column = 'bioEntity'
    bio_sample_name_column = 'bioSample'
    test_sample_name_column = 'testSample'
    ngs_library_name_column = 'ngsLibrary'

    def check_tsv_line(self, mapping, lineno):
        """Cancer sample sheet--specific valiation"""
        # Check for hyphen in patient or sample name
        for key in ('bioEntity', 'bioSample', 'testSample', 'ngsLibrary'):
            if '-' in mapping[key]:
                raise GenericTSVSheetException(  # pragma: no cover
                    'Hyphen not allowed in {} column'.format(key))
        # Check "extractionType" field
        if mapping['extractionType'] and (
                mapping['extractionType'] not in EXTRACTION_TYPES):
            raise GenericTSVSheetException(
                'Invalid extraction type {}, must be in {{{}}}'.format(
                    mapping['extractionType'], ', '.join(EXTRACTION_TYPES)))
        # Check "libraryType" field
        if mapping['libraryType'] and (
                mapping['libraryType'] not in LIBRARY_TYPES):
            raise GenericTSVSheetException(
                'Invalid library type {}, must be in {{{}}}'.format(
                    mapping['libraryType'], ', '.join(LIBRARY_TYPES)))

    @classmethod
    def _check_consistency(cls, records, key):
        values = list(sorted(set(r[key] for r in records)))
        if len(values) > 1:
            raise ValueError(  # pragma: no cover
                'Inconsistent {} entries in records: {}'.format(key, values))


def read_generic_tsv_sheet(f, fname=None, naming_scheme=NAMING_DEFAULT):
    """Read compact generic TSV format from file-like object ``f``

    :return: models.Sheet
    """
    return GenericTSVReader(f, fname).read_sheet(
        name_generator_for_scheme(naming_scheme))


def read_generic_tsv_json_data(f, fname=None):
    """Read compact generic TSV format from file-like object ``f``

    :return: ``dict``
    """
    return GenericTSVReader(f, fname).read_json_data()
