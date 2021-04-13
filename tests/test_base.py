# -*- coding: utf-8 -*-
"""Tests for base module"""


import pytest

from biomedsheets.shortcuts.base import (
    InvalidSelector,
    MissingDataEntity
)


def test_invalid_selection_exception():
    """Tests InvalidSelector raised."""
    error_msg = "Raised InvalidSelector"
    with pytest.raises(Exception) as exec_info:
        raise InvalidSelector(error_msg)
    assert exec_info.value.args[0] == error_msg


def test_missing_data_entity_exception():
    """Tests MissingDataEntity raised."""
    error_msg = "Raised MissingDataEntity"
    with pytest.raises(Exception) as exec_info:
        raise MissingDataEntity(error_msg)
    assert exec_info.value.args[0] == error_msg
