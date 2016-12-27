# -*- coding: utf-8 -*-
"""Python classes for representing the generic part of BioMedical sheets
"""

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'

#: Key for storing disabled flag for entities
KEY_DISABLED = 'disabled'
# TODO: add this as a main property

#: Key for selecting an ``NGSLibrary`` object
KEY_NGS_LIBRARY = 'ngs_library'
#: Key for selecting an ``MSProteinPool`` object
KEY_MS_PROTEIN_POOL = 'ms_protein_pool'

#: Frozen set of valid ``TestSample`` child types
TEST_SAMPLE_CHILDREN = frozenset((
    KEY_NGS_LIBRARY, KEY_MS_PROTEIN_POOL))


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
            return self.sub_entries.crawl(rest)
        else:
            return self.sub_entries[next]

    def _merge_sub_entries(self, *dicts):
        # Check for conflicts in secondary ids
        duplicates = {}
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
    """Container for multiple :pyclass:`BioEntity` objects
    """

    def __init__(self, identifier, title, description=None,
                 bio_entities=None):
        #: Identifier URI of the sheet, cannot be changed after construction
        self.identifier = identifier
        #: Title of the sheet, can be changed after construction
        self.title = title
        #: Description of the sheet
        self.description = description
        #: List of ``BioEntity`` objects described in the sheet
        self.bio_entities = dict(bio_entities) or []
        #: Create ``sub_entries`` shortcut for ``crawl()``
        self.sub_entries = self.bio_entities


class SheetEntry:
    """Base class for the different ``Sheet`` entries

    Pulls up the common properties of primary key, secondary ID and additional
    properties dict
    """

    def __init__(self, pk, secondary_id, additional_properties=None):
        #: Primary key of the bio entity, globally unique
        self.pk = pk
        #: ``str`` with secondary id of the bio entity, unique in the sheet
        self.secondary_id = secondary_id
        #: Additional properties, ``dict``-like object
        self.additional_properties = additional_properties or {}


class BioEntity(SheetEntry, CrawlMixin):
    """Represent one biological specimen
    """

    def __init__(self, pk, secondary_id, additional_properties=None,
                 bio_samples=None):
        super().__init__(pk, secondary_id, additional_properties)
        #: List of ``BioSample`` objects described for the ``BioEntity``
        self.bio_samples = dict(bio_samples) or []
        #: Create ``sub_entries`` shortcut for ``crawl()``
        self.bio_samples = self.bio_samples


class BioSample(SheetEntry, CrawlMixin):
    """Represent one sample taken from a biological entity/specimen
    """

    def __init__(self, pk, secondary_id, additional_properties=None,
                 test_samples=None):
        super().__init__(pk, secondary_id, additional_properties)
        #: List of ``TestSample`` objects described for the ``BioSample``
        self.test_samples = dict(test_samples) or []
        #: Create ``sub_entries`` shortcut for ``crawl()``
        self.test_samples = self.test_samples


class TestSample(SheetEntry, CrawlMixin):
    """Represent a technical sample from biological sample, e.g., DNA or RNA
    """

    def __init__(self, pk, secondary_id, additional_properties=None,
                 ngs_libraries=None, ms_protein_pools=None):
        super().__init__(pk, secondary_id, additional_properties)
        #: List of ``NGSLibrary`` objects described for the ``TestSample``
        self.ngs_libraries = dict(ngs_libraries) or []
        #: List of ``MSProteinPools`` objects described for the ``TestSample``
        self.ms_protein_pools = dict(ms_protein_pools) or []
        # ``sub_entries`` shortcut, check for duplicates
        self.sub_entries = self._merge_sub_entries(
            self.ngs_libraries, self.ms_protein_pools)


class NGSLibrary(SheetEntry):
    """Represent one NGSLibrary generated from a test sample
    """

    def __init__(self, pk, secondary_id, additional_properties=None):
        super().__init__(pk, secondary_id, additional_properties)


class MSProteinPool(SheetEntry):
    """Represent one Mass-spec protein pool
    """

    def __init__(self, pk, secondary_id, additional_properties=None):
        super().__init__(pk, secondary_id, additional_properties)
