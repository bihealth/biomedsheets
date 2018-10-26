# -*- coding: utf-8 -*-
"""Code for reading and writing the compact germline TSV format
"""

from collections import OrderedDict

from .base import (
    LIBRARY_TYPES, NCBI_TAXON_HUMAN, std_field, TSVSheetException,
    BaseTSVReader)
from ..naming import name_generator_for_scheme, NAMING_DEFAULT

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Default title
GERMLINE_DEFAULT_TITLE = 'Germline Sample Sheet'

#: Default description
GERMLINE_DEFAULT_DESCRIPTION = (
    'Sample Sheet constructed from germline compact TSV file')

#: Germline body TSV header
GERMLINE_BODY_HEADER = ('patientName', 'fatherName', 'motherName', 'sex',
                        'isAffected', 'folderName', 'hpoTerms', 'libraryType')

#: Fixed "extraInfoDefs" field for germline compact TSV
GERMLINE_EXTRA_INFO_DEFS = OrderedDict([
    ('bioEntity', OrderedDict([
        std_field('ncbiTaxon'),
        std_field('fatherPk'),
        std_field('motherPk'),
        ('fatherName', OrderedDict([
            ('docs', 'secondary_id of father, used for construction only'),
            ('key', 'fatherName'),
            ('type', 'string'),
        ])),
        ('motherName', OrderedDict([
            ('key', 'motherName'),
            ('docs', 'secondary_id of mother, used for construction only'),
            ('type', 'string'),
        ])),
        std_field('sex'),
        std_field('isAffected'),
        std_field('hpoTerms'),
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

#: Constants for interpreting "sex" field
SEX_VALUES = {
    'M': 'male',
    'm': 'male',
    'f': 'female',
    'F': 'female',
    'U': 'unknown',
    'u': 'unknown',
    '0': 'unknown',
    '1': 'male',
    '2': 'female',
    None: 'unknown,'
}

#: Constants for interpreting "sex" field
AFFECTED_VALUES = {
    'Y': 'affected',
    'y': 'affected',
    'N': 'unaffected',
    'n': 'unaffected',
    'U': 'unknown',
    'u': 'unknown',
    '0': 'unknown',
    '1': 'unaffected',
    '2': 'affected',
    None: 'unknown,'
}


class GermlineTSVSheetException(TSVSheetException):
    """Raised on problems with loading germline TSV sample sheets"""


class GermlineTSVReader(BaseTSVReader):
    """Helper class for reading germline TSV file

    Prefer using ``read_germline_tsv_*()`` for shortcut
    """

    body_header = GERMLINE_BODY_HEADER
    extra_info_defs = GERMLINE_EXTRA_INFO_DEFS
    default_title = GERMLINE_DEFAULT_TITLE
    default_description = GERMLINE_DEFAULT_DESCRIPTION
    bio_entity_name_column = 'patientName'
    bio_sample_name_column = 'bioSample'
    test_sample_name_column = 'testSample'
    bio_sample_name = 'N1'
    optional_body_header_columns = ('seqPlatform', 'bioSample', 'testSample')

    def check_tsv_line(self, mapping, lineno):
        """Cancer sample sheet--specific valiation"""
        # Check for hyphen in patient or sample name
        if '-' in mapping['patientName']:
            raise GermlineTSVSheetException(
                'Hyphen not allowed in patientName column')  # pragma: no cover
        if mapping['fatherName'] and '-' in mapping['fatherName']:
            raise GermlineTSVSheetException(
                'Hyphen not allowed in fatherName column')  # pragma: no cover
        if mapping['motherName'] and '-' in mapping['motherName']:
            raise GermlineTSVSheetException(
                'Hyphen not allowed in motherName column')  # pragma: no cover
        # Check "libraryType" field
        if mapping['libraryType'] and (
                mapping['libraryType'] not in LIBRARY_TYPES):
            raise GermlineTSVSheetException(
                'Invalid library type {}, must be in {{{}}}'.format(
                    mapping['libraryType'], ', '.join(LIBRARY_TYPES)))
        # Check "sex" field
        if mapping['sex'] not in SEX_VALUES.keys():
            raise GermlineTSVSheetException(  # pragma: no cover
                ('Invalid "sex" value {} in line {} of data section of '
                 '{}').format(mapping['sex'], lineno + 2, self.fname))
        mapping['sex'] = SEX_VALUES[mapping['sex']]
        # Check "affected"
        if mapping['isAffected'] not in AFFECTED_VALUES.keys():
            raise GermlineTSVSheetException(  # pragma: no cover
                ('Invalid "isAffected" value {} in line {} of data section of '
                 '{}').format(mapping['isAffected'], lineno + 2, self.fname))
        mapping['isAffected'] = AFFECTED_VALUES[mapping['isAffected']]

    def postprocess_json_data(self, json_data):
        """Postprocess JSON data"""
        # Build mapping from bio entity name to pk
        bio_entity_name_to_pk = {
            name: bio_entity['pk']
            for name, bio_entity in json_data['bioEntities'].items()
        }
        # Update bio entities motherPk and fatherPk attributes
        for bio_entity in json_data['bioEntities'].values():
            extra_info = bio_entity['extraInfo']
            if extra_info.get('fatherName', '0') != '0':
                extra_info['fatherPk'] = bio_entity_name_to_pk[
                    extra_info['fatherName']]
            if extra_info.get('motherName', '0') != '0':
                extra_info['motherPk'] = bio_entity_name_to_pk[
                    extra_info['motherName']]
        return json_data

    def construct_bio_entity_dict(self, records, extra_info_defs):
        result = super().construct_bio_entity_dict(records, extra_info_defs)
        result['extraInfo']['ncbiTaxon'] = NCBI_TAXON_HUMAN
        # Check fatherName and motherName entries and assign to result
        self._check_consistency(records, 'fatherName')
        record = records[0]  # representative as it's consistent
        if record.get('fatherName') and record['fatherName'] != '0':
            result['extraInfo']['fatherName'] = record['fatherName']
        if record.get('motherName') and record['motherName'] != '0':
            result['extraInfo']['motherName'] = record['motherName']
        # Check sex and isAffected entries and assign to result
        result['extraInfo']['sex'] = record['sex']
        result['extraInfo']['isAffected'] = record['isAffected']
        # Check hpoTerms entries and assign to result
        if record['hpoTerms']:
            result['extraInfo']['hpoTerms'] = record['hpoTerms'].split(',')
        return result

    @classmethod
    def _check_consistency(cls, records, key):
        values = list(sorted(set(r[key] for r in records)))
        if len(values) > 1:
            raise ValueError(  # pragma: no cover
                'Inconsistent {} entries in records: {}'.format(key, values))


def read_germline_tsv_sheet(f, fname=None, naming_scheme=NAMING_DEFAULT):
    """Read compact germline TSV format from file-like object ``f``

    :return: models.Sheet
    """
    return GermlineTSVReader(f, fname).read_sheet(
        name_generator_for_scheme(naming_scheme))


def read_germline_tsv_json_data(f, fname=None):
    """Read compact germline TSV format from file-like object ``f``

    :return: ``dict``
    """
    return GermlineTSVReader(f, fname).read_json_data()
