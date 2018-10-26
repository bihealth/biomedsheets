# -*- coding: utf-8 -*-
"""Base code for reading compact TSV format
"""

from collections import OrderedDict
import re

from .. import ref_resolver
from .. import io
from ..naming import name_generator_for_scheme, NAMING_DEFAULT

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

# TODO: allow setting NCBI taxon through header
# TODO: allow disabling of PK generation through header?

#: Delimiter to use
DELIM = '\t'

#: Known schemas
TSV_SCHEMAS = (
    'cancer_matched', 'germline_variants', 'generic')

#: Known file format versions
FILE_FORMAT_VERSIONS = ('v1',)

#: Keys of TSV [Metadata] section
METADATA_KEYS = ('schema', 'schema_version', 'title', 'description')

#: Valid entities to refer to in custom fields
ENTITY_TYPES = ('bioEntity', 'bioSample', 'testSample', 'ngsLibrary')

#: Valid field types in TSV files
FIELD_TYPES = (
    'string', 'integer', 'boolean', 'number', 'enum', 'pattern')

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
    'YES': True,
    'yes': True,
    'NO': False,
    'no': False,
    'true': True,
    'false': False,
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


class TSVMetadata:
    """Meta data information"""

    def __init__(self, schema=None, schema_version=None, title=None,
                 description=None):
        #: Schema to use for the sample sheet
        self.schema = schema
        #: Version of the sample sheet file format
        self.schema_version = schema_version
        #: Title of the sample sheet
        self.title = title
        #: Description of the sample sheet
        self.description = description


class TSVCustomFieldsInfo:
    """Information about custom fields"""

    def __init__(
            self, key, entity, docs, field_type, minimum, maximum, unit,
            choices, pattern):
        #: Name/key of the field
        self.key = key
        #: The annotated entity
        self.entity = entity
        #: Documentation string, ``None`` if empty
        self.docs = docs
        #: The field type
        self.field_type = field_type
        #: The smallest value
        self.minimum = minimum
        #: The largest value
        self.maximum = maximum
        #: The unit of the value (free text)
        self.unit = unit
        #: Iterable with valid choices
        self.choices = None if choices is None else list(choices)
        #: The regular expression pattern of any
        self.pattern = pattern
        # Ensure all values are valid
        self._validate()

    def _validate(self):
        """Validate the the vaules in this object are valid"""
        if not self.key:
            raise TSVSheetException('Missing field name/key: ' + repr(self.key))
        if self.entity not in ENTITY_TYPES:
            raise TSVSheetException('Invalid entity: ' + repr(self.entity))
        if self.field_type not in FIELD_TYPES:
            raise TSVSheetException(
                'Invalid field type: ' + repr(self.field_type))
        self.minimum = self._convert_minmax(self.minimum, 'minimum')
        self.maximum = self._convert_minmax(self.maximum, 'maximum')
        if self.pattern:
            try:
                re.compile(self.pattern)
            except re.error:
                raise TSVSheetException(
                    'Invalid regular expression ' + repr(self.pattern))

    def _convert_minmax(self, val, which):
        if val is None:
            return None
        else:
            try:
                if self.field_type == 'integer':
                    return int(val)
                else:  # self.field_type == 'number'
                    return float(val)
            except TypeError:
                raise TSVSheetException(
                    'Invalid {} value: {}'.format(which, val))

    def __str__(self):
        return 'TSVCustomFieldsInfo({})'.format(
            ', '.join(map(
                repr, (self.key, self.entity, self.docs, self.field_type,
                       self.minimum, self.maximum, self.unit, self.choices,
                       self.pattern))))

    def __repr__(self):
        return str(self)


class TSVHeader:
    """Header information of succinct TSV files"""

    def __init__(self, metadata=None, custom_field_infos=None):
        #: TSVMetadata with overall information
        self.metadata = metadata
        #: List of TSVCustomFieldsInfo with custom field information
        self.custom_field_infos = OrderedDict([
            (info.key, info) for info in custom_field_infos or []])

    def __str__(self):
        return 'TSVHeader({}, {})'.format(*map(
            repr, (self.metadata, self.custom_field_infos)))

    def __repr__(self):
        return str(self)


#: Header with custom fields
CUSTOM_FIELDS_HEADER = (
    'key\tannotatedEntity\tdocs\ttype\tminimum\tmaximum\tunit\t'
    'choices\tpattern')


class TSVHeaderParser:
    """Parse TSV header from list of header lines"""

    def __init__(self, lines):
        #: List of lines to process
        self.lines = lines

    def run(self):
        """Process header lines and return TSVHeader object"""
        metadata = TSVMetadata()
        custom_fields_header = None
        custom_fields_infos = []
        state = None
        for line in self.lines:
            if line.startswith('#'):
                continue  # comment: ignore
            elif line.startswith('[Metadata]'):
                state = 'metadata'
                continue
            elif line.startswith('[Custom Fields]'):
                state = 'custom_fields'
                continue
            elif line.startswith('[Data]'):
                state = 'data'
                continue
            line = line.strip()
            if not line:
                continue  # skip empty lines
            if state == 'metadata':
                if '\t' not in line:
                    key, value = line, None
                else:
                    key, value = line.split('\t', 1)
                if key not in METADATA_KEYS:
                    raise TSVSheetException('Invalid [Metadata] key: ' + key)
                setattr(metadata, key, value)
            elif state == 'custom_fields':
                if not custom_fields_header:
                    custom_fields_header = line.strip()
                    if custom_fields_header != CUSTOM_FIELDS_HEADER:
                        raise TSVSheetException(
                            ('Invalid custom fields header: {}, '
                             'expected {}').format(
                                 repr(custom_fields_header),
                                 repr(CUSTOM_FIELDS_HEADER)))
                    custom_fields_header = custom_fields_header.split('\t')
                else:
                    custom_fields_infos.append(self._process_custom_fields(
                        line.split('\t')))
        return TSVHeader(metadata, custom_fields_infos)

    @classmethod
    def _process_custom_fields(cls, arr):
        if len(arr) != 9:
            raise TSVSheetException(
                ('Invalid number of entries in [Custom Fields] line: {}, '
                 'should be 9').format(len(arr)))
        arr = [x if x not in ('.', '') else None for x in arr]
        if arr[7]:  # choices
            arr[7] = arr[7].split(',')
        return TSVCustomFieldsInfo(*arr)


class BaseTSVReader:
    """Base class for shortcut TSV readers"""

    #: Iterable with TSV header
    body_header = None
    #: Optional column in body header
    optional_body_header_columns = ('seqPlatform',)
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
    #: Name of the test_sample name column
    test_sample_name_column = None
    #: Name of the ngs_library name column
    ngs_library_name_column = None
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
        tsv_header = TSVHeaderParser(header).run()
        body_header = body[0].split('\t')
        missing_columns = set(self.__class__.body_header) - set(body_header)
        if not body or missing_columns:
            raise TSVSheetException(
                ('Empty or invalid data column names in TSV sheet file {}. '
                 'Must be superset of {{{}}} but is missing {{{}}}').format(
                     self.fname, ', '.join(self.__class__.body_header),
                     ', '.join(missing_columns)))  # pragma: no cover
        # Check for unknown fields
        extra_columns = (
            set(body_header) -
            set(self.__class__.body_header) -
            set(tsv_header.custom_field_infos.keys()) -
            set(self.__class__.optional_body_header_columns))
        if extra_columns:
            msg = 'Unexpected column seen in header row of body: {}'
            raise TSVSheetException(
                msg.format(', '.join(sorted(extra_columns))))
        return self._create_sheet_json(tsv_header, body)

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
            if line.startswith('#'):
                continue  # comment, skip
            elif in_data:
                body.append(line)
            else:
                header.append(line)
                if line.startswith('[Data]'):
                    in_data = True
        return header, body

    def _create_sheet_json(self, tsv_header, body):
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
            mapping = self.convert_tsv_line(mapping, tsv_header)
            self.check_tsv_line(mapping, lineno)
            records.append(mapping)
        # Create the sheet from records
        return self._create_sheet_json_from_records(tsv_header, records)

    @classmethod
    def convert_tsv_line(cls, mapping, tsv_header):
        """Convert fields in TSV line after conversion to mapping"""
        custom_field_infos = tsv_header.custom_field_infos
        table = {
            'integer': int,
            'number': float,
            'boolean': lambda x: BOOL_VALUES.get(x, False),
        }
        for key, value in mapping.items():
            if value is not None and key in custom_field_infos:
                mapping[key] = table.get(
                    custom_field_infos[key].field_type,
                    lambda x: x)(value)
        return mapping

    def check_tsv_line(self, mapping, lineno):
        """Check TSV line after conversion into mapping

        Override in sub classes
        """
        raise NotImplementedError('Override in sub class')  # pragma: no cover

    def _create_sheet_json_from_records(self, tsv_header, records):
        """Create a new models.Sheet object from TSV records"""
        furl = 'file://{}'.format(self.fname)
        resolver = ref_resolver.RefResolver(dict_class=OrderedDict)
        extra_info_defs = self._augment_extra_info_defs(
            resolver.resolve(furl, self.__class__.extra_info_defs),
            tsv_header)
        json_data = OrderedDict([
            ('identifier', furl),
            ('title', (tsv_header.metadata.title or
                       self.__class__.default_title)),
            ('description', (
                tsv_header.metadata.description or
                self.__class__.default_description)),
            ('extraInfoDefs', extra_info_defs),
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
                bio_entity_name] = self._build_bio_entity_json(
                    records, extra_info_defs)
        return self.postprocess_json_data(json_data)

    @classmethod
    def _augment_extra_info_defs(cls, extra_info_defs, tsv_header):
        """Augment extra definitions with TSV ``[Custom Fields]`` header.
        """
        for info in tsv_header.custom_field_infos.values():
            if info.key not in extra_info_defs[info.entity]:
                extra_def = OrderedDict()
                if info.docs:
                    extra_def['docs'] = info.docs
                extra_def['key'] = info.key
                extra_def['type'] = info.field_type
                if info.pattern:
                    extra_def['pattern'] = info.pattern
                if info.minimum is not None:
                    extra_def['minimum'] = info.minimum
                if info.maximum is not None:
                    extra_def['maximum'] = info.maximum
                if info.choices:
                    extra_def['choices'] = info.choices
                if info.unit:
                    extra_def['unit'] = info.unit
                extra_info_defs[info.entity][info.key] = extra_def
        return extra_info_defs

    def postprocess_json_data(self, json_data):
        """Postprocess JSON data"""
        return json_data

    def _build_bio_entity_json(self, sub_records, extra_info_defs):
        """Build JSON for bio_entities entry"""
        result = self.construct_bio_entity_dict(sub_records, extra_info_defs)
        # If the sub class defines a sample name column then use it to further
        # split up the sample names.  Otherwise, there can only be one sample
        # name and its name must be defined in the class.
        if (self.__class__.bio_sample_name_column and
                any(self.__class__.bio_sample_name_column in record for record in sub_records)):
            sample_records = OrderedDict()  # records by bio sample
            for record in sub_records:
                sample_name = record[self.__class__.bio_sample_name_column]
                sample_records.setdefault(sample_name, [])
                sample_records[sample_name].append(record)
            for sample_name, entry in sample_records.items():
                result['bioSamples'][
                    sample_name] = self._build_bio_sample_json(
                        entry, extra_info_defs)
        else:
            assert self.__class__.bio_sample_name, \
                'Must be given if bio_sample_name_column is not'
            # skip if no record with libraryType
            if any(r['libraryType'] for r in sub_records):
                result['bioSamples'][self.__class__.bio_sample_name] = (
                    self._build_bio_sample_json(sub_records, extra_info_defs))
        return result

    def construct_bio_entity_dict(self, records, extra_info_defs):
        """Construct BioEntity dict from bio entity--related record

        Override in sub class to set extraInfo attributes of dict
        """
        self.next_pk += 1
        bio_entity_json = OrderedDict([
            ('pk', self.next_pk - 1),
            ('extraInfo', OrderedDict([
            ])),
            ('bioSamples', OrderedDict()),
        ])
        return self._augment_bio_entity_json(
            bio_entity_json, records[0], extra_info_defs)

    @classmethod
    def _augment_bio_entity_json(
            cls, bio_entity_json, record, extra_info_defs):
        """Augment test sample JSON"""
        for key in extra_info_defs['bioEntity']:
            if key not in bio_entity_json['extraInfo'] and record.get(key):
                bio_entity_json['extraInfo'][key] = record[key]
        return bio_entity_json

    def _build_bio_sample_json(self, records, extra_info_defs):
        """Build JSON for bio_samples entry

        A single test sample entry will be implicitely added.
        """
        self.check_bio_sample_records(records, extra_info_defs)
        result = self.construct_bio_sample_dict(records, extra_info_defs)
        counters_ext = dict((x, 1) for x in EXTRACTION_TYPES)
        counters_lib = {}
        print('reading...', records)
        for record in records:
            if not record['libraryType'] in LIBRARY_TO_EXTRACTION:
                continue
            extraction_type = LIBRARY_TO_EXTRACTION[record['libraryType']]
            if (self.__class__.test_sample_name_column and
                    self.__class__.test_sample_name_column in record):
                test_sample_name = record[
                    self.__class__.test_sample_name_column]
            else:
                test_sample_name = '{}{}'.format(
                    extraction_type, counters_ext[extraction_type])
            if self.__class__.ngs_library_name_column:
                lib_name = record[self.__class__.ngs_library_name_column]
            else:
                counters_lib.setdefault(test_sample_name, dict((x, 1) for x in LIBRARY_TYPES))
                lib_name = '{}{}'.format(record['libraryType'],
                                         counters_lib[test_sample_name][record['libraryType']])
                counters_lib[test_sample_name][record['libraryType']] += 1
            pk = self.next_pk
            self.next_pk += 1
            if test_sample_name not in result['testSamples']:
                test_sample_json = OrderedDict([
                    ('pk', pk),
                    ('extraInfo', OrderedDict([
                        ('extractionType', extraction_type),
                    ])),
                    ('ngsLibraries', OrderedDict([
                        (lib_name, self._build_ngs_library_json(
                            record, extra_info_defs)),
                    ]))
                ])
                test_sample_json = self._augment_test_sample_json(
                    test_sample_json, record, extra_info_defs)
                result['testSamples'][test_sample_name] = test_sample_json
            else:
                libraries = result['testSamples'][test_sample_name]['ngsLibraries']
                libraries[lib_name] = self._build_ngs_library_json(record, extra_info_defs)
        return result

    @classmethod
    def _augment_test_sample_json(
            cls, test_sample_json, record, extra_info_defs):
        """Augment test sample JSON"""
        for key in extra_info_defs['testSample']:
            if key not in test_sample_json['extraInfo'] and record.get(key):
                test_sample_json['extraInfo'][key] = record[key]
        return test_sample_json

    def check_bio_sample_records(self, record, extra_info_defs):
        """Override in sub class to check for consistent bio sample records"""

    def construct_bio_sample_dict(self, records, extra_info_defs):
        """Construct BioSample dict from bio sample--related records

        Override in sub class to set extraInfo attributes of dict
        """
        self.next_pk += 1
        bio_sample_json = OrderedDict([
            ('pk', self.next_pk - 1),
            ('extraInfo', OrderedDict()),
            ('testSamples', OrderedDict()),
        ])
        return self._augment_bio_sample_json(
            bio_sample_json, records[0], extra_info_defs)

    @classmethod
    def _augment_bio_sample_json(
            cls, bio_sample_json, record, extra_info_defs):
        """Augment test sample JSON"""
        for key in extra_info_defs['bioSample']:
            if key not in bio_sample_json['extraInfo'] and record.get(key):
                bio_sample_json['extraInfo'][key] = record[key]
        return bio_sample_json

    def _build_ngs_library_json(self, record, extra_info_defs):
        """Build JSON for ngs_libraries entry"""
        result = self.construct_bio_ngs_library_dict(record, extra_info_defs)
        return self._augment_ngs_library_json(result, record, extra_info_defs)

    @classmethod
    def _augment_ngs_library_json(
            cls, ngs_library_json, record, extra_info_defs):
        """Augment NGS library JSON"""
        for key in extra_info_defs['ngsLibrary']:
            if key not in ngs_library_json['extraInfo'] and key in record:
                ngs_library_json['extraInfo'][key] = record[key]
        return ngs_library_json

    def construct_bio_ngs_library_dict(self, record, extra_info_defs):
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
