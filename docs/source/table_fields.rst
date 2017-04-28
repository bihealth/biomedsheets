.. _table_fields:

============
Table Fields
============

-----------------
Core Table Fields
-----------------

This section describes the common table fields.
Generally, the ``pk`` field is an integer primary key that is to be automatically generated numbering each element uniquely despite its level in the hierarchy of all JSON elements (i.e. autoincrement in RDBMS).
The field ``secondary_id`` is an identifier assigned by the "data owner" (e.g., the collaboration partner).
This identifier has to be unique within a given project but can be ambiguous globally.

A possible best practice is to enforce the ``secondary_id`` to only consist of alphanumeric characters and underscores.
Then, they should be constructed as (none of the ``<Field>`` values should contain a hyphen itself):

::

    <BioEntity>-<BioSample>-<TestSample>-<NGSLibrary>

(of course only up to “BioSample” for BioSamples etc.).

Examples are:

- BioEntity secondary ids: 2355, BIH-234
- BioSample secondary ids:
    - 2355-B1 (first blood sample from patient 2355)
    - BIH_234-N1 (first normal sample from patient BIH-234)
    - BIH_234-T2 (second tumor sample from patient BIH-234)
- TestSample secondary ids:
    - 2355-B1-DNA1 (first DNA extraction from first blood sample)
    - BIH_234-T1-RNA1 (first RNA extraction from first tumor sample)
    - BIH_234-T2-DNA2 (second DNA extraction from second tumor sample)

Generally, the following are “core fields” (pk: primary key, fk: foreign key).

BioEntity
=========

- pk: integer
- secondary_id: string

BioSample
=========

- pk: integer
- bio_entity: fk to BioEntity.pk
- secondary_id: string

TestSample
==========

- pk: integer
- bio_sample: fk to BioSample.pk
- secondary_id: string

NGSLibrary
==========

- pk: integer
- test_sample: fk to TestSample.pk
- secondary_id: string

FlowCell
========

- pk: integer
- machine_name: string
- flowcell_name: string

NGSLibraryOnFlowCell
====================

- pk: integer
- ngs_library: fk to NGSLibrary.pk
- flowcell: fk to FlowCell
- lane: int


-------------------
Common Table Fields
-------------------

For many major use cases, the following table fields are useful additions to get a list of "common fields".

For all tables, adding a list of strings with external IDs (e.g., called "external_ids") is recommendable.
This way, external resources can be linked out to.
A recommendation is to use URLs for giving reads an unambiguous prefix.
These URLs can be pseudo URLs or real entry points in remote REST APIs.
Further, each record has a meta_data field for structured data in JSON format.

BioEntity
=========

- affected: boolean, optional field for specifying the “affected” state in rare disease studies
- sex: {‘male’, ‘female’, ‘unknown’}, optional field for person’s sex in germline studies
- father: fk to BioEntity.pk, optional fields for linking to father
- mother: fk to BioEntity.pk, optional fields for linking to mother

BioSample
=========

- cell_type: string with controlled vocabulary, optional field for specifying cell type

TestSample
==========

- extraction_type: controlled vocabulary with extraction type, e.g. {‘DNA’, ‘RNA’} or a superset thereof; optional field for describing extracted data

NGSLibrary
==========

- library_kind: controlled vocabulary with library preparation type, e.g., {‘WES’, ‘WGS’, ‘RNA-seq’, ‘other’} or a superset thereof; required field for describing library type
- kit: controlled vocabulary describing kit and version used for targeted sequencing, or RNA amplifcation method

NGSLibraryOnFC
==============

- adapter_name: string, optional field describing name of used adapter barcode(s)
- adapter_seq: string, optional field giving sequence of used adapter barcode(s)
