# -*- coding: utf-8 -*-
"""Shortcuts for generic sample sheets
"""

from collections import OrderedDict

from .base import (ShortcutMixin)
from .base import (ShortcutSampleSheet)

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


class GenericSampleSheet(ShortcutSampleSheet):
    """Shortcut for "rare disease" view on bio-medical sample sheets"""

    def __init__(self, sheet):
        super().__init__(sheet)
        #: Generic wrapper BioEntity objects
        self.bio_entities = OrderedDict(self._build_bio_entities())
        #: List of all NGS libraries
        self.all_ngs_libraries = []
        #: List of the primary NGS libraries for each bio sample
        self.primary_ngs_libraries = []
        # Build the shortcuts
        self._build_shortcuts()

    def _build_bio_entities(self):
        """Build GenericBioEntity objects for ``self.sheet``"""
        for name, bio_entity in self.sheet.bio_entities.items():
            yield name, GenericBioEntity(self, bio_entity)

    def _build_shortcuts(self):
        # Build self.{all,primary}_ngs_libraries
        for bio_entity in self.bio_entities.values():
            for bio_sample in bio_entity.bio_samples.values():
                primary = True
                for test_sample in bio_sample.test_samples.values():
                    for ngs_library in (
                            test_sample.ngs_libraries.values()):
                        if ngs_library.disabled:
                            continue
                        self.all_ngs_libraries.append(ngs_library)
                        if primary:
                            self.primary_ngs_libraries.append(ngs_library)
                            primary = False


class GenericNGSLibrary(ShortcutMixin):
    """Shortcut wrapper for NGS library in generic sample sheet"""

    def __init__(self, shortcut_test_sample, ngs_library):
        #: Parent GenericTestSample
        self.test_sample = shortcut_test_sample
        #: Parent object; for ShortcutMixin
        self.parent = shortcut_test_sample
        #: Wrapped object
        self.wrapped = ngs_library
        #: Wrapped NGSLibrary
        self.ngs_library = ngs_library


class GenericTestSample(ShortcutMixin):
    """Shortcut wrapper for test sample in generic sample sheet"""

    #: Type to use for creating bio samples
    ngs_library_class = GenericNGSLibrary

    def __init__(self, shortcut_bio_sample, test_sample):
        #: Parent GenericBioSample
        self.bio_sample = shortcut_bio_sample
        #: Parent object; for ShortcutMixin
        self.parent = shortcut_bio_sample
        #: Wrapped object
        self.wrapped = test_sample
        #: Wrapped TestSample
        self.test_sample = test_sample
        #: Shortcut to NGSLibrary objects
        self.ngs_libraries = OrderedDict(self._build_ngs_libraries())

    def _build_ngs_libraries(self):
        """BuildGenericNGSLibrary objects from
        ``self.test_sample.ngs_libraries"""
        for name, ngs_library in self.test_sample.ngs_libraries.items():
            yield name, self.__class__.ngs_library_class(self, ngs_library)


class GenericBioSample(ShortcutMixin):
    """Shortcut wrapper for bio sample in generic sample sheet"""

    #: Type to use for creating bio samples
    test_sample_class = GenericTestSample

    def __init__(self, shortcut_bio_entity, bio_sample):
        #: Parent GenericBioEntity
        self.bio_entity = shortcut_bio_entity
        #: Parent object; for ShortcutMixin
        self.parent = shortcut_bio_entity
        #: Wrapped object
        self.wrapped = bio_sample
        #: Wrapped BioSample
        self.bio_sample = bio_sample
        #: Shortcut BioSample objects
        self.test_samples = OrderedDict(self._build_test_samples())

    def _build_test_samples(self):
        """Build GenericTestSample objects for ``self.bio_sample.test_samples``
        """
        for name, test_sample in self.bio_sample.test_samples.items():
            yield name, self.__class__.test_sample_class(self, test_sample)


class GenericBioEntity(ShortcutMixin):
    """Shortcut wrapper for bio entity in generic sample sheet"""

    #: Type to use for creating bio samples
    bio_sample_class = GenericBioSample

    def __init__(self, shortcut_sheet, bio_entity):
        #: Parent GenericSampleSheet
        self.sheet = shortcut_sheet
        #: Parent object; for ShortcutMixin
        self.parent = None
        #: Wrapped object; for ShortcutMixin
        self.wrapped = bio_entity
        #: Wrapped BioEntity
        self.bio_entity = bio_entity
        #: Shortcut BioSample objects
        self.bio_samples = OrderedDict(self._build_bio_samples())

    def _build_bio_samples(self):
        """Build GenericBioSample objects for ``self.bio_entity.bio_samples``
        """
        for name, bio_sample in self.bio_entity.bio_samples.items():
            yield name, self.__class__.bio_sample_class(self, bio_sample)
