# -*- coding: utf-8 -*-
"""Python code for the validation of BioMed Schemas
"""

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class SchemaValidator:
    """Main validation driver for JSON documents"""

    def __init__(self, sheet_schema):
        #: ``SheetShema`` to use for the validation
        self.sheet_schema = sheet_schema

    def validate(self, resolved_json):
        """Perform validation

        resolved_json JSON document in Python representation
        """
        pass
