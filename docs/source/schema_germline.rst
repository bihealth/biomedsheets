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

The following fields must be present for matched cancer sample sheets.

- BioSample
    - fatherPk -- pk value of the father
    - motherPk -- pk value of the mother
    - sex -- sex of the patient
    - affected -- "is affected" flag

-------------------
Germline TSV Schema
-------------------

Additionally, there is an alternative to defining schemas in JSON format for germline variants sample sheets.
Instead, a TSV-based schema can be used.

Optionally, the schema can contain meta data, starting with ``[Metadata]`` INI-style section header (the data section has to start with ``[Data]``).

.. literalinclude:: code/germline_schema.tsv
    :language: text
    :lines: 1-7

The ``schema`` and ``schema_version`` lines are optional.

If the file does not start with an INI-style section header, it starts with tab-separated column names.
An example is shown below:

.. literalinclude:: code/germline_schema.tsv
    :language: text
    :lines: 8-

They are as follows:

1. ``patientName`` -- name of the patient, used for identifying the patient in the sample sheet. This value will be translated into ``BioEntity`` defined in the global scheme (:ref:`high_level_overview`) and JSON schema (:ref:`examples`).
2. ``fatherName`` -- name of the patient's father, dot (``0``) for founder
3. ``mother`` -- name of the patient's mother, dot (``0``) for founder
4. ``sex`` -- flag for sex, one of ``M``: male, ``F``: female, ``.``: unknown/missing, or ``0``, ``1``, ``2``, as in PED
5. ``affected`` -- flag for being affected, one of ``Y``: yes, ``N``: no, ``.``: unknown/missing, or ``0``, ``1``, ``2``, as in PED
6. ``folderName`` -- a folder name to search the library's FASTQ files for, ``.`` if not sequenced
   A list of base folders to search for the folder names is given in the configuration, so no full path is given here.
7. ``hpoTerms`` -- a comma-separated list of HPO terms
8. ``extractionType`` -- a valid extraction type as in the JSON schema (:ref:`exxamples`), which is one of ``DNA``, ``RNA`` or ``other``. This links to `TestSample` in the global overview :ref:`high_level_overview`.
9. ``libraryType`` -- a rough classification of the library type {``WGS``, ``WES``, ``Panel-seq``}, ``.`` if not sequenced or unknown. This entry will be translated to ``NGSLibrary`` defined in the global scheme (ref:`high_level_overview`) and JSON schema (:ref:`examples`)
10. ``kitName/kitType`` -- type/name of the kit used (free text/controlled vocabulary), ``.`` if not sequenced or unknown; optional.
   This column can be left out.
11. ``kitVersion`` -- version of the kit used, ``.`` if not sequenced or unknown; optional.
    This column can be left out.

Note that the name of ``BioSample``, ``TestSample``, and ``NGSLibrary`` entities are missing, they will be auto-generated based on the ``patienName``, ``extractionType`` and ``libraryType``, respectively.

Optionally, the following fields can be added:

- ``seqPlatform`` can be one of ``Illumina`` and ``PacBio``, default is ``Illumina``
