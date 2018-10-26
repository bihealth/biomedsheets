# -*- coding: utf-8 -*-
"""Tests for the shortcuts module with germline sample sheet"""

import io
import pytest
import textwrap

from biomedsheets import naming, io_tsv, shortcuts


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def tsv_sheet_germline():
    """Example TSV germline sheet"""
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\tgermline_variants
    schema_version\tv1
    title\tExample germline study
    description\tSimple study with two trios

    [Data]
    patientName\tfatherName\tmotherName\tsex\tisAffected\tlibraryType\tfolderName\thpoTerms
    index1\tfather1\tmother1\tM\tY\tWES\tindex1\t.
    father1\t0\t0\tM\tN\tWES\tfather1\t.
    mother1\t0\t0\tM\tN\tWES\tmother1\t.
    index2\tfather2\tmother2\tM\tY\tWES\tindex2\t.
    father2\t0\t0\tM\tN\tWES\tfather2\t.
    mother2\t0\t0\tM\tN\tWES\tmother2\t.
    """.lstrip()))
    return f


@pytest.fixture
def sheet_germline(tsv_sheet_germline):
    """Return ``Sheet`` instance for the germline example"""
    return shortcuts.GermlineCaseSheet(io_tsv.read_germline_tsv_sheet(tsv_sheet_germline))


@pytest.fixture
def tsv_sheet_germline_two_libs():
    """Example TSV germline sheet"""
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\tgermline_variants
    schema_version\tv1
    title\tExample germline study
    description\tsingle individual, sequenced twice

    [Data]
    patientName\tfatherName\tmotherName\tsex\tisAffected\tlibraryType\tfolderName\thpoTerms
    donor\t0\t0\tM\tN\tWES\tdonor-a\t.
    donor\t0\t0\tM\tN\tWES\tdonor-b\t.
    """.lstrip()))
    return f


@pytest.fixture
def sheet_germline_two_libs(tsv_sheet_germline_two_libs):
    """Return ``Sheet`` instance for the germline example with two libraries"""
    return shortcuts.GermlineCaseSheet(io_tsv.read_germline_tsv_sheet(
        tsv_sheet_germline_two_libs, naming_scheme=naming.NAMING_ONLY_SECONDARY_ID))


@pytest.fixture
def tsv_sheet_germline_two_bio_samples():
    """Example TSV germline sheet"""
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\tgermline_variants
    schema_version\tv1
    title\tExample germline study
    description\tsingle individual, sequenced twice

    [Data]
    patientName\tfatherName\tmotherName\tsex\tisAffected\tbioSample\tlibraryType\tfolderName\thpoTerms
    donor\t0\t0\tM\tN\tN1\tWES\tdonor-a\t.
    donor\t0\t0\tM\tN\tN2\tWES\tdonor-b\t.
    """.lstrip()))
    return f


@pytest.fixture
def sheet_germline_two_bio_samples(tsv_sheet_germline_two_bio_samples):
    """Return ``Sheet`` instance for the germline example with two bio_samples"""
    return shortcuts.GermlineCaseSheet(io_tsv.read_germline_tsv_sheet(
        tsv_sheet_germline_two_bio_samples, naming_scheme=naming.NAMING_ONLY_SECONDARY_ID))


@pytest.fixture
def tsv_sheet_germline_two_test_samples():
    """Example TSV germline sheet"""
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\tgermline_variants
    schema_version\tv1
    title\tExample germline study
    description\tsingle individual, sequenced twice

    [Data]
    patientName\tfatherName\tmotherName\tsex\tisAffected\ttestSample\tlibraryType\tfolderName\thpoTerms
    donor\t0\t0\tM\tN\tDNA1\tWES\tdonor-a\t.
    donor\t0\t0\tM\tN\tDNA2\tWES\tdonor-b\t.
    """.lstrip()))
    return f


@pytest.fixture
def sheet_germline_two_test_samples(tsv_sheet_germline_two_test_samples):
    """Return ``Sheet`` instance for the germline example with two test_samples"""
    return shortcuts.GermlineCaseSheet(io_tsv.read_germline_tsv_sheet(
        tsv_sheet_germline_two_test_samples, naming_scheme=naming.NAMING_ONLY_SECONDARY_ID))


def test_germline_case_sheet(sheet_germline):
    """Tests for the germline case sheet"""
    sheet = sheet_germline
    assert len(sheet.donors) == 6
    assert sheet.cohort
    assert len(sheet.index_ngs_library_to_pedigree) == 2
    assert list(sheet.index_ngs_library_to_pedigree) == [
        'index1-N1-DNA1-WES1-000004', 'index2-N1-DNA1-WES1-000016']
    assert len(sheet.index_ngs_library_to_donor) == 6
    assert list(sheet.library_name_to_library) == [
        'index1-N1-DNA1-WES1-000004',
        'father1-N1-DNA1-WES1-000008',
        'mother1-N1-DNA1-WES1-000012',
        'index2-N1-DNA1-WES1-000016',
        'father2-N1-DNA1-WES1-000020',
        'mother2-N1-DNA1-WES1-000024',
    ]


def test_germline_case_sheet_two_libs(sheet_germline_two_libs):
    """Tests for the germline case sheet with two libraries"""
    sheet = sheet_germline_two_libs
    assert len(sheet.donors) == 1
    assert len(sheet.index_ngs_library_to_pedigree) == 1
    assert list(sheet.index_ngs_library_to_pedigree) == ['donor-N1-DNA1-WES1']
    assert len(sheet.index_ngs_library_to_donor) == 1
    assert list(sheet.library_name_to_library) == [
        'donor-N1-DNA1-WES1',
        'donor-N1-DNA1-WES2'
    ]


def test_germline_case_sheet_two_bio_samples(sheet_germline_two_bio_samples):
    """Tests for the germline case sheet with two bio samples"""
    sheet = sheet_germline_two_bio_samples
    assert len(sheet.donors) == 1
    assert len(sheet.index_ngs_library_to_pedigree) == 1
    assert list(sheet.index_ngs_library_to_pedigree) == ['donor-N1-DNA1-WES1']
    assert len(sheet.index_ngs_library_to_donor) == 1
    assert list(sheet.library_name_to_library) == [
        'donor-N1-DNA1-WES1',
        'donor-N2-DNA1-WES1'
    ]


def test_germline_case_sheet_two_test_samples(sheet_germline_two_test_samples):
    """Tests for the germline case sheet with two test samples"""
    sheet = sheet_germline_two_test_samples
    assert len(sheet.donors) == 1
    assert len(sheet.index_ngs_library_to_pedigree) == 1
    assert list(sheet.index_ngs_library_to_pedigree) == ['donor-N1-DNA1-WES1']
    assert len(sheet.index_ngs_library_to_donor) == 1
    assert list(sheet.library_name_to_library) == [
        'donor-N1-DNA1-WES1',
        'donor-N1-DNA2-WES1'
    ]


def test_germline_donor(sheet_germline):
    """Tests for the GermlineDonor objects"""
    index1 = sheet_germline.cohort.indices[0]
    assert index1.father_pk == '5'
    assert index1.father
    assert index1.father.name == 'father1-000005'
    assert index1.mother_pk == '9'
    assert index1.mother
    assert index1.mother.name == 'mother1-000009'


def test_pedigree(sheet_germline):
    """Tests for Pedigree objects"""
    pedigree = sheet_germline.cohort.pedigrees[0]
    assert str(pedigree).startswith('Pedigree(')
    assert [d.name for d in pedigree.donors] == [
        'index1-000001', 'father1-000005', 'mother1-000009']
    assert pedigree.index.name == 'index1-000001'
    assert [d.name for d in pedigree.affecteds] == ['index1-000001']
    assert [d.name for d in pedigree.founders] == ['father1-000005', 'mother1-000009']
    assert list(pedigree.name_to_donor) == ['index1-000001', 'father1-000005', 'mother1-000009']
    assert list(pedigree.pk_to_donor) == ['1', '5', '9']
    assert list(pedigree.secondary_id_to_donor) == ['index1', 'father1', 'mother1']


def test_cohorts(sheet_germline):
    """Tests for Cohort object"""
    cohort = sheet_germline.cohort
    assert len(cohort.pedigrees) == 2
    assert set(d.name for d in cohort.indices) == {'index1-000001', 'index2-000013'}
    assert set(d.name for d in cohort.affecteds) == {'index1-000001', 'index2-000013'}
    assert set(cohort.name_to_pedigree) == {
        'father1-000005',
        'father2-000017',
        'index1-000001',
        'index2-000013',
        'mother1-000009',
        'mother2-000021'}
    assert set(cohort.pk_to_pedigree) == {1, 17, 5, 21, 9, 13}
    assert set(cohort.secondary_id_to_pedigree) == {'index1', 'father1', 'index2', 'mother1', 'father2', 'mother2'}
    assert set(cohort.name_to_donor) == {
        'father1-000005',
        'father2-000017',
        'index1-000001',
        'index2-000013',
        'mother1-000009',
        'mother2-000021'}
    assert set(cohort.secondary_id_to_donor) == {'index1', 'father1', 'mother2', 'index2', 'mother1', 'father2'}
    assert cohort.member_count == 6
    assert cohort.pedigree_count == 2
