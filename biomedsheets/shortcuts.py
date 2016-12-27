# -*- coding: utf-8 -*-
"""Python classes for enabling shortcut views on the biomedical sheet

Note that these shortcuts rely on the following assumptions.  These
assumptions are quite strong but make sense in clinical context.  Also, they
enforce a sensible streamlining of the high-throughput biomedical assay
structure which is the case for the interesting studies anyway.

- each shortcut sheet only uses one data type (e.g., WES, WGS, or mass-spec
  data)
- in the case of rare disease studies, only the first active bio and test
  sample and NGS library need to be considered
- in the case of cancer studies, only the first active test sample and NGS
  library are of interesting
- both one and multiple test samples can be of study, e.g., in the case
  of considering multiple parts of a larger tumor or metastesis

This all is to facilitate the automatic processing in pipelines.  Of course,
more assays can be combined by loading the results in a downstream step.
These downstream steps can then combine the information in any fashion they
see fit and build larger, more complex systems out of the simpler building
blocks that this module is meant for.
"""

from . import models

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Token for identifying a rare disease sequencing experiment
RARE_DISEASE = 'rare_disease'
#: Token for identifying a cancer matched tumor/normal study
CANCER_MATCHED = 'cancer_matched'
#: Token for identifying a generic experiment
GENERIC_EXPERIMENT = 'generic_experiment'
#: Known sheet types with shortcuts
SHEET_TYPES = (RARE_DISEASE, CANCER_MATCHED, GENERIC_EXPERIMENT)

# TODO: the major thing here that is missing in the pre-selection of the
#       part after TestSample, e.g., WES/RNA-seq/WGS library or HPLC-MS


class InvalidSelector(Exception):
    """Raised in the case of an invalid ``TestSample`` child type"""


class MissingDataEntity(Exception):
    """Raised if the given data entity is not known"""


class TestSampleShortcut:
    """When navigating with the ``biomedsheets.shortcuts`` through the
    sheets, this is the type that you end up instead of raw ``TestSample``
    objects

    Objects of this class are pre-configured with a specific ``TestSample``
    child type (e.g., NGS library or MSProteinPool) where the primary
    active will be picked.
    """

    def __init__(self, test_sample, selector):
        #: Raw ``TestSample``
        self.test_sample = test_sample
        # Check selector for being valid
        if selector not in models.TEST_SAMPLE_CHILDREN:
            raise InvalidSelector(
                'Invalid test sample selector {}'.format(selector))
        #: Selector for ``TestSample`` children
        self.selector = selector
        #: The selected ``TestSample`` child
        self.data_entity = self._get_data_entity()

    def _get_data_entity(self):
        """Return ``TestSample`` child or raise an exception"""
        attr_lst = None or []  # TODO
        for entity in attr_lst:
            if not entity.disabled:
                return entity
        raise MissingDataEntity(
            'Could not find data entity for type {} in {}'.format(
                self.selector, self.test_sample))


class RareDiseaseCaseSheet:
    """Shortcut for "rare disease" view on bio-medical sample sheets"""

    def __init__(self, sheet):
        #: The wrapped ``Sheet``
        self.sheet = sheet
        # TODO: construct shortcuts into the pedigree


class CancerCaseSheet:
    """Shortcut for "matched tumor/normal" view on bio-medical sample sheets
    """

    def __init__(self, sheet):
        #: The wrapped ``Sheet``
        self.sheet = sheet
        #: List of donors in the sample sheet
        self.donors = list(self._iter_donors)
        #: List of matched tumor/normal sample pairs in the sample sheet
        self.sample_pairs = list(self._iter_sample_pairs)

    def _iter_donors(self):
        """Return iterator over the donors in the study"""
        raise NotImplementedError('Implement me!')

    def _iter_sample_pairs(self, only_primary_sample=True):
        """Return iterator over the matched tumor/normal pairs

        If ``only_primary_sample`` is ``True`` then only one pair per donor
        will be returned with the cancer sample marked as primary.  If this
        flag is ``False`` then one pair for each ``cancer`` sample will be
        returned.
        """
        raise NotImplementedError('Implement me!')


class CancerDonor:
    """Represent a donor in a matched tumor/normal"""

    def __init__(self, bio_entity):
        #: The ``BioEntity`` from the sample sheet
        self.bio_entity = bio_entity
        #: The primary ``CancerMatchedSamplePair``
        self.primary_pair = self._get_primary_pair()
        #: All tumor/normal pairs
        self.all_pairs = list(self._iter_all_pairs())

    def _get_primary_pair(self):
        """Return primary ``CancerMatchedSamplePair``"""
        raise NotImplementedError('Implement me!')

    def _iter_all_pairs(self):
        """Iterate all tumor/normal pair"""
        raise NotImplementedError('Implement me!')


class CancerMatchedSamplePair:
    """Represents a matched tumor/normal sample pair"""

    def __init__(self, donor, tumor_sample, normal_sample):
        #: The ``BioEntity`` from the sample sheet
        self.donor = donor
        #: The ``CancerSample`` from the sample sheet
        self.tumor_sample = tumor_sample
        #: The ``CancerSample`` from the sample sheet
        self.normal_sample = normal_sample


class CancerSample:
    """Represents one sample in a tumor/normal sample pair in the context
    of a matched Cancer tumor/normal study
    """

    def __init__(self, bio_sample):
        #: The ``BioSample`` from the sample sheet
        self.bio_sample = bio_sample


class GenericExperimentSampleSheet:
    """Shortcut of a generic experiment sample sheet"""

    def __init__(self, sheet):
        #: The wrapped ``Sheet``
        self.sheet = sheet
        #: List of all primary ``TestSample`` of the assumed type
        self.test_samples = list(self._iter_test_samples())

    def _iter_test_samples(self):
        """Iterate over the test samples of the selected type that"""
