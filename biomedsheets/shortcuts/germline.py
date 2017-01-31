# -*- coding: utf-8 -*
"""Shortcuts for rare germline sample sheets
"""

from .base import (ShortcutSampleSheet)

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class GermlineCaseSheet(ShortcutSampleSheet):
    """Shortcut for "germline" view on bio-medical sample sheets"""

    def __init__(self, sheet):
        super().__init__(sheet)

