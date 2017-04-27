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
Note that the sheet only contains one donor with two bio samples (normal sample ``N1`` and primary tumor ``T1``).

.. literalinclude:: ../../examples/example_cancer_matched.json
    :language: json

-------------
Code Examples
-------------

The following Python program uses the ``biomedsheets`` module for loading the JSON sheet from above.
It then prints the names of the donors and the names of the NGS libraries for the tumor/normal pairs.

.. literalinclude:: ../../examples/use_shortcut_cancer.py

------
Output
------

The output of the program is as follows::

    Donors

    P001-000001

    Libraries of all tumor/normal pairs

      P001-000001
        normal DNA: P001-N1-DNA1-WES1-000004
        tumor DNA:  P001-T1-DNA1-WES1-000007
        tumor RNA:  P001-T1-RNA1-mRNA_seq1-000009
