.. _schema_custom_fields:

============================
Custom Fields in TSV Schemas
============================

When using TSV ``cancer_matched`` or ``germline_variants`` schemas, you can use custom fields by filling the ``[Custom Fields]`` header in the TSV file.

-------
Example
-------

In the following example, we add the fields ``shimada4Class`` (an enum with two possible values), ``patientStatus`` (an enum with three different value), to the bio entity/patient, the field ``mycnCn`` (a floating point number greater than or equal to 0) to the test sample, and one boolean flag for each the test sample and NGS library (``testSampleFlag`` and ``ngsLibraryFlag``).

.. literalinclude:: code/cancer_sheet_ext.tsv
    :language: text

-----------
Field Types
-----------

The valid field types are given together with whether additional restrictions/information is allowed (``Y``) or even required (``R``).

===========  ======================  =======  =======  ====  =======  =======
Type         Summary                 minimum  maximum  unit  choices  pattern
===========  ======================  =======  =======  ====  =======  =======
``string``   a string value
``integer``  an integer              Y        Y        Y
``number``   a floating point value  Y        Y        Y
``boolean``  boolean flag
``enum``     one of several strings                          R
``regex``    regex-checked string                                     R
===========  ======================  =======  =======  ====  =======  =======
