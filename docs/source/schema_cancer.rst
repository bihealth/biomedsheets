.. _schema_cancer:

======================
Matched Cancer Samples
======================

A relatively simple schema for the analysis of matched tumor/normal samples from cancer studies.
The assumed setting is as follows.

- Each bio entity is a patient/donor.
- Each donor gives one normal (bio) sample (e.g., blood or saliva) and at least one (bio) sample from the cancer (e.g., primary tumor, metastesis, or blood cancer cells).
- For each cancer and non-cancer sample, there is at least one DNA HTS library sequenced.
- For each cancer sample, there can be RNA HTS libraries.
- Only the first seen DNA/RNA library is considered for each sample (the "primary one")

.. note::

    The requirement of one DNA HTS library for each sample and RNA only for cancer can be dropped in the future.

.. note::

    Allowing for other assays such as proteomics and metabolomics should be possible in the future.

---------------------
Matched Cancer Fields
---------------------

The following fields must be present for matched cancer sample sheets.

- BioSample
    - isCancer -- a boolean defining whether the sample was taken from cancerous cells

-------------------------
Matched Cancer TSV Schema
-------------------------

Additionally, there is an alternative to defining schemas in JSON format for matched cancer sample sheets.
Instead, a TSV-based schema can be used.

Optionally, the schema can contain meta data, starting with ``[Metadata]`` INI-style section header (the data section has to start with ``[Data]``).

.. literalinclude:: code/cancer_schema.tsv
    :language: text
    :lines: 1-7

The ``schema`` and ``schema_version`` lines are optional.

If the file does not start with an INI-style section header, it starts with tab-separated column names.
An example is shown below:

.. literalinclude:: code/cancer_schema.tsv
    :language: text
    :lines: 8-

They are as follows:

1. ``patientName`` -- name of the patient, used for identifying the patient in the sample sheet.
2. ``sampleName`` -- name of the sample, used for identifying the sample for the patient in the sample sheet (the combination of patient and sample must be unique in the sheet).
3. ``isCancer`` -- a flag identifying a sample as being cancerous, one of {``Y``, ``N``, ``1``, ``0``}
4. ``extractionType`` -- a valid extraction type as in the JSON schema
5. ``libraryType`` -- a valid libraryType, as in the JSON schema
6. ``folderName`` -- a folder name to search the library's FASTQ files for.
   A list of base folders to search for the folder names is given in the configuration, so no full path is given here.

Note that the name of the ``TestSample`` and and ``NGSLibrary`` entities are missing, they will be auto-generated based on the ``extractionType`` and ``libraryType``.
