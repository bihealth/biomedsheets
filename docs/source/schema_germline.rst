.. _schema_germline:

=========================
Germline Variants Samples
=========================

A relatively simple schema with the essential information for genetic germline variant samples with support for pedigree information.
The assumed setting is as follows.

- Each bio entity is a patient/person/donor.
- Each donor gives one normal (bio) sample (e.g., blood or saliva) and each sample has at one DNA library.
- The pedigree has to be described in a way such that all members who donated a sample are connected.
- Within each pedigree, the flag for "affected" specifies the same genetic disease (i.e., in a polydactily family, only members affected with this phenotype are flagged as affected).

.. note::

    The requirement of one DNA HTS library for each donor can be dropped in the future.

---------------
Germline Fields
---------------

The following fields must be present for germline variants sample sheets.

- ``BioSample``
    - ``fatherPk`` -- pk value of the father
    - ``motherPk`` -- pk value of the mother
    - ``sex`` -- sex of the patient
    - ``affected`` -- "is affected" flag

-------------------
Germline TSV Schema
-------------------

Additionally, there is an alternative to defining schemas in JSON format for germline variants sample sheets.
Instead, a TSV-based schema can be used.

Optionally, the schema can contain meta data, starting with ``[Metadata]`` INI-style section header (the data section has to start with ``[Data]``).

.. literalinclude:: code/germline_sheet.tsv
    :language: text
    :lines: 1-7

The ``schema`` and ``schema_version`` lines are optional.

If the file does not start with an INI-style section header, it starts with tab-separated column names.
An example is shown below:

.. literalinclude:: code/germline_sheet.tsv
    :language: text
    :lines: 8-

They are as follows:

1. ``patientName`` -- name of the patient, used for identifying the patient in the sample sheet.
   This value will be used as the secondary id of the ``BioEntity`` of the patient.
2. ``fatherName`` -- name of the patient's father, use ``0`` or ``.`` for founder.
   This refers to the ``patientName`` of the patient's father.
3. ``mother`` -- name of the patient's mother, use ``0`` or ``.`` for founder.
   This refers to the ``patientName`` of the patient's mother.
4. ``sex`` -- flag for sex, one of ``M``: male, ``F``: female, ``.``: unknown/missing, or ``0``, ``1``, ``2``, as in PED.
5. ``affected`` -- flag for being affected, one of ``Y``: yes, ``N``: no, ``.``: unknown/missing, or ``0``, ``1``, ``2``, as in PED.
6. ``folderName`` -- a folder name to search the library's FASTQ files for, ``.`` if not sequenced.
   The list of base folders to search for is given in the configuration and this folder is searched for a folder with the name given here.
   Thus, no absolute path is given here, only the folder name.
7. ``hpoTerms`` -- a comma-separated list of HPO terms to label the patient with, ``.`` if empty.
8. ``libraryType`` -- a rough classification of the library type {``WGS``, ``WES``, ``Panel-seq``}, ``.`` if not sequenced or unknown
9. ``kitName/kitType`` -- type/name of the kit used (free text/controlled vocabulary), ``.`` if not sequenced or unknown; optional.
   This column can be left out.
10. ``kitVersion`` -- version of the kit used, ``.`` if not sequenced or unknown; optional.
    This column can be left out.

Optionally, the following fields can be added:

- ``seqPlatform`` can be one of ``Illumina`` and ``PacBio``, default is ``Illumina``
