.. _json_sheet_schema:

==================
JSON Sample Sheets
==================

---------------
Rough Structure
---------------

Overall, a JSON sample sheet looks as follows.

The sheet is described as a JSON object and is given an ID, a title, and a description.

.. literalinclude:: code/small.json
    :lines: 1-4

This is followed by a section describing the optional additional fields for each of the objects.

.. literalinclude:: code/small.json
    :lines: 6

The extra fields can be described in each schema, e.g., as in the following example referring to the NCBI organism taxonomy.

.. literalinclude:: code/small.json
    :lines: 8-14

Or by refering to the built-in standard fields bundled with the ``biomedsheets`` module.

.. literalinclude:: code/small.json
    :lines: 15-17

There can be field definitions for each data type.

.. literalinclude:: code/small.json
    :lines: 18-22

Then, the bio entities are given.
They are stored in a JSON object/map.
The attribute name/key is the secondary ID that has to be unique within the project.
Each BioEntity must have a primary key, can have some extra IDs and additional information (as described in ``extraInfoDefs`` above).

.. literalinclude:: code/small.json
    :lines: 24-33

Then, each BioEntity can have a number of BioSamples.
Note that the secondary id is given without the prefix of the secondary ID of the containing BioSample.
The BioSample must have a global ID ``pk``, can have extra infos attached (and, of course extra IDs, omitted here).

.. literalinclude:: code/small.json
    :lines: 34-38

Recursively, each BioSample can have a number of TestSamples which can have a number of NGSLibrary's and MSProteinPool's.

.. literalinclude:: code/small.json
    :lines: 39-

----------------
Sheet Validation
----------------

Validation of sample sheets has four steps:

1. the sheet must be valid JSON,
2. expansion of JSON pointers ``{ "$ref": "<URL>" }`` is performed,
3. the sheet must conform to the JSON schema bundled with ``biomedsheets`` (in the future it will be versionised at some URL),
4. additional validation based on ``extraInfoDefs`` is performed.

Steps 1 and 3 can be performed with standard tools or libraries.
Step 2 is relatively easy and the ``biomedsheets`` module ships with code for performing this easily (the functionality is available as a Python program as well).
Step 4 is not implemented yet.

On the one hand, custom fields allow for the definition of arbitrary "simple" values.
Currently, it is possible to have boolean, numbers, strings, enums and lists of the atomic types.
On the other hand, using JSON pointers, centrally defined field types can be used.
This allows for easy sharing of data types and easier computation.

.. _predefined_fields:

-----------------
Predefined Fields
-----------------

.. note:: Once stabilized, the common fields will be documented here.
