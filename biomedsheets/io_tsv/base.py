# -*- coding: utf-8 -*-
"""Base code for reading compact TSV format
"""

from collections import OrderedDict

from .. import ref_resolver
from .. import io
from ..naming import name_generator_for_scheme, NAMING_DEFAULT

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

# TODO: allow setting NCBI taxon through header
# TODO: allow disabling of PK generation through header?

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

#: Extraction type DNA
EXTRACTION_TYPE_DNA = 'DNA'

#: Extraction type RNA
EXTRACTION_TYPE_RNA = 'RNA'

#: Known extraction types
EXTRACTION_TYPES = (EXTRACTION_TYPE_DNA, EXTRACTION_TYPE_RNA)

#: Key for the TSV header, field "title"
KEY_TITLE = 'title'

#: Key for the TSV header, field "description"
KEY_DESCRIPTION = 'description'

#: Platform "Illumina"
PLATFORM_ILLUMINA = 'Illumina'

#: Platform "PacBio"
PLATFORM_PACBIO = 'PacBio'

#: Platform "other"
PLATFORM_OTHER = 'other'

#: Platform default
PLATFORM_DEFAULT = PLATFORM_ILLUMINA

#: Known platforms
PLATFORM_NAMES = (PLATFORM_ILLUMINA, PLATFORM_PACBIO, PLATFORM_OTHER)

#: Constants for interpreting booleans
BOOL_VALUES = {
    'Y': True,
    'y': True,
    'N': False,
    'n': False,
}

#: NCBI taxon for human
NCBI_TAXON_HUMAN = 'NCBITaxon_9606'


class SheetIOException(Exception):
    """Raised on problems with loading sample sheets"""


class TSVSheetException(SheetIOException):
    """Raised on problems with loading the compact TSV sheets"""


def std_field(name):
    """Return data structure for returning JSON pointer data structure"""
    tpl = ('resource://biomedsheets/data/std_fields.json#'
           '/extraInfoDefs/template/{}')
    return (name, OrderedDict([('$ref', tpl.format(name))]))


class BaseTSVReader:
    """Base class for shortcut TSV readers"""

    #: Iterable with TSV header
    tsv_header = None
    #: Extra info definitions
    extra_info_defs = None
    #: Default title
    default_title = None
    #: Default description
    default_description = None
    #: Name of bio_entity name column
    bio_entity_name_column = None
    #: Name of the bio_sample name column
    bio_sample_name_column = None
    #: Default sample name if not given in the sample sheet
    bio_sample_name = None
    #: Single extraction type if given
    extraction_type = None

    def __init__(self, f, fname=None):
        self.f = f
        self.fname = fname or '<unknown>'
        self.next_pk = 1

    def read_json_data(self):
        """Read from file-like object ``self.f``, use file name in case of
        problems

        :raises:TSVSheetException in case of problems
        """
        # Read lines from file and check for file not being empty
        lines = [l.strip() for l in self.f]
        if not lines:
            raise TSVSheetException(
                'Problem loading TSV sheet in file {}'.format(
                    self.fname))  # pragma: no cover
        # Decide between the case with or without header
        if lines[0].startswith('['):
            header, body = self._split_lines(lines)
        else:
            header = []
            body = lines
        # Process header and then create a models.Sheet
        proc_header = self._process_header(header)
        header = body[0].split('\t')
        missing_columns = set(
            self.__class__.tsv_header) - set(body[0].split('\t'))
        if not body or missing_columns:
            raise TSVSheetException(
                ('Empty or invalid data column names in TSV sheet file {}. '
                 'Must be superset of {{{}}} but is missing {{{}}}').format(
                     self.fname, ', '.join(self.__class__.tsv_header),
                     ', '.join(missing_columns)))  # pragma: no cover
        return self._create_sheet_json(proc_header, body)

    def read_sheet(self, name_generator=None):
        """Read into JSON and construct ``models.Sheet``"""
        self.name_generator = name_generator or name_generator_for_scheme(
            NAMING_DEFAULT)
        return io.SheetBuilder(self.read_json_data()).run(
            name_generator=name_generator)

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
            # Replace '.' and '' with ``None``, for empty field
            arr = [(x if x not in ('.', '') else None) for x in arr]
            # Check number of entries in line
            if len(arr) != len(names):
                msg = ('Invalid number of entries in line {} of data '
                       'section of {}: {} vs {}')
                raise TSVSheetException(msg.format(
                    lineno + 2, self.fname, arr, names))  # pragma: no cover
            mapping = dict(zip(names, arr))
            self.check_tsv_line(mapping, lineno)
            records.append(mapping)
        # Create the sheet from records
        return self._create_sheet_json_from_records(header_dict, records)

    def check_tsv_line(self, mapping, lineno):
        """Check TSV line after conversion into mapping

        Override in sub classes
        """
        raise NotImplementedError('Override in sub class')  # pragma: no cover

    def _create_sheet_json_from_records(self, header_dict, records):
        """Create a new models.Sheet object from TSV records"""
        furl = 'file://{}'.format(self.fname)
        resolver = ref_resolver.RefResolver(dict_class=OrderedDict)
        extra_defs = resolver.resolve(furl, self.__class__.extra_info_defs)
        json_data = OrderedDict([
            ('identifier', furl),
            ('title', header_dict.get(
                KEY_TITLE, self.__class__.default_title)),
            ('description', header_dict.get(
                KEY_DESCRIPTION, self.__class__.default_description)),
            ('extraInfoDefs', extra_defs),
            ('bioEntities', OrderedDict()),
        ])
        records_by_bio_entity = OrderedDict()  # records by bio entity
        for record in records:
            records_by_bio_entity.setdefault(
                record[self.__class__.bio_entity_name_column], [])
            records_by_bio_entity[record[
                self.__class__.bio_entity_name_column]].append(record)
        for bio_entity_name, records in records_by_bio_entity.items():
            json_data['bioEntities'][
                bio_entity_name] = self._build_bio_entity_json(records)
        return self.postprocess_json_data(json_data)

    def postprocess_json_data(self, json_data):
        """Postprocess JSON data"""
        return json_data

    def _build_bio_entity_json(self, sub_records):
        """Build JSON for bio_entities entry"""
        result = self.construct_bio_entity_dict(sub_records)
        # If the sub class defines a sample name column then use it to further
        # split up the sample names.  Otherwise, there can only be one sample
        # name and its name must be defined in the class.
        if self.__class__.bio_sample_name_column:
            sample_records = OrderedDict()  # records by bio sample
            for record in sub_records:
                sample_records.setdefault(record['sampleName'], [])
                sample_records[record['sampleName']].append(record)
            for sample_name, entry in sample_records.items():
                result['bioSamples'][
                    sample_name] = self._build_bio_sample_json(entry)
        else:
            assert self.__class__.bio_sample_name, \
                'Must be given if bio_sample_name_column is not'
            # skip if no record with libraryType
            if any(r['libraryType'] for r in sub_records):
                result['bioSamples'][self.__class__.bio_sample_name] = (
                    self._build_bio_sample_json(sub_records))
        return result

    def construct_bio_entity_dict(self, records):
        """Construct BioEntity dict from bio entity--related record

        Override in sub class to set extraInfo attributes of dict
        """
        self.next_pk += 1
        return OrderedDict([
            ('pk', self.next_pk - 1),
            ('extraInfo', OrderedDict([
                ('ncbiTaxon', NCBI_TAXON_HUMAN),
            ])),
            ('bioSamples', OrderedDict()),
        ])

    def _build_bio_sample_json(self, records):
        """Build JSON for bio_samples entry

        A single test sample entry will be implicitely added.
        """
        self.check_bio_sample_records(records)
        result = self.construct_bio_sample_dict(records)
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
                    (lib_name, self._build_ngs_library_json(record)),
                ]))
            ])
        return result

    def check_bio_sample_records(self, record):
        """Override in sub class to check for consistent bio sample records"""

    def construct_bio_sample_dict(self, _):
        """Construct BioSample dict from bio sample--related records

        Override in sub class to set extraInfo attributes of dict
        """
        self.next_pk += 1
        return OrderedDict([
            ('pk', self.next_pk - 1),
            ('extraInfo', OrderedDict()),
            ('testSamples', OrderedDict()),
        ])

    def _build_ngs_library_json(self, record):
        """Build JSON for ngs_libraries entry"""
        result = self.construct_bio_ngs_library_dict(record)
        return result

    def construct_bio_ngs_library_dict(self, record):
        """Construct NGSLibrary dict from NGS library--related record

        Override in sub class to set extraInfo attributes of dict
        """
        self.next_pk += 1
        return OrderedDict([
            ('pk', self.next_pk - 1),
            ('extraInfo', OrderedDict([
                ('seqPlatform', record.get('seqPlatform', PLATFORM_DEFAULT)),
                ('folderName', record['folderName']),
                ('libraryType', record['libraryType']),
            ])),
        ])
