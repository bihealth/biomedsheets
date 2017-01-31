# -*- coding: utf-8 -*
"""Shortcuts for rare germline sample sheets
"""

from collections import OrderedDict

from .base import (
    EXTRACTION_TYPE_DNA, EXTRACTION_TYPE_RNA,
    MissingDataEntity, ShortcutSampleSheet, TestSampleShortcut,
    NGSLibraryShortcut)
from .generic import GenericBioEntity
from ..union_find import UnionFind

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Key value for "extraction type" value
KEY_EXTRACTION_TYPE = 'extractionType'

#: Key value for the "is affected" flag
KEY_IS_AFFECTED = 'isAffected'

#: Key value for the "father PK" value
KEY_FATHER_PK = 'fatherPK'

#: Key value for the "mother PK" value
KEY_MOTHER_PK = 'motherPK'


class Pedigree:
    """Class for accessing information in a pedigree

    The individuals are represented by :py:class:`GermlineDonor` objects.

    Note that the shortcut members are set upon creation.  When members are modified after the
    construction, the ``update_shortcuts()`` method must be called.
    """

    def __init__(self, donors=None, index=None):
        #: Members of the pedigree
        self.donors = list(donors or [])
        #: Index patient in the pedigree, there can only be one, even if there are multiple
        #: affected individuals.  Usually, the first affected patient in a study is used
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
        self.affecteds = [d for d in self.donors if d.is_affected]
        if self.index is None and self.affecteds:
            self.index = self.affecteds[0]
        self.founders = [d for d in self.donors if d.is_founder]
        self.name_to_donor = {d.name for d in self.donors}
        self.pk_to_donor = {d.pk for d in self.donors}
        self.secondary_id_to_donor = {d.secondary_id for d in self.donors}


class Cohort:
    """Class for accessing information about a set of :py:class:`Pedigree`: objects.

    Pedigrees are assumed to not overlap.

    Note that the shortcut members are set upon creation.  When pedigrees are modified after the
    construction, the ``update_shortcuts()`` method must be called.
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
                self.name_to_pedigree, {d.name: pedigree for d in pedigree.donors}, 'name')
            self._checked_update(
                self.pk_to_pedigree, {d.pk: pedigree for d in pedigree.donors}, 'pk')
            self._checked_update(
                self.secondary_id_to_pedigree, {d.secondary_id: pedigree for d in pedigree.donors},
                'secondary id')
            # Update {name,pk,secondary_id} to donor mapping
            self._checked_update(
                self.name_to_donor, {d.name: d for d in pedigree.donors}, 'name')
            self._checked_update(
                self.pk_to_donor, {d.pk: d for d in pedigree.donors}, 'pk')
            self._checked_update(
                self.secondary_id_to_donor, {d.secondary_id: d for d in pedigree.donors},
                'secondary id')

    def _checked_update(self, dest, other, msg_token):
        """Check overlap of keys between ``dest`` and ``other``, update and return dest

        In case of error, use ``msg_token`` for exception message.
        """
        overlap = set(dest.keys()) & set(other.keys())
        if overlap:
            raise ValueError('Duplicate {}s when building cohort shortcuts: {}'.format(
                msg_token, list(sorted(overlap))))
        dest.update(other)
        return dest


class CohortBuilder:
    """Helper class for building a :py:class:`Cohort` object from an iterable of
    :py:class:`GermlineDonor` objects

    Also initialize the internal father and mother attributes of :py:class:`GermlineDonor`
    """

    def __init__(self, donors):
        #: Iterable of :py:class:`GermlineDonor` objects
        self.donors = list(donors)

    def run(self):
        """Return :py:class:`Cohort` object with :py:class:`Pedigree` sub structure
        """
        return Cohort(self._yield_pedigrees())

    def _yield_pedigrees(self):
        """Yield Pedigree objects built from self.donors"""
        # Use Union-Find data structure for gathering pedigree donors
        union_find = UnionFind()
        for donor in self.donors:
            for parent_pk in (pk for pk in (donor.father_pk, donor.mother_pk) if pk):
                union_find.union(donor.pk, parent_pk)
        # Partition the donors
        partition = OrderedDict()
        for donor in self.donors:
            partition.setdefault(union_find[donor.pk], []).append(donor)
        # Construct the pedigrees
        for ped_donors in partition.values():
            affecteds = [d for d in ped_donors if d.is_affected]
            if affecteds:
                index = affecteds[-1]
            else:
                index = None
            yield Pedigree(ped_donors, index)


class GermlineDonor(GenericBioEntity):
    """Represent a donor in a germline study"""

    def __init__(self, shortcut_sheet, bio_entity):
        super().__init__(shortcut_sheet, bio_entity)
        # ``GermlineDonor`` object for father, access via property, set in ``CohortBuilder``
        self._father = None
        # ``GermlineDonor`` object for mother, access via property, set in ``CohortBuilder``
        self._mother = None

    @property
    def is_affected(self):
        """Return whether or not the donor is affected"""
        return self.extra_infos[KEY_IS_AFFECTED]

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
            raise AttributeError('Father object not yet set, although PK available.  '
                                 'Not processed through CohortBuilder?')
        return self._father

    @property
    def mother(self):
        """Return mother ``GermlineDonor`` object or ``None``"""
        if not self._mother and self.mother_pk:
            raise AttributeError('Mother object not yet set, although PK available.  '
                                 'Not processed through CohortBuilder?')
        return self._mother

    @property
    def is_founder(self):
        """Return whether is founder, i.e., has neither mother nor father"""
        return (not self.father_pk) and (not self.mother_pk)


class GermlineCaseSheet(ShortcutSampleSheet):
    """Shortcut for "germline" view on bio-medical sample sheets"""

    bio_entity_class = GermlineDonor

    def __init__(self, sheet):
        super().__init__(sheet)
        #: List of donors in the sample sheet
        self.donors = list(self._iter_donors())
        #: :py:class:`Cohort` object with the pedigrees and donors built from the sample sheet
        self.cohort = CohortBuilder(self.donors).run()

    def _iter_donors(self):
        """Return iterator over the donors in the study"""
        for bio_entity in self.sheet.bio_entities.values():
            yield GermlineDonor(self, bio_entity)
