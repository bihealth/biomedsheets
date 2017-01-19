# -*- coding: utf-8 -*-
"""Code for reading and writing the compact TSV formats
"""

from collections import OrderedDict

from . import io
from . import ref_resolver
from . import models

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Default title
DEFAULT_TITLE = 'Cancer Sample Sheet'

#: Default description
DEFAULT_DESCRIPTION = (
    'Sample Sheet constructed from cancer matched samples '
    'compact TSV file')

#: Delimiter to use
DELIM = '\t'

#: Cancer TSV header
CANCER_TSV_HEADER = ('patientName', 'sampleName', 'isCancer',
                     'libraryType', 'folderName')

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

#: Fixed "extraInfoDefs" field for cancer compact TSV
CANCER_EXTRA_INFO_DEFS = OrderedDict([
    ('bioEntity', OrderedDict([
        ('ncbiTaxon', OrderedDict([
            ('$ref',
             'resource://biomedsheets/data/std_fields.json'
             '#/extraInfoDefs/template/ncbiTaxon')
        ])),
    ])),
    ('bioSample', OrderedDict([
        ('isCancer', OrderedDict([
            ('$ref',
             'resource://biomedsheets/data/std_fields.json'
             '#/extraInfoDefs/template/isCancer')
        ])),
    ])),
    ('testSample', OrderedDict([
        ('extractionType', OrderedDict([
            ('$ref',
             'resource://biomedsheets/data/std_fields.json'
             '#/extraInfoDefs/template/extractionType')
        ])),
    ])),
    ('ngsLibrary', OrderedDict([
        ('libraryType', OrderedDict([
            ('$ref',
             'resource://biomedsheets/data/std_fields.json'
             '#/extraInfoDefs/template/libraryType')
        ])),
        ('folderName', OrderedDict([
            ('$ref',
             'resource://biomedsheets/data/std_fields.json'
             '#/extraInfoDefs/template/folderName')
        ])),
    ])),
])


class SheetIOException(Exception):
    """Raised on problems with loading sample sheets"""


class TSVSheetException(SheetIOException):
    """Raised on problems with loading the compact TSV sheets"""


class CancerTSVSheetException(TSVSheetException):
    """Raised on problems with loading cancer TSV sample sheets"""


class CancerTSVReader:
    """Helper class for reading cancer TSV file

    Prefer using ``read_cancer_tsv_*()`` for shortcut
    """

    def __init__(self, f, fname=None):
        self.f = f
        self.fname = fname or '<unknown>'
        self.next_pk = 1

    def read_json_data(self):
        """Read from file-like object ``self.f``, use file name in case of
        problems

        :raises:CancerTSVSheetException in case of problems
        """
        # Read lines from file and check for file not being empty
        lines = [l.strip() for l in self.f]
        if not lines:
            raise CancerTSVSheetException(
                'Problem loading cancer TSV sheet in file {}'.format(
                    self.fname))
        # Decide between the case with or without header
        if lines[0].startswith('['):
            header, body = self._split_lines(lines)
        else:
            header = []
            body = lines
        # Process header and then create a models.Sheet
        proc_header = self._process_header(header)
        if not body or set(body[0].split('\t')) != set(CANCER_TSV_HEADER):
            raise CancerTSVSheetException(
                ('Empty or invalid data column names in cancer TSV sheet '
                 'file {}. Must be {{{}}} but is {{{}}}').format(
                     self.fname, ', '.join(CANCER_TSV_HEADER),
                     body[0].replace('\t', ', ')))
        return self._create_sheet_json(proc_header, body)

    def read_sheet(self):
        """Read into JSON and construct ``models.Sheet``"""
        return io.SheetBuilder(self.read_json_data()).run()

    def _split_lines(self, lines):
        """Split string array lines into header and body"""
        header, body = [], []
        in_data = False
        for line in lines:
            if in_data:
                body.append(line)
            else:
                header.append(line)
                if line.startswith('[Data]'):
                    in_data = True
        return header, body

    def _process_header(self, header):
        """Process header lines"""
        result = {}
        for line in header:
            if DELIM in line:
                key, value = line.split(DELIM, 1)
                result[key] = value
        return result

    def _create_sheet_json(self, header_dict, body):
        """Create models.Sheet object from header dictionary and body lines
        """
        names = body[0].split('\t')  # idx to name
        # Build validated list of records
        records = []
        for lineno, line in enumerate(body[1:]):
            arr = line.split('\t')
            # Check number of entries in line
            if len(arr) != len(names):
                raise CancerTSVSheetException(
                    ('Invalid number of entries in line {} of data '
                     'section of {}').format(lineno + 2, self.fname))
            mapping = dict(zip(names, arr))
            # Check "isCancer" field, convert to bool
            if mapping['isCancer'] not in BOOL_VALUES.keys():
                raise CancerTSVSheetException(
                    ('Invalid boolean value {} in line {} of data '
                     'section of {}').format(
                         mapping['isCancer'], lineno + 2, self.fname))
            mapping['isCancer'] = BOOL_VALUES[mapping['isCancer']]
            # Check "libraryType" field
            if mapping['libraryType'] not in LIBRARY_TYPES:
                raise CancerTSVSheetException(
                    'Invalid library type {}, must be in {{{}}}'.format(
                        mapping['libraryType'], ', '.join(LIBRARY_TYPES)))
            # Check other fields for being non-empty
            for key in CANCER_TSV_HEADER:
                if mapping[key] == '':
                    raise CancerTSVSheetException(
                        'Field {} empty in line {} of {}'.format(
                            key, lineno + 2, self.fname))
            records.append(mapping)
        # TODO: we should perform more validation here in the future
        # Create the sheet from records
        return self._create_sheet_json_from_records(header_dict, records)

    def _create_sheet_json_from_records(self, header_dict, records):
        """Create a new models.Sheet object from TSV records"""
        furl = 'file://{}'.format(self.fname)
        resolver = ref_resolver.RefResolver(dict_class=OrderedDict)
        extraDefs = resolver.resolve(furl, CANCER_EXTRA_INFO_DEFS)
        json_data = OrderedDict([
            ('identifier', furl),
            ('title', header_dict.get(KEY_TITLE, DEFAULT_TITLE)),
            ('description',
             header_dict.get(KEY_DESCRIPTION, DEFAULT_DESCRIPTION)),
            ('extraInfoDefs', extraDefs),
            ('bioEntities', OrderedDict()),
        ])
        patient_records = OrderedDict()
        for record in records:
            patient_records.setdefault(record['patientName'], [])
            patient_records[record['patientName']].append(record)
        for patient_name, entry in patient_records.items():
            json_data['bioEntities'][patient_name] = \
                self._build_bio_entity_json(patient_name, entry)
        return json_data

    def _build_bio_entity_json(self, patient_name, records):
        """Build JSON for bio_entities entry"""
        result = OrderedDict([
            ('pk', self.next_pk),
            ('extraInfo', OrderedDict([
                ('ncbiTaxon', 'NCBITaxon_9606'),
            ])),
            ('bioSamples', OrderedDict()),
        ])
        self.next_pk += 1
        sample_records = OrderedDict()
        for record in records:
            sample_records.setdefault(record['sampleName'], [])
            sample_records[record['sampleName']].append(record)
        for sample_name, entry in sample_records.items():
            result['bioSamples'][sample_name] = \
                self._build_bio_sample_json(sample_name, entry)
        return result

    def _build_bio_sample_json(self, sample_name, records):
        """Build JSON for bio_samples entry

        A test sample entry will be implicitely added.
        """
        if len(set(r['isCancer'] for r in records)) != 1:
            raise CancerTSVSheetException(
                'Inconsistent "isCancer" flag for records')
        result = OrderedDict([
            ('pk', self.next_pk),
            ('extraInfo', OrderedDict([
                ('isCancer', records[0]['isCancer']),
            ])),
            ('testSamples', OrderedDict()),
        ])
        self.next_pk += 1
        counters_ext = dict((x, 1) for x in EXTRACTION_TYPES)
        counters_lib = dict((x, 1) for x in LIBRARY_TYPES)
        for record in records:
            extraction_type = LIBRARY_TO_EXTRACTION[record['libraryType']]
            test_sample_name = '{}{}'.format(
                extraction_type, counters_ext[extraction_type])
            lib_name = '{}{}'.format(record['libraryType'],
                                     counters_lib[record['libraryType']])
            counters_ext[extraction_type] += 1
            counters_lib[record['libraryType']] += 1
            pk = self.next_pk
            self.next_pk += 1
            result['testSamples'][test_sample_name] = OrderedDict([
                ('pk', pk),
                ('extraInfo', OrderedDict([
                    ('extractionType', extraction_type),
                ])),
                ('ngsLibraries', OrderedDict([
                    (lib_name, self._build_ngs_library_json(lib_name, record)),
                ]))
            ])
        return result


    def _build_ngs_library_json(self, library_name, record):
        """Build JSON for ngs_libraries entry"""
        result = OrderedDict([
            ('pk', self.next_pk),
            ('extraInfo', OrderedDict([
                ('folderName', record['folderName']),
                ('libraryType', record['libraryType']),
            ])),
        ])
        self.next_pk += 1
        return result


def read_cancer_tsv_sheet(f, fname=None):
    """Read compact cancer TSV format from file-like object ``f``

    :return: models.Sheet
    """
    return CancerTSVReader(f, fname).read_sheet()


def read_cancer_tsv_json_data(f, fname=None):
    """Read compact cancer TSV format from file-like object ``f``

    :return: ``dict``
    """
    return CancerTSVReader(f, fname).read_json_data()
