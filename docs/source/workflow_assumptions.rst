.. _workflow_assumptions:

====================
Workflow Assumptions
====================

One aim for the biomedical sheets is to drive workflow engines.
Currently, the main aim is supporting Snakemake but the described data structures and file formats are straightforward enough so they can be used by any engine.
Further, the schemas and workflows described below focus on high-throughput sequencing data.
Adaption to proteomics, metabolomics, etc. should be

One central assumption is that the overall workflow is modularized and each module deals with one "well-defined" processing step with "homogeneous data".
While this is not clearly defined, some examples are:

- A module that aligns HTS data from FASTQ files, supporting both RNA/DNA sequencing data and paired/single read data.
  Depending on the annotated test sample extraction type, read length, and paired/single mode, the aligner is chosen (BWA-MEM, BWA-ALN, STAR).
  The alignments are post-processed for masking duplicates, converted to BAM, sorted, indexed, and basic statistics are computed.
  The module is smart enough to create appropriate read groups in the BAM file for each pair of/single FASTQ files for correcting for lane bias.
- A module that takes HTS alignments in BAM data and performs "simple" variant calling, i.e., each sample is considered independently.
  The resulting VCF file is appropriately postprocessed (normalize indels, sort, bgzip, index).
  The module can also interpret donor-based pedigree information from the sample sheet and call variants for all samples from a family independently.
  If the pedigree mode is used then there is the restriction that there must be only one sample from each person in the family.
  Based on configuration, one or multiple of a set of supported variant callers can be used.
  A "cancer" mode performs variant calling of all samples of one donor together.
- A module that takes HTS alignments in BAM data and performs "somatic" variant calling.
  Each donor must have exactly one sample flagged as "is not cancer" and one or more samples flagged as "is cancer".
  For each cancer sample, the module performs paired somatic variant calling with one or more tools from a supported list.
  Only one library for each the control and the cancer samples is supported.
  The result is a VCF file for each tool and each cancer sample with the somatic variants.
  The VCF is appropriately preformatted.

Such typical modules are much easier to write and use if certain assumptions about the sample sheets hold.
Generally, the aim is to define a small core set of information that is required for the proper processing in workflows.
Schema-specific settings are described in the following chapters.
Core information is described here (somewhat redundant with the chapter :ref:`high_level_overview`).

-----------
Core Fields
-----------

- BioEntity
    - pk
    - secondaryId
- BioSample
    - pk
    - secondaryId
- TestSample
    - pk
    - secondaryId
    - extraction_type
- AssaySample
    - pk
    - secondaryId

---------------
HTS Core Fields
---------------

The following fields are required by all workflow steps that process HTS data.

- TestSample
    - extractionType -- extracted sample, currently one of {``DNA``, ``RNA``, ``other``}
- AssaySample
    - libraryType -- library type, currently one of {``WES``, ``WGS``, ``Panel_seq``, ``mRNA_seq``, ``total_RNA_seq``, ``other``}
