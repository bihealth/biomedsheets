# -*- coding: utf-8 -*-
"""Entrypoint for biomedsheets

The biomedsheets package provides Python library modules as well as an
executable for the various
"""

import argparse
import collections
import json
import logging
import os
import sys

import pkg_resources

from .io import SheetSchema, json_loads_ordered
from .io_tsv import (
    read_cancer_tsv_json_data, read_germline_tsv_json_data,
    read_generic_tsv_json_data)
from .ref_resolver import RefResolver
from .validation import SchemaValidator
from .shortcuts import (
    SHEET_TYPE_GERMLINE_VARIANTS, SHEET_TYPE_CANCER_MATCHED,
    SHEET_TYPE_GENERIC)

#: Choices for the TSV sheet type
CHOICES_SHEET_TYPE = (
    SHEET_TYPE_GERMLINE_VARIANTS, SHEET_TYPE_CANCER_MATCHED,
    SHEET_TYPE_GENERIC)

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class AppBase:
    """Base class for application, sub classed for each command"""

    def __init__(self, args):
        #: Parsed command line arguments
        self.args = args


class JsonSheetAppBase(AppBase):
    """Base class for working with sheets"""

    def __init__(self, args):
        super().__init__(args)
        #: SheetSchema from bundled json
        self.sheet_schema = self.load_sheet_schema()
        #: Validator for BioMed JSON schemas
        self.validator = SchemaValidator(self.sheet_schema)
        #: Sample sheet JSON
        self.sheet_json = self.load_sheet_json()
        #: Resolved JSON
        self.resolved_json = self.resolve_refs(self.sheet_json)

    def run(self):
        """Execute the command"""
        raise NotImplementedError('Abstract method called: override me!')

    def load_sheet_schema(self):
        """Load the bundled SheetSchema"""
        print('Loading bundled BioMed Sheet JSON Schema...', file=sys.stderr)
        return SheetSchema.load_from_string(pkg_resources.resource_stream(
            'biomedsheets', 'data/sheet.schema.json').read().decode())

    def load_sheet_json(self):
        """Load the sheet JSON file"""
        print('Loading sheet JSON from "{}"'.format(self.args.input),
              file=sys.stderr)
        try:
            with open(self.args.input, 'rt') as f:
                return json_loads_ordered(f.read())
        except FileNotFoundError:
            raise  # re-raise

    def get_lib_dirs(self):
        """Return list of paths to search for relative paths"""
        lib_dirs = list(self.args.lib_dir)
        lib_dirs.append(os.path.dirname(os.path.abspath(self.args.input)))
        return lib_dirs

    def resolve_refs(self, sheet_json):
        """Resolve "$ref" JSON pointers in sheet_json"""
        print('Resolving {{ "$ref": "..." }} in JSON...')
        resolver = RefResolver(
            lookup_paths=self.get_lib_dirs(),
            dict_class=collections.OrderedDict)
        return resolver.resolve('file://' + self.args.input, sheet_json)

    def validate_and_print_errors(self):
        errors = self.validator.validate(self.resolved_json)
        if errors:
            print('The following validation errors occured', file=sys.stderr)
            for error in errors:
                print(' - {}'.format(error), file=sys.stderr)
        return errors


class ValidateApp(JsonSheetAppBase):
    """App sub class for validation sub command"""

    def run(self):
        if self.validate_and_print_errors():
            return 1
        else:
            print('Sheet passed validation, congratulation!', file=sys.stderr)


class ExpandApp(JsonSheetAppBase):
    """App sub class for expanding "$ref" JSON pointers"""

    def run(self):
        json.dump(self.resolved_json, self.args.output, indent='  ')
        print('', file=self.args.output)


class ConvertApp(AppBase):
    """App sub class for converting shortcut TSV sheets to JSON sheets"""

    def run(self):
        funcs = {
            SHEET_TYPE_GERMLINE_VARIANTS: read_germline_tsv_json_data,
            SHEET_TYPE_CANCER_MATCHED: read_cancer_tsv_json_data,
            SHEET_TYPE_GENERIC: read_generic_tsv_json_data,
        }
        json.dump(
            funcs[self.args.type](self.args.input, self.args.input.name),
            self.args.output,
            indent='    ')
        print('', file=self.args.output)


def run(args):
    """Program entry point after parsing command line arguments"""
    apps = {
        'validate': ValidateApp,
        'expand': ExpandApp,
        'convert': ConvertApp,
    }
    return apps[args.subparser](args).run()


def main(argv=None):
    """Main program entry point, starts parsing command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--lib-dir', type=str, default=['.', os.getcwd()], action='append',
        help=('Base directorie for JSON file pointers, can be given '
              'multiple times'))

    subparsers = parser.add_subparsers(dest='subparser')

    parser_validate = subparsers.add_parser(
        'validate', help='Validate sample sheet JSON')
    parser_validate.add_argument(
        '-i', '--input', type=str, required=True,
        help='Path to BioMed Sheet (JSON or YAML) file')

    parser_expand = subparsers.add_parser(
        'expand', help='Expand "$ref" JSON pointers')
    parser_expand.add_argument(
        '-i', '--input', type=str, required=True,
        help='Path to BioMed Sheet (JSON or YAML) file')
    parser_expand.add_argument(
        '-o', '--output', type=argparse.FileType('wt'), default=sys.stdout,
        help='Path to output file, defaults to stdout')

    parser_convert = subparsers.add_parser(
        'convert', help='Convert shortcut TSV sheet to JSON sample sheet')
    parser_convert.add_argument(
        '-t', '--type', choices=CHOICES_SHEET_TYPE, required=True,
        help='Shortcut TSV sheet type')
    parser_convert.add_argument(
        '-i', '--input', type=argparse.FileType('rt'), required=True,
        help='Path to input TSV file')
    parser_convert.add_argument(
        '-o', '--output', type=argparse.FileType('wt'), default=sys.stdout,
        help='Path to output file, defaults to stdout')

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    args = parser.parse_args(argv)
    if not args.subparser:
        parser.print_usage()
        return 1
    return run(args)


if __name__ == '__main__':
    sys.exit(main())
