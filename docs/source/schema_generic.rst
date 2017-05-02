.. _schema_generic:

=====================
Generic Sample Sheets
=====================

We describe call using a sample sheet not following the matched cancer or germline variants schema **generic sample sheets**.
These can be used to describe arbitrary biomedical experiments.
There is no restriction on the structure of such a sample sheet.

However, there also is a shortcut TSV format to describe such sample sheets that has some restrictions.


.. _schema_generic_tsv:

------------------
Generic TSV Schema
------------------

The following assumptions must hold when using the generic TSV schema:

- Each bio entity must have at least one bio sample, each bio sample at least one test sample, and each test sample at least one NGS library.
- You have to explicitely assign a secondary ID to each object in this tree.
- The files of each NGS library are below the same folder.
- You have to define the extraction type (e.g., ``DNA`` or ``RNA``) and the librar type (e.g., ``mRNA_seq`` or ``WES``).

A minimal generic TSV file (with header) looks as follows:

.. literalinclude:: code/generic_sheet.tsv
    :language: text

Again, the header can be omitted, then the file starts after the ``[Data]`` line.
All further information has to be described using custom fields as described in the section :ref:`schema_custom_fields`.
For example with additional information:

.. literalinclude:: code/generic_sheet_ext.tsv
    :language: text
