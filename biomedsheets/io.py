# -*- coding: utf-8 -*-
"""Code for reading and writing BioMed Sheets from/to file-like objects

Optionally, objects can be validated before reading/writing.
"""

from collections import OrderedDict
import json

from . import models
from .naming import DEFAULT_NAME_GENERATOR

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


def json_loads_ordered(s):
    """Helper function to load JSON using OrderedDict for object pairs"""
    return json.loads(s, object_pairs_hook=OrderedDict)


class SheetSchema:
    """Programmatic access to the bundled BioMed Schema JSON file"""

    @classmethod
    def load_from_string(self, s):
        """Load schema from JSON string ``s``"""
        return SheetSchema(json_loads_ordered(s))

    def __init__(self, parsed_json):
        #: parsed JSON that is wrapped by schema
        self.parsed_json = parsed_json


class ExtraInfoBuilder:
    """Helper class for converting from "extraInfo" value to Python value
    """

    def __init__(self, definition):
        #: Dispatch table for different types, mostly Python type constructors
        self.builders = {
            'boolean': bool,
            'string': str,
            'pattern': str,
            'integer': int,
            'number': float,
            'enum': str,
            'object': lambda x: x,  # identity
            'array': self._build_array,
        }
        #: Definition from JSON file
        self.definition = definition

    def build(self, value):
        return self.builders[self.definition['type']](value)

    def _build_array(self, value):
        """Handle array entry type"""
        func = self.builders[self.definition['entry']]
        return list(map(func, value))


class SheetBuilder:
    """Helper class to construct ``models.Sheet`` from JSON sheet data

    This is implemented as a class instead of a function so state can be
    stored in attributes and be used implicitely in the methods than
    having to be passed explicitely in function arguments
    """

    def __init__(self, json_data):
        #: Validated BioMed Sheet data
        self.json_data = json_data

    def run(self, dict_type=OrderedDict,
            name_generator=DEFAULT_NAME_GENERATOR):
        return models.Sheet(
            identifier=self.json_data.get('identifier', ''),
            title=self.json_data.get('title', ''),
            description=self.json_data.get('description', ''),
            bio_entities=self._build_bio_entities(
                extra_infos_defs=self.json_data.get(
                    'extraInfoDefs', dict_type()),
                bio_entities_json=self.json_data.get(
                    'bioEntities', dict_type()),
                dict_type=dict_type,
                name_generator=name_generator),
            json_data=self.json_data,
            dict_type=dict_type,
            name_generator=name_generator)

    def _build_bio_entities(
            self, extra_infos_defs, bio_entities_json, dict_type,
            name_generator):
        """Build BioEntity list
        """
        for secondary_id, value in bio_entities_json.items():
            bio_entity = models.BioEntity(
                pk=value['pk'],
                disabled=value.get('disabled', False),
                secondary_id=secondary_id,
                extra_ids=value.get('extraIds', []),
                extra_infos=dict_type(self._build_extra_infos(
                    extra_infos=value.get('extraInfo', dict_type()),
                    extra_infos_defs=extra_infos_defs.get(
                        'bioEntity', dict_type()),
                    dict_type=dict_type,
                    name_generator=name_generator)),
                bio_samples=dict_type(self._build_bio_samples(
                    extra_infos_defs=extra_infos_defs,
                    bio_samples_json=value.get('bioSamples', dict_type()),
                    dict_type=dict_type,
                    name_generator=name_generator)),
                dict_type=dict_type,
                name_generator=name_generator)
            yield (secondary_id, bio_entity)

    @classmethod
    def _build_extra_infos(
            cls, extra_infos_defs, extra_infos, dict_type, name_generator):
        """Interpret extraInfo stuff, including type conversion"""
        for key, value in extra_infos.items():
            yield (key, ExtraInfoBuilder(extra_infos_defs[key]).build(value))

    def _build_bio_samples(
            self, extra_infos_defs, bio_samples_json, dict_type,
            name_generator):
        """Build models.BioSample object, root JSON is required for attribute
        description
        """
        for secondary_id, value in bio_samples_json.items():
            bio_sample = models.BioSample(
                pk=value['pk'],
                disabled=value.get('disabled', False),
                secondary_id=secondary_id,
                extra_ids=value.get('extraIds', []),
                extra_infos=dict_type(self._build_extra_infos(
                    extra_infos=value.get('extraInfo', dict_type()),
                    extra_infos_defs=extra_infos_defs.get(
                        'bioSample', dict_type()),
                    dict_type=dict_type,
                    name_generator=name_generator)),
                test_samples=dict_type(self._build_test_samples(
                    extra_infos_defs, value.get('testSamples', dict_type()),
                    dict_type, name_generator)),
                dict_type=dict_type,
                name_generator=name_generator)
            yield (secondary_id, bio_sample)

    def _build_test_samples(
            self, extra_infos_defs, test_samples_json, dict_type,
            name_generator):
        """Build models.TestSample object
        """
        for secondary_id, value in test_samples_json.items():
            test_sample = models.TestSample(
                pk=value['pk'],
                disabled=value.get('disabled', False),
                secondary_id=secondary_id,
                extra_ids=value.get('extraIds', []),
                extra_infos=dict_type(self._build_extra_infos(
                    extra_infos=value.get('extraInfo', dict_type()),
                    extra_infos_defs=extra_infos_defs.get(
                        'testSample', dict_type()),
                    dict_type=dict_type,
                    name_generator=name_generator)),
                ngs_libraries=dict_type(self._build_ngs_libraries(
                    extra_infos_defs=extra_infos_defs,
                    ngs_libraries_json=value.get(
                        'ngsLibraries', dict_type()),
                    dict_type=dict_type,
                    name_generator=name_generator)),
                dict_type=dict_type,
                name_generator=name_generator)
            yield (secondary_id, test_sample)

    def _build_ngs_libraries(
            self, extra_infos_defs, ngs_libraries_json, dict_type,
            name_generator):
        """Build models.NGSLibrary objects
        """
        for secondary_id, value in ngs_libraries_json.items():
            ngs_library = models.NGSLibrary(
                pk=value['pk'],
                disabled=value.get('disabled', False),
                secondary_id=secondary_id,
                extra_ids=value.get('extraIds', []),
                extra_infos=dict_type(self._build_extra_infos(
                    extra_infos=value.get('extraInfo', dict_type()),
                    extra_infos_defs=extra_infos_defs.get(
                        'ngsLibrary', dict_type()),
                    dict_type=dict_type,
                    name_generator=name_generator)),
                dict_type=dict_type,
                name_generator=name_generator)
            yield (secondary_id, ngs_library)
