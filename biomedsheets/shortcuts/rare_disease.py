# -*- coding: utf-8 -*
"""Shortcuts for rare disease sample sheets
"""

from .base import (ShortcutSampleSheet)

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class RareDiseaseCaseSheet(ShortcutSampleSheet):
    """Shortcut for "rare disease" view on bio-medical sample sheets"""

    def __init__(self, sheet):
        super().__init__(sheet)

