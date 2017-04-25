=============
BioMed Sheets
=============

.. image:: https://travis-ci.org/bihealth/biomedsheets.svg?branch=master
    :target: https://travis-ci.org/bihealth/biomedsheets

.. image:: https://readthedocs.org/projects/biomedsheets/badge/?version=master
    :target: https://biomedsheets.readthedocs.io/en/master

.. image:: https://api.codacy.com/project/badge/Grade/842a296b23d5450eb7bc525621d7f5a2
    :target: https://www.codacy.com/app/manuel-holtgrewe/biomedsheets?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/biomedsheets&amp;utm_campaign=Badge_Grade

.. image:: https://api.codacy.com/project/badge/Coverage/842a296b23d5450eb7bc525621d7f5a2
    :target: https://www.codacy.com/app/manuel-holtgrewe/biomedsheets?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=bihealth/biomedsheets&amp;utm_campaign=Badge_Coverage

This project contains the documentation for the BioMedical sample sheets project.
Further, it contains the implementation of a Python API for I/O and comfortable access to the sample sheets and some CLI tools.

------------
Installation
------------

It's best to start a new virtualenv

::

    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    $ pip install -r requirements_dev.txt
    $ pip install -e .

Use ``python setup.py install`` if you want to copy the files instead of creating a link only.

----------------------
Building Documentation
----------------------

After installation (``requirements_dev.txt`` contains the appropriate Sphinx version)

::

    $ cd docs
    $ make clean html

Now, open ``docs/build/html/index.html``.

-------------
Running Tests
-------------

::

    $ py.test
