=============
BioMed Sheets
=============

.. image:: https://readthedocs.org/projects/biomedsheets/badge/?version=master
    :target: https://biomedsheets.readthedocs.io/en/master


This project contains the documentation for the BioMedical sample sheets project.
Further, it contains the implementation of a Python API for I/O and comfortable access to the sample sheets and some CLI tools.

------------
Installation
------------

It's best to start a new virtualenv

::

    $ virtualenv -p python3 venv
    $ source venv/bin/activate
    $ pip install -r requirements/dev.txt
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

------------------
Publishing to PyPi
------------------

::

    $ python setup.py sdist upload
