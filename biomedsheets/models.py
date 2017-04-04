# -*- coding: utf-8 -*-
"""Python classes for representing the generic part of BioMedical sheets
"""

from collections import OrderedDict

from .naming import DEFAULT_NAME_GENERATOR

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


#: Key for storing disabled flag for entities
KEY_DISABLED = 'disabled'
# TODO: add this as a main property

#: Key for selecting an ``NGSLibrary`` object
KEY_NGS_LIBRARY = 'ngs_library'

#: Frozen set of valid ``TestSample`` child types
TEST_SAMPLE_CHILDREN = frozenset((KEY_NGS_LIBRARY,))


class BioMedSheetsBaseException(Exception):
    """Base exception for module"""


class AmbiguousSecondaryIdException(BioMedSheetsBaseException):
    """Raised on duplicate secondary IDs"""


class SheetPathCrawlingException(Exception):
    """Raised on problems crawling the sample sheet"""


class InvalidSecondaryIDException(SheetPathCrawlingException):
    """Raised when the secondary ID was invalid"""


class SecondaryIDNotFoundException(SheetPathCrawlingException):
    """Raised when a secondary id could not be found during crawling"""


class CrawlMixin:
    """Mixin that provides the ``crawl()`` function

    Also provides helpers for merging "sub_entries" dicts
    """

    def crawl(self, name, sep='-'):
        """Crawl through sheet based on the path by secondary id
        """
        if sep in name:
            next, rest = name.split(sep, 1)
        else:
            next, rest = name, None
        if next not in self.sub_entries:
            raise SecondaryIDNotFoundException(
                'Could not find sub entry with secondary ID {}'.format(
                    next))
        if rest:
            return self.sub_entries[next].crawl(rest)
        else:
            return self.sub_entries[next]

    def _merge_sub_entries(self, *dicts):
        # Check for conflicts in secondary ids
        duplicates = set()
        for d1 in dicts:
            for d2 in dicts:
                if d1 is not d2:
                    dupes = set(d1.keys()) & set(d2.keys())
                    duplicates = duplicates | dupes
        if len(duplicates) > 0:
            raise AmbiguousSecondaryIdException(
                'Ambiguous secondary IDs: {}'.format(duplicates))
        # Build result
        result = {}
        for d in dicts:
            result.update(d)
        return result


class Sheet(CrawlMixin):
    """Container for multiple :class:`BioEntity` objects
    """

    def __init__(self, identifier, title, json_data, description=None,
                 bio_entities=None, extra_infos=None, dict_type=OrderedDict,
                 name_generator=DEFAULT_NAME_GENERATOR):
        #: Identifier URI of the sheet, cannot be changed after construction
        self.identifier = identifier
        #: Title of the sheet, can be changed after construction
        self.title = title
        #: The underlying data from JSON
        self.json_data = json_data
        #: Description of the sheet
        self.description = description
        #: Extra info, ``dict``-like object
        self.extra_infos = dict_type(extra_infos or [])
        #: List of ``BioEntity`` objects described in the sheet
        self.bio_entities = dict_type(bio_entities or [])
        #: Create ``sub_entries`` shortcut for ``crawl()``
        self.sub_entries = self.bio_entities
        #: Name generator used in the sheet
        self.name_generator = name_generator

    def __repr__(self):
        return 'Sheet({})'.format(', '.join(map(str, [
            self.identifier, self.title, self.json_data, self.description,
            self.bio_entities, self.extra_infos, self.sub_entries])))

    def __str__(self):
        return repr(self)


class SheetEntry:
    """Base class for the different ``Sheet`` entries

    Pulls up the common properties of primary key, secondary ID and additional
    properties dict
    """

    def __init__(self, pk, disabled, secondary_id, extra_ids=None,
                 extra_infos=None, dict_type=OrderedDict,
                 name_generator=DEFAULT_NAME_GENERATOR):
        #: Primary key of the bio entity, globally unique
        self.pk = pk
        #: Flag for explicit disabling of objects
        self.disabled = disabled
        #: ``str`` with secondary id fragment of the bio entity, unique in the
        #: sheet
        self.secondary_id = secondary_id
        #: Extra IDs
        self.extra_ids = list(extra_ids or [])
        #: Extra info, ``dict``-like object
        self.extra_infos = dict_type(extra_infos or [])
        #: Name generator to use
        self.name_generator = name_generator

    @property
    def full_secondary_id(self):
        """Return full path from BioEntity to this entry"""
        raise NotImplementedError('Override me!')

    @property
    def name(self):
        """Abstract function for returning name"""
        return self.name_generator(self)

    @property
    def enabled(self):
        """Inverse of ``self.enabled``"""
        return not self.disabled


class BioEntity(SheetEntry, CrawlMixin):
    """Represent one biological specimen
    """

    def __init__(self, pk, disabled, secondary_id, extra_ids=None,
                 extra_infos=None, bio_samples=None, dict_type=OrderedDict,
                 name_generator=DEFAULT_NAME_GENERATOR):
        super().__init__(
            pk, disabled, secondary_id, extra_ids, extra_infos, dict_type,
            name_generator)
        #: List of ``BioSample`` objects described for the ``BioEntity``
        self.bio_samples = dict_type(bio_samples or [])
        # Assign owner pointer in bio samples to self
        for bio_sample in self.bio_samples.values():
            bio_sample.bio_entity = self
        #: Create ``sub_entries`` shortcut for ``crawl()``
        self.sub_entries = self.bio_samples

    @property
    def full_secondary_id(self):
        return self.secondary_id

    def __repr__(self):
        return 'BioEntity({})'.format(', '.join(map(str, [
            self.pk, self.disabled, self.secondary_id, self.extra_ids,
            self.extra_infos, self.bio_samples])))

    def __str__(self):
        return repr(self)


class BioSample(SheetEntry, CrawlMixin):
    """Represent one sample taken from a biological entity/specimen
    """

    def __init__(self, pk, disabled, secondary_id, extra_ids=None,
                 extra_infos=None, test_samples=None, dict_type=OrderedDict,
                 bio_entity=None, name_generator=DEFAULT_NAME_GENERATOR):
        super().__init__(
            pk, disabled, secondary_id, extra_ids, extra_infos, dict_type,
            name_generator)
        #: Containing BioEntity
        self.bio_entity = bio_entity
        #: List of ``TestSample`` objects described for the ``BioSample``
        self.test_samples = dict_type(test_samples or [])
        # Assign owner pointer in test samples to self
        for test_sample in self.test_samples.values():
            test_sample.bio_sample = self
        #: Create ``sub_entries`` shortcut for ``crawl()``
        self.sub_entries = self.test_samples

    @property
    def full_secondary_id(self):
        return '-'.join((self.bio_entity.full_secondary_id, self.secondary_id))

    def __repr__(self):
        return 'BioSample({})'.format(', '.join(map(str, [
            self.pk, self.disabled, self.secondary_id, self.extra_ids,
            self.extra_infos, self.test_samples])))

    def __str__(self):
        return repr(self)


class TestSample(SheetEntry, CrawlMixin):
    """Represent a technical sample from biological sample, e.g., DNA or RNA
    """

    def __init__(self, pk, disabled, secondary_id, extra_ids=None,
                 extra_infos=None, ngs_libraries=None, dict_type=OrderedDict,
                 bio_sample=None,
                 name_generator=DEFAULT_NAME_GENERATOR):
        super().__init__(
            pk, disabled, secondary_id, extra_ids, extra_infos, dict_type,
            name_generator)
        #: Containing BioSample
        self.bio_sample = bio_sample
        #: List of ``NGSLibrary`` objects described for the ``TestSample``
        self.ngs_libraries = dict_type(ngs_libraries or [])
        # Assign owner pointer in NGS libraries to self
        for ngs_library in self.ngs_libraries.values():
            ngs_library.test_sample = self
        # ``sub_entries`` shortcut, check for duplicates
        self.sub_entries = self._merge_sub_entries(self.ngs_libraries)

    @property
    def full_secondary_id(self):
        return '-'.join((self.bio_sample.full_secondary_id, self.secondary_id))

    def __repr__(self):
        return 'TestSample({})'.format(', '.join(map(str, [
            self.pk, self.disabled, self.secondary_id, self.extra_ids,
            self.extra_infos, self.ngs_libraries])))

    def __str__(self):
        return repr(self)


class NGSLibrary(SheetEntry):
    """Represent one NGSLibrary generated from a test sample
    """

    def __init__(self, pk, disabled, secondary_id, extra_ids=None,
                 extra_infos=None, dict_type=OrderedDict, test_sample=None,
                 name_generator=DEFAULT_NAME_GENERATOR):
        super().__init__(
            pk, disabled, secondary_id, extra_ids, extra_infos, dict_type,
            name_generator)
        #: Owning TestSample
        self.test_sample = test_sample

    @property
    def full_secondary_id(self):
        return '-'.join((
            self.test_sample.full_secondary_id, self.secondary_id))

    def __repr__(self):
        return 'NGSLibrary({})'.format(', '.join(map(str, [
            self.pk, self.disabled, self.secondary_id, self.extra_ids,
            self.extra_infos])))

    def __str__(self):
        return repr(self)
