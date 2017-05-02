.. _index:

==============================
Welcome to BioMed Sample Sheet
==============================

This document describes the biomedical sample sheets file format and software.

.. figure:: img/Overview_Usage.png
    :align: center

Biomedical sample sheet files are files for saving the necessary information on biomedical experiments/studies that is required for the data analysis.
For example, such a sheet might describe patients and their family relations and phenotypes for a raw disease NGS study.
Another example is the description of a cohort of cancer patients, taken biopsies and subsequent sequencing.

Such files are useful for various tasks such as (1) information export from/import into databases, (2) required sample meta data for pipelines, (3) displaying information to users and allow them to enter data, (4) exchanging experiment meta data with collaborators.

The biomedical sample sheet file format (and the data schema used) was developed at the Core Unit Bioinformatics of the Berlin Institute of Health and is based on the work of Sven Nahnsen's group in Tubingen.

You are viewing the documentation of the ``biomedsheets`` Python package which contains the reference implementation for parsing/writing such files and the specification of the data schema and related file formats.

----------------
Project Contents
----------------

The project consists of

- a JSON-based data format for the description of biomedical sample sheets as well as a TSV format that is easier to use for humans,
- pre-defined data types to be used in the sample sheets,
- a Python program for the validation thereof,
- a Python program for conversion between JSON and TSV-based sample sheets (for easier viewing and editing),
- a Python library for access of the JSON sheets, and
- a Python library for simplified access of the JSON sheets for the important cases of matched tumor/normal studies and rare disease studies with pedigree relationships.

--------------
Project Status
--------------

We (CUBI) are actively using the file format and library but it is still under development.

--------------
Open Questions
--------------

- Keep or drop globally unique PKs from the file names?
  Random pks make everything very hard to use as files, add complexity to shortcut schemas.
  Sequential pks at least keep a temporal order.

.. toctree::
    :caption: Overview
    :maxdepth: 1
    :titlesonly:
    :hidden:

    introduction
    high_level_overview
    table_fields
    json_sheet_schema
    tsv_sheets
    examples
    faq

.. toctree::
    :caption: Schemas & Workflows
    :maxdepth: 1
    :titlesonly:
    :hidden:

    workflow_assumptions
    entity_names
    schema_cancer
    schema_germline
    schema_custom_fields
    schema_generic

.. toctree::
    :caption: API
    :maxdepth: 1
    :titlesonly:
    :hidden:

    api_models
    api_shortcuts
    api_io
    api_io_tsv


.. Generated pages, should not appear

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
