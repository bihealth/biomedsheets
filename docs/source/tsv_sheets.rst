.. _tsv_sheets:

=================
TSV Sample Sheets
=================

Writing sample sheets as TSV (tab-separated values) files is an alternative to writing JSON files.
As they can be edited with text editors and spreadsheet programs such as Excel, viewing and modifying TSV files is more convenient than for JSON files.

However, TSV sample sheets do not have a full 1:1 relation to the JSON sample sheets.
Rather, they serve as shortcuts for the most important practical cases (germline variants, matched cancer, and (later) relatively simple generic experiments).

---------------
Rough Structure
---------------

Overall, a TSV sample sheet looks as follows.

First, the sheet can start with a ``[Metadata]`` section.
This can be used for defining meta data for the sheet.
The following key/value pairs can be defined:

- ``schema`` -- name of the schema (``germline_variants`` or ``cancer_matched``),
- ``schema_version`` -- for versionizing the schema (currently only ``v1``),
- ``title`` -- title of the sample sheet,
- ``description`` -- a description of the sample sheet.

.. literalinclude:: code/germline_sheet_ext.tsv
    :lines: 1-5

Optionally, a ``[Custom Fields]`` section can follow.
This can be used to define custom fields to place in addition to the core fields.
The core fields will be described later when describing the germline variants and matched cancer sheet formats.
Custom field definition is explained in :ref:`schema_custom_fields`.

.. literalinclude:: code/germline_sheet_ext.tsv
    :lines: 7-10

Finally, the data is placed in a ``[Data]`` section.
If the Metadata and Custom Fields sections are missing, the file can also start with the column headers of the data section (omitting ``[Data]``).

.. literalinclude:: code/germline_sheet_ext.tsv
    :lines: 12-16

.. _tsv_sheet_processing:

--------------------
TSV Sheet Processing
--------------------

When reading TSV sample sheets, they will be converted to JSON sheets on the fly.
This will be done with the algorithm described below.

For germline sample sheets, only the patient (``BioEntity``) is explicitely defined and named.
It is assumed that only one bio sample it taken for each bio entity and is named ``N1``.
Further, it is assumed that only one test sample is extracted (implicitely using extraction type ``DNA``) which is named ``DNA1``.
Multiple libraries can be specified by giving different lines with the same ``patientName`` and different ``extractionType`` and/or ``folderName`` is given.
These will be named ``WGS1``, ``WGS2``, etc. (or ``WES1``, ``WES2``, etc.)

For matched cancer sample sheets, the patient (``BioEntity``) is explicitely defined and named as well as the ``BioSample``.
The name of the sample is given explicitely to allow for naming tumors differently, e.g., ``T1`` for the first sample from a primary tumor and ``M1`` for the first sample of a metastatic tumor.
For each extraction type, (e.g., ``DNA`` or ``RNA``), a new counter will be started (e.g., yielding ``DNA1``, ``DNA2``, ``RNA1``, etc.)
In addition, for each new ``sampleType``, a new sample will be started and for each new ``folderName``, a new ``NGSLibrary`` will be started.
