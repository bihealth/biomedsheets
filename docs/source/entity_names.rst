.. _entity_names:

============
Entity Names
============

The term **name**  is used for strings/tokens that represent a bio entity, bio sample, test sample, NGS library, etc. uniquely as part of file names.
Further, they are used where sample names or similar are required in file contents, e.g., in VCF or BAM files.
There are many possible strategies for this.

One important point is that the name must be unique, ideally globally.
For this reason, it is recommended to include the primary key in the name, such that read alignment files can be named ``{sample_name}.bam``, for example, and the file name is then unique throughout all systems.

-------------------------
Primary Key as Name Parts
-------------------------

The recommendation is to construct sample names etc. as ``{secondary_id}-{pk}`` where ``{secondary_id}`` is the **full** secondary id (e.g., ``PATIENT-T1-DNA1-WES1``) and ``pk`` is the integer primary key from the database.

Example file names:

- ``bwa.PATIENT-T1-DNA1-WES-0000001.bam``
- ``mutect.PATIENT-T1-DNA1-WES-0000001.vcf.gz``

----------------------
Secondary IDs as Names
----------------------

If no primary key has been assigned yet, a possible alternative strategy is to only use the secondary id.
This allows stable file names even if no stable primary key can be assigned.

.. note:: This is the recommendation for cubi_pipeline until we have a good id assignment system available.

Example file names:

- ``bwa.PATIENT-T1-DNA1-WES.bam``
- ``mutect.PATIENT-T1-DNA1-WES.vcf.gz``
