.. _index:

==============================
Welcome to BioMed Sample Sheet
==============================

.. note::

    This document is a draft and only the special case of matched tumor/normal data from cancer studies is currently ready.

This document describes the current draft of the biomedical sample sheets.

The project consists of

- a JSON-based data format for the description of biomedical sample sheets,
- pre-defined data types to be used in the sample sheets,
- a Python program for the validation thereof,
- a Python program for conversion between JSON and Excel-based sample sheets (for easier viewing and editing),
- a Python library for access of the JSON sheets, and
- a Python library for simplified access of the JSON sheets for the important cases of matched tumor/normal studies and rare disease studies with pedigree relationships.

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

.. toctree::
    :caption: API
    :maxdepth: 1
    :titlesonly:
    :hidden:

    api_shortcuts
    api_io
    api_models


.. Generated pages, should not appear

    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`
