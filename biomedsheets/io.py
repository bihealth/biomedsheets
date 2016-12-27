# -*- coding: utf-8 -*-
"""Code for reading and writing BioMed Sheets from/to file-like objects

Optionally, objects can be validated before reading/writing.
"""

import collections
import json

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


def json_loads_ordered(s):
    """Helper function to load JSON using OrderedDict for object pairs"""
    return json.loads(s, object_pairs_hook=collections.OrderedDict)


class SheetSchema:
    """Programmatic access to the bundled BioMed Schema JSON file"""

    @classmethod
    def load_from_string(self, s):
        """Load schema from JSON string ``s``"""
        return SheetSchema(json_loads_ordered(s))

    def __init__(self, parsed_json):
        #: parsed JSON that is wrapped by schema
        self.parsed_json = parsed_json
