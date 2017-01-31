# -*- coding: utf-8 -*-
"""Tests for loading the compressed germline TSV file
"""

import io
import json
import textwrap

import pytest

from biomedsheets import io_tsv

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def tsv_sheet_germline_header():
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema          germline_variants
    schema_version  v1
    title           Example germline study
    description     The study has two patients, P001 has one tumor sample, P002 has two

    [Data]
    patientName\tfatherName\tmotherName\tsex\taffected\tfolderName\thpoTerms
    12-345\t12-346\t12-347\tM\tY\t12-345\tHP:0009946,HP:0009899
    12-348\t12-346\t12-347\tM\tN\t12-348
    12-346\t.\t.\tM\tN\t.
    12-347\t.\t.\tF\tN\t12-347
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_germline_no_header():
    """Tumor TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    patientName\tfatherName\tmotherName\tsex\taffected\tfolderName\thpoTerms
    12-345\t12-346\t12-347\tM\tY\t12-345\tHP:0009946,HP:0009899
    12-348\t12-346\t12-347\tM\tN\t12-348
    12-346\t.\t.\tM\tN\t.
    12-347\t.\t.\tF\tN\t12-347
    """.lstrip()))
    return f


# Expected value for the germline sheet JSON with header
EXPECTED_GERMLINE_SHEET_JSON_HEADER = r"""
""".lstrip()

# Expected value for the germline sheet JSON without header
EXPECTED_GERMLINE_SHEET_JSON_NO_HEADER = r"""
""".lstrip()


def test_read_germline_sheet_header(tsv_sheet_germline_header):
    sheet = io_tsv.read_germline_tsv_sheet(tsv_sheet_germline_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_germline_sheet_no_header(tsv_sheet_germline_no_header):
    sheet = io_tsv.read_germline_tsv_sheet(tsv_sheet_germline_no_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_NO_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_tumor_json_header(tsv_sheet_germline_header):
    sheet_struc = io_tsv.read_germline_tsv_json_data(tsv_sheet_germline_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_tumor_json_no_header(tsv_sheet_germline_no_header):
    sheet_struc = io_tsv.read_germline_tsv_json_data(tsv_sheet_germline_no_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_NO_HEADER == json.dumps(
        sheet_struc, indent='    ')
