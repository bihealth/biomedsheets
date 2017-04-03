# -*- coding: utf-8 -*-
"""Tests for the ``__main__`` module

Currently, these are smoke tests only and we should test more stringently
"""

import os

import pytest

from biomedsheets.__main__ import main


@pytest.fixture
def path_json_sheet_cancer():
    """Return path to cancer JSON sheet"""
    return os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'data', 'example_cancer.json')


@pytest.fixture
def path_tsv_sheet_cancer():
    """Return path to cancer TSV sheet"""
    return os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'data', 'example_cancer_matched.tsv')


@pytest.fixture
def path_tsv_sheet_germline():
    """Return path to germline TSV sheet"""
    return os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'data', 'example_germline_variants.tsv')


def test_validate_cancer_json(path_json_sheet_cancer):
    assert not main(['validate', '-i', path_json_sheet_cancer])


def test_expand_cancer_json(path_json_sheet_cancer):
    assert not main(['expand', '-i', path_json_sheet_cancer])


def test_convert_cancer_tsv(path_tsv_sheet_cancer):
    assert not main(
        ['convert', '-t', 'cancer_matched', '-i', path_tsv_sheet_cancer])


def test_convert_germline_tsv(path_tsv_sheet_germline):
    assert not main(
        ['convert', '-t', 'germline_variants', '-i', path_tsv_sheet_germline])
