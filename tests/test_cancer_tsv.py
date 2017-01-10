# -*- coding: utf-8 -*-
"""Tests for loading the compressed cancer TSV file
"""

import collections
import io
import os
import pytest
import textwrap

from biomedsheets import io_tsv

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def tsv_sheet_cancer_header():
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema          cancer_matched
    schema_version  v1
    title           Example matched cancer tumor/normal study
    description     The study has two patients, P001 has one tumor sample, P002 has two

    [Data]
    patientName\tsampleName\tisCancer\tlibraryType\tfolderName
    P001\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P001\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P001\tT1\tY\tmRNA-seq\tP001-T1-RNA1-mRNAseq1
    P002\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-RNA1-RNAseq1
    P002\tT2\tY\tWES\tP001-T2-DNA1-WES1
    P002\tT2\tY\tmRNA-seq\tP001-T2-RNA1-mRNAseq1
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_cancer_no_header():
    """Cancer TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    patientName\tsampleName\tisCancer\tlibraryType\tfolderName
    P001\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P001\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P001\tT1\tY\tmRNA-seq\tP001-T1-RNA1-mRNAseq1
    P002\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-RNA1-RNAseq1
    P002\tT2\tY\tWES\tP001-T2-DNA1-WES1
    P002\tT2\tY\tmRNA-seq\tP001-T2-RNA1-mRNAseq1
    """.lstrip()))
    return f


def test_read_cancer_sheet_header(tsv_sheet_cancer_header):
    sheet = io_tsv.read_cancer_tsv(tsv_sheet_cancer_header)


def tsv_sheet_cancer_no_header(tsv_sheet_cancer_no_header):
    sheet = io_tsv.read_cancer_tsv(tsv_sheet_cancer_no_header)
