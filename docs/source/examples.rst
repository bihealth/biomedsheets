.. _examples:

========
Examples
========

.. note:

    The examples below are restricted to the case of matched tumor/normal sample sheets

--------------
Sheet Examples
--------------

Below is an example JSON file with a cancer sample sheet.
Note that the sheet only conatins one donor with two bio samples (primary tumor ``T1`` and metastasis ``M1``).

.. literalinclude:: ../../examples/example_cancer.json
    :language: json

-------------
Code Examples
-------------

The following Python program uses the ``biomedsheets`` module for loading the JSON sheet from above.
It them prints the names of the donors and the names of the NGS libraries for the tumor/normal pairs.

.. literalinclude:: ../../examples/use_shortcut_cancer.py

------
Output
------

The output of the program is as follows::

    Donors

    123001-BIH_001

    Libraries of all tumor/normal pairs

    123001-BIH_001
        normal DNA: 567001-BIH_001-N1-DNA1-WES1
        tumor DNA:  567002-BIH_001-T1-DNA1-WES1
        tumor RNA:  567004-BIH_001-T1-RNA1-RNAseq1
    123001-BIH_001
        normal DNA: 567001-BIH_001-N1-DNA1-WES1
        tumor DNA:  567005-BIH_001-M1-DNA1-WES1
