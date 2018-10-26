# -*- coding: utf-8 -*
"""Shortcuts for rare germline sample sheets
"""

from collections import OrderedDict
from warnings import warn

from .base import (
    EXTRACTION_TYPE_DNA, EXTRACTION_TYPE_RNA, MissingDataEntity,
    ShortcutSampleSheet, BioSampleShortcut, TestSampleShortcut,
    NGSLibraryShortcut, MissingDataWarning)
from .generic import GenericBioEntity
from ..union_find import UnionFind

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

# TODO: need selector or WGS/WES data somehow in case both are present.

#: Key value for "extraction type" value
KEY_EXTRACTION_TYPE = 'extractionType'

#: Key value for the "is affected" flag
KEY_IS_AFFECTED = 'isAffected'

#: Key value for the "father PK" value
KEY_FATHER_PK = 'fatherPk'

#: Key value for the "mother PK" value
KEY_MOTHER_PK = 'motherPk'

#: Key value for "sex".
KEY_SEX = 'sex'


class Pedigree:
    """Class for accessing information in a pedigree

    The individuals are represented by :py:class:`GermlineDonor` objects.

    Note that the shortcut members are set upon creation.  When members are
    modified after the construction, the ``update_shortcuts()`` method must
    be called.
    """

    def __init__(self, donors=None, index=None):
        #: Members of the pedigree
        self.donors = list(donors or [])
        #: Index patient in the pedigree, there can only be one, even if
        #: there are multiple affected individuals.  Usually, the first
        #: affected patient in a study is used
        self.index = index
        #: All affected individuals
        self.affecteds = []
        #: Founders in the pedigree, assumed to be unrelated
        self.founders = []
        #: Mapping from individual name to donor individual
        self.name_to_donor = {}
        #: Mapping from individual pk to donor individual
        self.pk_to_donor = {}
        #: Mapping from individual secondary_id to donor individual
        self.secondary_id_to_donor = {}
        # Initialize the shortcuts
        self.update_shortcuts()

    @property
    def member_count(self):
        """Return number of members in the pedigree"""
        return len(self.donors)

    def update_shortcuts(self):
        """Update the shortcut members"""
        if len(self.donors) == 1:
            # For singletons, use the single individual as index regardless
            # of affection state.  This allows the usage of cancer sample
            # sheets in variant_calling.
            self.affecteds = []
            self.index = self.donors[0]
        else:
            self.affecteds = [d for d in self.donors if d.is_affected]
            if self.index is None and self.affecteds:
                self.index = self.affecteds[0]
            elif self.index is None:  # fallback to first in list
                self.index = self.donors[0]
        self.founders = [d for d in self.donors if d.is_founder]
        self.name_to_donor = OrderedDict([(d.name, d) for d in self.donors])
        self.pk_to_donor = OrderedDict([(str(d.pk), d) for d in self.donors])
        self.secondary_id_to_donor = OrderedDict([
            (d.secondary_id, d) for d in self.donors])

    def __repr__(self):
        return 'Pedigree({})'.format(', '.join(map(str, [
            self.donors, self.index])))

    def __str__(self):
        return repr(self)


def _append_pedigree_to_ped(pedigree, f):
    family = 'FAM_' + pedigree.index.name
    for donor in pedigree.donors:
        affected = {
            'affected': '2', 'unaffected': '1', 'unknown': '0'
        }[donor.extra_infos.get(KEY_IS_AFFECTED, 'unknown')]
        sex = {'male': '1', 'female': '2', 'unknown': '0'}[
            donor.extra_infos.get(KEY_SEX, 'unknown')]
        father = '0'
        if donor.father_pk:
            if hasattr(pedigree.pk_to_donor[donor.father_pk],
                       'dna_ngs_library'):
                donor_father = pedigree.pk_to_donor[donor.father_pk]
                if donor_father.dna_ngs_library is None:
                    father = donor_father.name
                else:
                    father = donor_father.dna_ngs_library.name
        mother = '0'
        if donor.mother_pk:
            if hasattr(pedigree.pk_to_donor[donor.mother_pk],
                       'dna_ngs_library'):
                donor_mother = pedigree.pk_to_donor[donor.mother_pk]
                if donor_mother.dna_ngs_library is None:
                    mother = donor_mother.name
                else:
                    mother = donor_mother.dna_ngs_library.name
        if hasattr(donor, 'dna_ngs_library'):
            if donor.dna_ngs_library is None:
                name = donor.name
            else:
                name = donor.dna_ngs_library.name
            print('\t'.join(
                (family, name, father, mother, sex, affected)), file=f)


def write_pedigree_to_ped(pedigree, path):
    with open(path, 'wt') as f:
        _append_pedigree_to_ped(pedigree, f)


def write_pedigrees_to_ped(pedigrees, path):
    with open(path, 'wt') as f:
        for pedigree in pedigrees:
            _append_pedigree_to_ped(pedigree, f)


class Cohort:
    """Class for accessing information about a set of :py:class:`Pedigree`:
    objects.

    Pedigrees are assumed to not overlap.

    Note that the shortcut members are set upon creation.  When pedigrees are
    modified after the construction, the ``update_shortcuts()`` method must
    be called.
    """

    def __init__(self, pedigrees=None):
        #: The pedigrees in the cohort
        self.pedigrees = list(pedigrees or [])
        #: List of all index individuals of all pedigrees
        self.indices = []
        #: List of all affected individuals of all pedigrees
        self.affecteds = []
        #: Mapping from individual name to pedigree
        self.name_to_pedigree = {}
        #: Mapping from individual pk to pedigree
        self.pk_to_pedigree = {}
        #: Mapping from individual secondary_id to pedigree
        self.secondary_id_to_pedigree = {}
        #: Mapping from individual name to donor individual
        self.name_to_donor = {}
        #: Mapping from individual pk to donor individual
        self.pk_to_donor = {}
        #: Mapping from individual secondary_id to donor individual
        self.secondary_id_to_donor = {}
        # Initialize the shortcuts
        self.update_shortcuts()

    @property
    def member_count(self):
        """Return number of members in the cohort"""
        return sum(p.member_count for p in self.pedigrees)

    @property
    def pedigree_count(self):
        """Return number of pedigrees in the cohort"""
        return len(self.pedigrees)

    def update_shortcuts(self):
        """Update the shortcut members"""
        # Re-build lists of index and affected individuals
        self.indices = [p.index for p in self.pedigrees]
        self.affecteds = sum((p.affecteds for p in self.pedigrees), [])
        # Re-build mappings
        self.name_to_pedigree = {}
        self.pk_to_pedigree = {}
        self.secondary_id_to_pedigree = {}
        self.name_to_donor = {}
        self.pk_to_donor = {}
        self.secondary_id_to_donor = {}
        for pedigree in self.pedigrees:
            # Update {name,pk,secondary_id} to pedigree mapping
            self._checked_update(
                self.name_to_pedigree,
                {d.name: pedigree for d in pedigree.donors}, 'name')
            self._checked_update(
                self.pk_to_pedigree,
                {d.pk: pedigree for d in pedigree.donors}, 'pk')
            self._checked_update(
                self.secondary_id_to_pedigree,
                {d.secondary_id: pedigree for d in pedigree.donors},
                'secondary id')
            # Update {name,pk,secondary_id} to donor mapping
            self._checked_update(
                self.name_to_donor,
                {d.name: d for d in pedigree.donors}, 'name')
            self._checked_update(
                self.pk_to_donor, {d.pk: d for d in pedigree.donors}, 'pk')
            self._checked_update(
                self.secondary_id_to_donor, {
                    d.secondary_id: d for d in pedigree.donors},
                'secondary id')

    def _checked_update(self, dest, other, msg_token):
        """Check overlap of keys between ``dest`` and ``other``, update and
        return dest

        In case of error, use ``msg_token`` for exception message.
        """
        overlap = set(dest.keys()) & set(other.keys())
        if overlap:
            tpl = ('Duplicate {}s when building '
                   'cohort shortcuts: {}')  # pramga: no cover
            raise ValueError(  # pramga: no cover
                tpl.format(msg_token, list(sorted(overlap))))
        dest.update(other)
        return dest


class CohortBuilder:
    """Helper class for building a :py:class:`Cohort` object from an iterable
    of :py:class:`GermlineDonor` objects

    Also initialize the internal father and mother attributes of
    :py:class:`GermlineDonor`
    """

    def __init__(self, donors):
        #: Iterable of :py:class:`GermlineDonor` objects
        self.donors = list(donors)

    def run(self):
        """Return :py:class:`Cohort` object with :py:class:`Pedigree` sub
        structure
        """
        cohort = Cohort(self._yield_pedigrees())
        for pedigree in cohort.pedigrees:
            for donor in pedigree.donors:
                if donor.father_pk:
                    donor._father = cohort.pk_to_donor[int(donor.father_pk)]
                if donor.mother_pk:
                    donor._mother = cohort.pk_to_donor[int(donor.mother_pk)]
        return cohort

    def _yield_pedigrees(self):
        """Yield Pedigree objects built from self.donors"""
        # Use Union-Find data structure for gathering pedigree donors
        union_find = UnionFind()
        for donor in self.donors:
            for parent_pk in (
                    pk for pk in (donor.father_pk, donor.mother_pk) if pk):
                # String conversion is necessary because "fatherPk" and
                # "motherPk" are given with type "str" in std_fields.json
                union_find.union(str(donor.pk), parent_pk)
        # Partition the donors
        partition = OrderedDict()
        for donor in self.donors:
            partition.setdefault(union_find[str(donor.pk)], []).append(donor)
        # Construct the pedigrees
        for ped_donors in partition.values():
            yield Pedigree(ped_donors)


class GermlineDonor(GenericBioEntity):
    """Represent a donor in a germline study"""

    def __init__(self, shortcut_sheet, bio_entity):
        super().__init__(shortcut_sheet, bio_entity)
        # ``GermlineDonor`` object for father, access via property, set in
        # ``CohortBuilder``
        self._father = None
        # ``GermlineDonor`` object for mother, access via property, set in
        # ``CohortBuilder``
        self._mother = None
        #: The primary bio sample with DNA
        self.dna_bio_sample = self._get_primary_dna_bio_sample()
        #: The primary bio sample with RNA, if any
        self.rna_bio_sample = self._get_primary_rna_bio_sample()
        #: The primary DNA test sample
        self.dna_test_sample = self._get_primary_dna_test_sample()
        #: The primary RNA test sample, if any
        self.rna_test_sample = self._get_primary_rna_test_sample()
        #: The primary DNA NGS library for this sample
        self.dna_ngs_library = self._get_primary_dna_ngs_library()
        #: The primary RNA NGS library for this sample, if any
        self.rna_ngs_library = self._get_primary_rna_ngs_library()

    @property
    def is_affected(self):
        """Return whether or not the donor is affected"""
        return self.extra_infos.get(
            KEY_IS_AFFECTED, 'unaffected') == 'affected'

    @property
    def father_pk(self):
        """Return PK of father or ``None``"""
        return self.extra_infos.get(KEY_FATHER_PK, None)

    @property
    def mother_pk(self):
        """Return PK of mother or ``None``"""
        return self.extra_infos.get(KEY_MOTHER_PK, None)

    @property
    def father(self):
        """Return mother ``GermlineDonor`` object or ``None``"""
        if not self._father and self.father_pk:
            raise AttributeError(
                'Father object not yet set, although PK available.  '
                'Not processed through CohortBuilder?')
        return self._father

    @property
    def mother(self):
        """Return mother ``GermlineDonor`` object or ``None``"""
        if not self._mother and self.mother_pk:
            raise AttributeError(
                'Mother object not yet set, although PK available.  '
                'Not processed through CohortBuilder?')
        return self._mother

    @property
    def is_founder(self):
        """Return whether is founder, i.e., has neither mother nor father"""
        return (not self.father_pk) and (not self.mother_pk)

    def _get_primary_dna_bio_sample(self):
        """Spider through ``self.bio_entity`` and return primary bio sample
        """
        for sample in self._iter_all_bio_samples(EXTRACTION_TYPE_DNA, True):
            if not sample.extra_infos.get('isTumor', False):
                return BioSampleShortcut(self, sample, 'ngs_library')
        return None

    def _get_primary_rna_bio_sample(self):
        """Spider through ``self.bio_entity`` and return primary bio sample
        with RNA data, if any; ``None`` otherwise
        """
        for sample in self._iter_all_bio_samples(EXTRACTION_TYPE_RNA, True):
            if not sample.extra_infos.get('isTumor', False):
                return BioSampleShortcut(self, sample, 'ngs_library')
        return None

    def _get_primary_dna_test_sample(self):
        """Spider through ``self.bio_entity`` and return primary DNA test sample
        """
        if (self.dna_bio_sample and
                self.dna_bio_sample.bio_sample.test_samples):
            return TestSampleShortcut(self.dna_bio_sample, next(iter(
                self.dna_bio_sample.bio_sample.test_samples.values())),
                'ngs_library')
        else:
            return None

    def _get_primary_rna_test_sample(self):
        """Spider through ``self.bio_entity`` and return primary RNA
        testsample, if any; ``None`` otherwise
        """
        if (self.rna_bio_sample and
                self.rna_bio_sample.bio_sample.test_samples):
            return TestSampleShortcut(self.rna_bio_sample, next(iter(
                self.rna_bio_sample.bio_sample.test_samples.values())),
                'ngs_library')
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

    def _iter_all_bio_samples(self, ext_type, allow_none):
        """Yield all bio samples with a test sample of the given extraction
        type

        Require yielding of at least one unless ``allow_none``
        """
        yielded_any = False
        for bio_sample in self.bio_entity.bio_samples.values():
            for test_sample in bio_sample.test_samples.values():
                if KEY_EXTRACTION_TYPE not in test_sample.extra_infos:
                    raise MissingDataEntity(
                        'Could not find "{}" flag in TestSample {}'.format(
                            KEY_EXTRACTION_TYPE, test_sample))
                elif test_sample.extra_infos[KEY_EXTRACTION_TYPE] == ext_type:
                    yielded_any = True
                    yield bio_sample
                    break  # each bio_sample only once
        if not yielded_any and not allow_none:
            msg = 'Could not find a TestSample with {} == {} for BioEntity {}'
            raise MissingDataEntity(msg.format(
                KEY_EXTRACTION_TYPE, ext_type, self.bio_entity))

    def __repr__(self):
        return 'GermlineDonor({})'.format(', '.join(map(
            str, [self.sheet, self.bio_entity])))

    def __str__(self):
        return repr(self)


class GermlineCaseSheet(ShortcutSampleSheet):
    """Shortcut for "germline" view on bio-medical sample sheets"""

    bio_entity_class = GermlineDonor

    def __init__(self, sheet):
        super().__init__(sheet)
        #: List of donors in the sample sheet
        self.donors = list(self._iter_donors())
        #: :py:class:`Cohort` object with the pedigrees and donors built from
        #: the sample sheet
        self.cohort = CohortBuilder(self.donors).run()
        #: Mapping from index DNA NGS library name to pedigree
        self.index_ngs_library_to_pedigree = OrderedDict(
            self._index_ngs_library_to_pedigree())
        #: Mapping from any DNA NGS library name in pedigree to pedigree
        self.donor_ngs_library_to_pedigree = OrderedDict([
            (donor.dna_ngs_library.name, pedigree)
            for pedigree in self.cohort.pedigrees
            for donor in pedigree.donors if donor.dna_ngs_library])
        #: Mapping from DNA NGS library name to donor
        self.index_ngs_library_to_donor = OrderedDict([
            (donor.dna_ngs_library.name, donor)
            for donor in self.donors if donor.dna_ngs_library])
        #: Mapping from library name to object
        self.library_name_to_library = OrderedDict(
            self._library_name_to_library())

    def _iter_donors(self):
        """Return iterator over the donors in the study"""
        for bio_entity in self.sheet.bio_entities.values():
            yield GermlineDonor(self, bio_entity)

    def _index_ngs_library_to_pedigree(self):
        """Build mapping from NGS library name to pedigree"""
        for pedigree in self.cohort.pedigrees:
            if not pedigree.index:
                raise ValueError(  # pragma: no cover
                    'Found pedigree without index! {}'.format(pedigree))
            if not pedigree.index.dna_ngs_library:
                # Warn if pedigree does not have a NGS library
                tpl = 'Pedigree index has no DNA library! {}/{}'
                msg = tpl.format(pedigree.index, pedigree)
                warn(msg, MissingDataWarning)
                continue
            yield pedigree.index.dna_ngs_library.name, pedigree

    def _library_name_to_library(self):
        """Yield mapping from library name to library"""
        for donor in self.donors:
            for bio_sample in donor.bio_samples.values():
                for test_sample in bio_sample.test_samples.values():
                    for ngs_library in test_sample.ngs_libraries.values():
                        yield ngs_library.name, ngs_library
