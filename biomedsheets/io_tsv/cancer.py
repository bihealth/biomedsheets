# -*- coding: utf-8 -*-
"""Code for reading and writing the compact cancer TSV format
"""

from collections import OrderedDict

from .base import (
    LIBRARY_TYPES, BOOL_VALUES, NCBI_TAXON_HUMAN, std_field,
    TSVSheetException, BaseTSVReader)
from ..naming import name_generator_for_scheme, NAMING_DEFAULT

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Default title
CANCER_DEFAULT_TITLE = 'Cancer Sample Sheet'

#: Default description
CANCER_DEFAULT_DESCRIPTION = (
    'Sample Sheet constructed from cancer matched samples '
    'compact TSV file')

#: Cancer body TSV header
CANCER_BODY_HEADER = (
    'patientName', 'sampleName', 'isTumor', 'libraryType', 'folderName')

#: Fixed "extraInfoDefs" field for cancer compact TSV
CANCER_EXTRA_INFO_DEFS = OrderedDict([
    ('bioEntity', OrderedDict([
        std_field('ncbiTaxon'),
    ])),
    ('bioSample', OrderedDict([
        std_field('isTumor'),
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


class CancerTSVSheetException(TSVSheetException):
    """Raised on problems with loading cancer TSV sample sheets"""


class CancerTSVReader(BaseTSVReader):
    """Helper class for reading cancer TSV file

    Prefer using ``read_cancer_tsv_*()`` for shortcut
    """

    body_header = CANCER_BODY_HEADER
    extra_info_defs = CANCER_EXTRA_INFO_DEFS
    default_title = CANCER_DEFAULT_TITLE
    default_description = CANCER_DEFAULT_DESCRIPTION
    bio_entity_name_column = 'patientName'
    bio_sample_name_column = 'sampleName'

    def check_tsv_line(self, mapping, lineno):
        """Cancer sample sheet--specific valiation"""
        # Check for hyphen in patient or sample name
        if '-' in mapping['patientName']:
            raise CancerTSVSheetException(
                'Hyphen not allowed in patientName column')  # pragma: no cover
        if '-' in mapping['sampleName']:
            raise CancerTSVSheetException(
                'Hyphen not allowed in sampleName column')  # pragma: no cover
        # Check "isTumor" field, convert to bool
        if mapping['isTumor'] not in BOOL_VALUES.keys():
            raise CancerTSVSheetException(  # pragma: no cover
                ('Invalid boolean value {} in line {} '
                 'of data section of {}').format(
                     mapping['isTumor'], lineno + 2, self.fname))
        mapping['isTumor'] = BOOL_VALUES[mapping['isTumor']]
        # Check "libraryType" field
        if mapping['libraryType'] not in LIBRARY_TYPES:
            raise CancerTSVSheetException(  # pragma: no cover
                'Invalid library type {}, must be in {{{}}}'.format(
                    mapping['libraryType'], ', '.join(LIBRARY_TYPES)))
        # Check other fields for being non-empty
        for key in self.__class__.body_header:
            if mapping[key] is None:
                raise CancerTSVSheetException(
                    'Field {} empty in line {} of {}'.format(
                        key, lineno + 2, self.fname))  # pragma: no cover
        # TODO: we should perform more validation here in the future

    def construct_bio_entity_dict(self, records, extra_info_defs):
        result = super().construct_bio_entity_dict(records, extra_info_defs)
        result['extraInfo']['ncbiTaxon'] = NCBI_TAXON_HUMAN
        return result

    def check_bio_sample_records(self, records, extra_info_defs):
        if len(set(r['isTumor'] for r in records)) != 1:
            raise TSVSheetException(
                'Inconsistent "isTumor" flag for records')  # pragma: no cover

    def construct_bio_sample_dict(self, records, extra_info_defs):
        result = super().construct_bio_sample_dict(records, extra_info_defs)
        result['extraInfo']['isTumor'] = records[0]['isTumor']
        return result


def read_cancer_tsv_sheet(f, fname=None, naming_scheme=NAMING_DEFAULT):
    """Read compact cancer TSV format from file-like object ``f``

    :return: models.Sheet
    """
    return CancerTSVReader(f, fname).read_sheet(
        name_generator_for_scheme(naming_scheme))


def read_cancer_tsv_json_data(f, fname=None):
    """Read compact cancer TSV format from file-like object ``f``

    :return: ``dict``
    """
    return CancerTSVReader(f, fname).read_json_data()
