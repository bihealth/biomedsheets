# -*- coding: utf-8 -*-
"""Tests for the reference resolving code."""

import json
import os

from biomedsheets.ref_resolver import RefResolver


def test_included():
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')
    resolver = RefResolver([path])
    path_base = path + '/base.json'
    with open(path_base, 'rt') as file_json:
        data_base = json.load(file_json)
    result = resolver.resolve('file://' + path_base, data_base)
    expected = {
        'key1': 'value.base',
        'key2': 'value.included1',
        'key3': 'value.included2',
        'nested': {
            'key1': 1,
            'key2': 2,
            'key3': 3,
        },
        'more': {
            'key': 'value',
        },
    }
    assert expected == result
