.. _schema_custom_fields:

============================
Custom Fields in TSV Schemas
============================

When using TSV ``cancer_matched`` or ``germline_variants`` schemas, you can use custom fields by filling the ``[Custom Fields]`` header in the TSV file.

-------
Example
-------

In the following example, we add the fields ``shimada4Class`` (an enum with two possible values), ``patientStatus`` (an enum with three different value), to the bio entity/patient, the field ``mycnCn`` (a floating point number greater than or equal to 0) to the test sample, and one boolean flag for each the test sample and NGS library (``testSampleFlag`` and ``ngsLibraryFlag``).

::

    [Metadata]
    schema	cancer_matched
    schema_version	v1
    title	Example matched cancer tumor/normal study
    description	This example shows how to add custom fields

    [Custom Fields]
    key	annotatedEntity	docs	type	minimum	maximum	unit	choices	pattern
    shimada4Class	bioEntity	Shimada 4 classification	enum	.	.	.	favorable,unfavorable	.
    patientStatus	bioSample	Status of patient	enum	.	.	.	Deceased_from_disease,No_disease_event,Relapse_progression	.
    mycnCn	bioSample	MYCN copy number	number	0.0	.	.	.	.
    testSampleNice	testSample	Is test sample nice?	boolean	.	.	.	.	.
    ngsLibraryNice	ngsLibrary	Is NGS library nice?	boolean	.	.	.	.	.

    [Data]
    patientName	sampleName	isTumor	libraryType	folderName	shimada4Class	patientStatus	mycnCn	testSampleFlag	ngsLibraryFlag
    P001	N1	N	WES	P001-N1-DNA1-WES1	favorable	Deceased_from_disease	2.0	Y	N
    P001	T1	Y	WES	P001-T1-DNA1-WES1	favorable	Deceased_from_disease	2.0	N	Y
    P001	T1	Y	mRNA_seq	P001-T1-RNA1-mRNAseq1	favorable	Deceased_from_disease	2.0	Y	Y

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
