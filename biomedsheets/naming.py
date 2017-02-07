# -*- coding: utf-8 -*
"""Helper code for name generation"""

#: PK padding length
DEFAULT_PK_PADDING_LENGTH = 6

#: Default name pattern
NAME_PATTERN_DEFAULT = "{full_secondary_id}-{pk}"

#: Name pattern with secondary id only
NAME_PATTERN_SECONDARY_ID = "{full_secondary_id}"

#: Naming scheme "{secondary_id}-{pk}"
NAMING_SECONDARY_ID_PK = 'secondary_id_pk'

#: Naming scheme "{secondary_id}"
NAMING_ONLY_SECONDARY_ID = 'only_secondary_id'

#: Default naming scheme
NAMING_DEFAULT = NAMING_SECONDARY_ID_PK

#: Valid naming schemes
NAMING_SCHEMES = (NAMING_SECONDARY_ID_PK, NAMING_ONLY_SECONDARY_ID)


class NameGenerator:
    """Base class for name generators for BioMed Sheet entities"""

    def __call__(self, obj):
        """Return generated name"""
        raise NotImplementedError('Abstract method called!')


class PatternNameGenerator(NameGenerator):
    """Name generation based on string format patterns"""

    def __init__(self, pattern, pk_padding_length=DEFAULT_PK_PADDING_LENGTH):
        #: The pattern to generate the name for
        self.pattern = pattern
        #: The default padding length
        self.pk_padding_length = pk_padding_length

    def __call__(self, obj):
        """Return generated name"""
        padded_pk = str(obj.pk).rjust(self.pk_padding_length, '0')
        return self.pattern.format(full_secondary_id=obj.full_secondary_id, pk=padded_pk)


#: Default name generator is a :py:class:`PatternNameGenerator` with
#: :py:data:`NAME_PATTERN_DEFAULT` as the value.
DEFAULT_NAME_GENERATOR = PatternNameGenerator(NAME_PATTERN_DEFAULT)


def name_generator_for_scheme(scheme):
    """Return ``PatternNameGenerator`` for the given naming ``scheme``"""
    if scheme not in NAMING_SCHEMES:
        raise ValueError('No known naming scheme {}'.format(scheme))
    mapping = {
        NAMING_SECONDARY_ID_PK: PatternNameGenerator(NAME_PATTERN_DEFAULT),
        NAMING_ONLY_SECONDARY_ID: PatternNameGenerator(NAME_PATTERN_SECONDARY_ID),
    }
    return mapping[scheme]
