# -*- coding: utf-8 -*-
"""Shortcuts for cancer sample sheets
"""

from collections import OrderedDict
from warnings import warn

from .base import (
    EXTRACTION_TYPE_DNA, EXTRACTION_TYPE_RNA,
    MissingDataEntity, MissingDataWarning, ShortcutSampleSheet,
    TestSampleShortcut, NGSLibraryShortcut)
from .generic import (GenericBioEntity, GenericBioSample)

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


#: Key value for "is tumor" flag
KEY_IS_TUMOR = 'isTumor'

#: Key value for "extraction type" value
KEY_EXTRACTION_TYPE = 'extractionType'


class CancerCaseSheetOptions:
    """Options for parsing cancer case sheets"""

    @classmethod
    def create_defaults(klass):
        return CancerCaseSheetOptions(
            allow_missing_normal=False,
            allow_missing_tumor=False)

    def __init__(self, *, allow_missing_normal, allow_missing_tumor):
        #: Allow missing normal sample, leads to empty pair list
        self.allow_missing_normal = allow_missing_normal
        #: Allow missing tumor sample, leads to empty pair list
        self.allow_missing_tumor = allow_missing_tumor

    def __str__(self):
        args = (self.allow_missing_normal, self.allow_missing_tumor)
        return 'CancerCaseSheetOptions({})'.format(', '.join(map(str, args)))

    def __repr__(self):
        return str(self)


class CancerCaseSheet(ShortcutSampleSheet):
    """Shortcut for "matched tumor/normal" view on bio-medical sample sheets

    Note that by default, at least one normal and one tumor sample must be
    given.  This can be changed by setting the ``options`` on creation.
    """

    def __init__(self, sheet, options=None):
        super().__init__(sheet)
        #: Configuration
        self.options = options or CancerCaseSheetOptions.create_defaults()
        #: List of donors in the sample sheet
        self.donors = list(self._iter_donors())
        #: List of primary matched tumor/normal sample pairs in the sheet
        self.primary_sample_pairs = list(self._iter_sample_pairs(True))
        #: List of all matched tumor/normal sample pairs in the sample sheet
        self.all_sample_pairs = list(self._iter_sample_pairs(False))
        #: Mapping of all sample pairs by name of primary DNA test sample
        self.all_sample_pairs_by_tumor_dna_test_sample = OrderedDict(
            (pair.tumor_sample.dna_test_sample.name, pair)
            for pair in self.all_sample_pairs
            if pair.tumor_sample and pair.tumor_sample.dna_test_sample)
        #: Mapping of all sample pairs by name of primary DNA library name
        self.all_sample_pairs_by_tumor_dna_ngs_library = OrderedDict(
            (pair.tumor_sample.dna_ngs_library.name, pair)
            for pair in self.all_sample_pairs
            if pair.tumor_sample.dna_ngs_library)
        #: Mapping of all sample pairs by name of primary RNA library name
        self.all_sample_pairs_by_tumor_rna_ngs_library = OrderedDict(
            (pair.tumor_sample.rna_ngs_library.name, pair)
            for pair in self.all_sample_pairs
            if pair.tumor_sample.rna_ngs_library)

    def _iter_donors(self):
        """Return iterator over the donors in the study"""
        for bio_entity in self.sheet.bio_entities.values():
            yield CancerDonor(self, bio_entity)

    def _iter_sample_pairs(self, only_primary_sample_pairs):
        """Return iterator over the matched tumor/normal pairs

        If ``only_primary_sample`` is ``True`` then only one pair per donor
        will be returned with the cancer sample marked as primary.  If this
        flag is ``False`` then one pair for each ``cancer`` sample will be
        returned.
        """
        for donor in self.donors:
            if only_primary_sample_pairs:
                yield donor.primary_pair
            else:
                yield from donor.all_pairs


class CancerMatchedSamplePair:
    """Represents a matched tumor/normal sample pair"""

    def __init__(self, donor, tumor_sample, normal_sample):
        #: The ``BioEntity`` from the sample sheet
        self.donor = donor
        #: Alias for ``self.donor``
        self.bio_entity = self.donor
        #: The ``CancerBioSample`` from the sample sheet
        self.tumor_sample = tumor_sample
        #: The ``CancerBioSample`` from the sample sheet
        self.normal_sample = normal_sample

    def __repr__(self):
        return 'CancerMatchedSamplePair({})'.format(', '.join(
            map(str, [self.donor, self.tumor_sample, self.normal_sample])))

    def __str__(self):
        return repr(self)


class CancerBioSample(GenericBioSample):
    """Represents one sample in a tumor/normal sample pair in the context
    of a matched Cancer tumor/normal study

    Currently, only NGS samples are supported and at least one DNA library is
    required.  This will change in the future
    """

    def __init__(self, shortcut_bio_entity, bio_sample):
        super().__init__(shortcut_bio_entity, bio_sample)
        #: The ``CancerDonor`` from the sample sheet
        self.donor = shortcut_bio_entity
        #: The primary DNA test sample
        self.dna_test_sample = self._get_primary_dna_test_sample()
        #: The primary RNA test sample, if any
        self.rna_test_sample = self._get_primary_rna_test_sample()
        #: The primary DNA NGS library for this sample
        self.dna_ngs_library = self._get_primary_dna_ngs_library()
        #: The primary RNA NGS library for this sample, if any
        self.rna_ngs_library = self._get_primary_rna_ngs_library()

    @property
    def is_tumor(self):
        """Whether or not the bio sample is cancerous"""
        return self.extra_infos[KEY_IS_TUMOR]

    def _get_primary_dna_test_sample(self):
        """Spider through ``self.bio_sample`` and return primary DNA test
        sample
        """
        sample = next(self._iter_all_test_samples(EXTRACTION_TYPE_DNA, True),
                      None)
        if sample:
            return TestSampleShortcut(self, sample, 'ngs_library')
        else:
            return None

    def _get_primary_rna_test_sample(self):
        """Spider through ``self.bio_sample`` and return primary RNA test
        sample, if any; ``None`` otherwise
        """
        sample = next(self._iter_all_test_samples(EXTRACTION_TYPE_RNA, True),
                      None)
        if sample:
            return TestSampleShortcut(self, sample, 'ngs_library')
        else:
            return None

    def _get_primary_dna_ngs_library(self):
        """Get primary DNA NGS library from self.dna_test_sample
        """
        if (self.dna_test_sample and
                self.dna_test_sample.test_sample.ngs_libraries):
            return NGSLibraryShortcut(self.dna_test_sample, next(iter(
                self.dna_test_sample.test_sample.ngs_libraries.values())))
        else:
            return None

    def _get_primary_rna_ngs_library(self):
        """Get primary RNA NGS library from self.rna_test_sample, if any
        """
        if (self.rna_test_sample and
                self.rna_test_sample.test_sample.ngs_libraries):
            return NGSLibraryShortcut(self.rna_test_sample, next(iter(
                self.rna_test_sample.test_sample.ngs_libraries.values())))
        else:
            return None

    def _iter_all_test_samples(self, ext_type, allow_none):
        """Yield all test samples with the given extraction type

        Require yielding of at least one unless ``allow_none``
        """
        yielded_any = False
        for test_sample in self.bio_sample.test_samples.values():
            if KEY_EXTRACTION_TYPE not in test_sample.extra_infos:
                raise MissingDataEntity(  # pragma: no cover
                    'Could not find "{}" flag in TestSample {}'.format(
                        KEY_EXTRACTION_TYPE, test_sample))
            elif test_sample.extra_infos[KEY_EXTRACTION_TYPE] == ext_type:
                yielded_any = True
                yield test_sample
        if not yielded_any and not allow_none:
            raise MissingDataEntity(  # pragma: no cover
                ('Could not find a TestSample with {} == {} for '
                 'BioSample {}'.format(
                     KEY_EXTRACTION_TYPE, ext_type, self.bio_sample)))

    def __repr__(self):
        return 'CancerBioSample({})'.format(', '.join(
            map(str, [self.bio_entity, self.bio_sample])))

    def __str__(self):
        return repr(self)


class CancerDonor(GenericBioEntity):
    """Represent a donor in a matched tumor/normal"""

    # Override to use cancer-specific bio sample class
    bio_sample_class = CancerBioSample

    def __init__(self, shortcut_sheet, bio_entity):
        super().__init__(shortcut_sheet, bio_entity)
        #: The primary ``CancerMatchedSamplePair``
        self.primary_pair = self._get_primary_pair()
        #: All tumor/normal pairs
        self.all_pairs = list(self._iter_all_pairs())

    def _get_primary_pair(self):
        """Return primary ``CancerMatchedSamplePair``"""
        try:
            return next(self._iter_all_pairs())
        except StopIteration:
            return None

    def _iter_all_pairs(self):
        """Iterate all tumor/normal pair"""
        normal_bio_sample = self._get_primary_normal_bio_sample()
        if normal_bio_sample:
            for tumor_bio_sample in self._iter_tumor_bio_samples():
                yield CancerMatchedSamplePair(
                    self, tumor_bio_sample, normal_bio_sample)

    def _get_primary_normal_bio_sample(self):
        """Return primary normal ``BioSample``

        Raises ``MissingDataEntity`` in the case of problems
        """
        for bio_sample in self.bio_samples.values():
            if KEY_IS_TUMOR not in bio_sample.extra_infos:
                raise MissingDataEntity(  # pragma: no cover
                    'Could not find "{}" flag in BioSample {}'.format(
                        KEY_IS_TUMOR, bio_sample))
            elif not bio_sample.extra_infos[KEY_IS_TUMOR]:
                return bio_sample
        # Having no normal sample is an error by default but this behaviour
        # can be switched off.
        tpl = 'Could not find primary normal sample for BioEntity {}'
        msg = tpl.format(self.bio_entity)
        if not self.sheet.options.allow_missing_normal:  # pragma: no cover
            raise MissingDataEntity(msg)
        else:
            warn(msg, MissingDataWarning)

    def _iter_tumor_bio_samples(self):
        """Return iterable over all cancer bio samples

        The order depends on the order in ``self.bio_samples``.  If
        the type of this attribute is an ordered dict, then the behaviour of
        this function is reproducible, otherwise it is not.

        Raises ``MissingDataEntity`` in the case of problems
        """
        yielded_any = False
        for bio_sample in self.bio_samples.values():
            if KEY_IS_TUMOR not in bio_sample.extra_infos:
                raise MissingDataEntity(  # pragma: no cover
                    'Could not find "{}" flag in BioSample {}'.format(
                        KEY_IS_TUMOR, bio_sample))
            elif bio_sample.extra_infos[KEY_IS_TUMOR]:
                yielded_any = True
                yield bio_sample
        if not yielded_any:
            # Having no tumor sample is an error by default but this behaviour
            # can be switched off.
            tpl = 'Could not find a BioSample with {} = true for BioEntity {}'
            msg = tpl.format(KEY_IS_TUMOR, self.bio_entity)
            if not self.sheet.options.allow_missing_tumor:
                raise MissingDataEntity(msg)  # pragma: no cover
            else:
                warn(msg, MissingDataWarning)

    def __repr__(self):
        return 'CancerDonor({})'.format(', '.join(map(
            str, [self.sheet, self.bio_entity])))

    def __str__(self):
        return repr(self)
