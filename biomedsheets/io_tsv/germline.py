# -*- coding: utf-8 -*-
"""Code for reading and writing the compact germline TSV format
"""

from collections import OrderedDict

from .base import (
    LIBRARY_TYPES, LIBRARY_TO_EXTRACTION, EXTRACTION_TYPES, KEY_TITLE, KEY_DESCRIPTION,
    BOOL_VALUES, DELIM, NCBI_TAXON_HUMAN,
    std_field, TSVSheetException, BaseTSVReader)

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Default title
GERMLINE_DEFAULT_TITLE = 'Germline Sample Sheet'

#: Default description
GERMLINE_DEFAULT_DESCRIPTION = 'Sample Sheet constructed from germline compact TSV file'

#: Germline TSV header
GERMLINE_TSV_HEADER = ('patientName', 'fatherName', 'motherName', 'sex',
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
    None: 'unknown,'
}


class GermlineTSVSheetException(TSVSheetException):
    """Raised on problems with loading germline TSV sample sheets"""


class GermlineTSVReader(BaseTSVReader):
    """Helper class for reading germline TSV file

    Prefer using ``read_germline_tsv_*()`` for shortcut
    """

    tsv_header = GERMLINE_TSV_HEADER
    extra_info_defs = GERMLINE_EXTRA_INFO_DEFS
    default_title = GERMLINE_DEFAULT_TITLE
    default_description = GERMLINE_DEFAULT_DESCRIPTION
    bio_entity_name_column = 'patientName'
    bio_sample_name = 'DNA1'

    def check_tsv_line(self, mapping, lineno):
        """Cancer sample sheet--specific valiation"""
        # Check "libraryType" field
        if mapping['libraryType'] and mapping['libraryType'] not in LIBRARY_TYPES:
            raise GermlineTSVSheetException('Invalid library type {}, must be in {{{}}}'.format(
                mapping['libraryType'], ', '.join(LIBRARY_TYPES)))
        # Check "sex" field
        if mapping['sex'] not in SEX_VALUES.keys():
            raise GermlineTSVSheetException(
                'Invalid "sex" value {} in line {} of data section of {}'.format(
                    mapping['sex'], lineno + 2, self.fname))
        mapping['sex'] = SEX_VALUES[mapping['sex']]
        # Check "affected"
        if mapping['isAffected'] not in AFFECTED_VALUES.keys():
            raise GermlineTSVSheetException(
                'Invalid "isAffected" value {} in line {} of data section of {}'.format(
                    mapping['isAffected'], lineno + 2, self.fname))
        mapping['isAffected'] = AFFECTED_VALUES[mapping['isAffected']]

    def postprocess_json_data(self, json_data):
        """Postprocess JSON data"""
        # Build mapping from bio entity name to pk
        bio_entity_name_to_pk = {
            name: bio_entity['pk'] for name, bio_entity in json_data['bioEntities'].items()}
        # Update bio entities motherPk and fatherPk attributes
        for bio_entity in json_data['bioEntities'].values():
            if bio_entity['extraInfo'].get('fatherName'):
                bio_entity['extraInfo']['fatherPk'] = bio_entity_name_to_pk[
                    bio_entity['extraInfo']['fatherName']]
            if bio_entity['extraInfo'].get('motherName'):
                bio_entity['extraInfo']['motherPk'] = bio_entity_name_to_pk[
                    bio_entity['extraInfo']['motherName']]

    def construct_bio_entity_dict(self, records):
        result = super().construct_bio_entity_dict(records)
        result['extraInfo']['ncbiTaxon'] = NCBI_TAXON_HUMAN
        # Check fatherName and motherName entries and assign to result
        self._check_consistency(records, 'fatherName')
        if records[0]['fatherName']:
            result['extraInfo']['fatherName'] = records[0]['fatherName']
        if records[0]['motherName']:
            result['extraInfo']['motherName'] = records[0]['motherName']
        # Check sex and isAffected entries and assign to result
        result['extraInfo']['sex'] = records[0]['sex']
        result['extraInfo']['isAffected'] = records[0]['isAffected']
        # Check hpoTerms entries and assign to result
        if records[0]['hpoTerms']:
            result['extraInfo']['hpoTerms'] = records[0]['hpoTerms'].split(',')
        return result

    @classmethod
    def _check_consistency(cls, records, key):
        values = list(sorted(set(r[key] for r in records)))
        if len(values) > 1:
            raise ValueError('Inconsistent {} entries in records: {}'.format(key, values))


def read_germline_tsv_sheet(f, fname=None):
    """Read compact germline TSV format from file-like object ``f``

    :return: models.Sheet
    """
    return GermlineTSVReader(f, fname).read_sheet()


def read_germline_tsv_json_data(f, fname=None):
    """Read compact germline TSV format from file-like object ``f``

    :return: ``dict``
    """
    return GermlineTSVReader(f, fname).read_json_data()
