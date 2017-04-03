# -*- coding: utf-8 -*-
"""Tests for the shortcuts module with cancer sample sheet"""

import collections
import os
import pytest

from biomedsheets import io, ref_resolver, shortcuts


__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def sheet_cancer():
    """Return ``Sheet`` instance for the cancer example"""
    path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'data', 'example_cancer.json')
    sheet_json = io.json_loads_ordered(open(path, 'rt').read())
    resolver = ref_resolver.RefResolver(dict_class=collections.OrderedDict)
    return io.SheetBuilder(
        resolver.resolve('file://' + path, sheet_json)).run()


def test_sheet_donors(sheet_cancer):
    """Tests for the sheet's ``donors`` attribute"""
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    assert len(cancer_cases.donors) == 2
    assert str(cancer_cases.donors[0].bio_entity.pk) == '1'
    assert str(cancer_cases.donors[0].bio_entity.secondary_id) == 'EX_001'
    assert str(cancer_cases.donors[1].bio_entity.pk) == '8'
    assert str(cancer_cases.donors[1].bio_entity.secondary_id) == 'EX_002'


def test_donor_shortcuts(sheet_cancer):
    """Tests for shortcuts of the Donor objects"""
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    # First donor
    assert str(cancer_cases.donors[0].pk) == '1'
    assert str(cancer_cases.donors[0].secondary_id) == 'EX_001'
    assert str(cancer_cases.donors[0].name) == 'EX_001-000001'
    assert cancer_cases.donors[0].primary_pair
    assert len(cancer_cases.donors[0].all_pairs) == 1
    assert cancer_cases.donors[0].enabled
    assert not cancer_cases.donors[0].disabled
    # Second donor
    assert str(cancer_cases.donors[1].pk) == '8'
    assert str(cancer_cases.donors[1].secondary_id) == 'EX_002'
    assert str(cancer_cases.donors[1].name) == 'EX_002-000008'
    assert cancer_cases.donors[1].primary_pair
    assert len(cancer_cases.donors[1].all_pairs) == 1
    assert cancer_cases.donors[1].enabled
    assert not cancer_cases.donors[1].disabled


def test_sample_pair_shortcuts(sheet_cancer):
    """Test shortcuts of the ``CancerMatchedSamplePair`` objects

    Also tests the shortcuts of ``CancerSample``
    """
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    pair = cancer_cases.donors[0].primary_pair
    assert str(pair).startswith('CancerMatchedSamplePair(')
    assert pair.donor.name == 'EX_001-000001'
    # Tumor sample: test samples
    assert pair.tumor_sample.name == 'EX_001-T1-000005'
    assert pair.tumor_sample.dna_test_sample.name == 'EX_001-T1-DNA1-000006'
    assert pair.tumor_sample.dna_test_sample.assay_sample.name == 'EX_001-T1-DNA1-WES1-000007'
    assert pair.tumor_sample.rna_test_sample is None
    # Normal sample: test samples
    assert pair.normal_sample.name == 'EX_001-N1-000002'
    assert pair.normal_sample.dna_test_sample.name == 'EX_001-N1-DNA1-000003'
    assert pair.normal_sample.dna_test_sample.assay_sample.name == 'EX_001-N1-DNA1-WES1-000004'
    assert pair.normal_sample.rna_test_sample is None


def test_sample_pairs_all(sheet_cancer):
    """Test for the sheet's ``all_sample_pairs`` attribute"""
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    assert len(cancer_cases.all_sample_pairs) == 2
    assert cancer_cases.all_sample_pairs[0].donor.name == 'EX_001-000001'
    assert cancer_cases.all_sample_pairs[0].tumor_sample.name == 'EX_001-T1-000005'
    assert cancer_cases.all_sample_pairs[0].normal_sample.name == 'EX_001-N1-000002'
    assert cancer_cases.all_sample_pairs[1].tumor_sample.name == 'EX_002-T1-000012'
    assert cancer_cases.all_sample_pairs[1].normal_sample.name == 'EX_002-N1-000009'


def test_sample_pairs_primary(sheet_cancer):
    """Test for the sheet's ``primary_sample_pairs`` attribute"""
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    assert len(cancer_cases.primary_sample_pairs) == 2
    assert cancer_cases.primary_sample_pairs[0].donor.name == 'EX_001-000001'
    assert cancer_cases.primary_sample_pairs[0].tumor_sample.name == 'EX_001-T1-000005'
    assert cancer_cases.primary_sample_pairs[0].normal_sample.name == 'EX_001-N1-000002'
    assert cancer_cases.primary_sample_pairs[1].tumor_sample.name == 'EX_002-T1-000012'
    assert cancer_cases.primary_sample_pairs[1].normal_sample.name == 'EX_002-N1-000009'


def test_cancer_donor(sheet_cancer):
    """Test for ``CancerDonor``"""
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    donor = cancer_cases.donors[0]
    assert str(donor).startswith('CancerDonor(')
    assert donor.primary_pair
    assert donor.primary_pair.tumor_sample.name == 'EX_001-T1-000005'
    assert donor.primary_pair.normal_sample.name == 'EX_001-N1-000002'
    assert len(donor.all_pairs) == 1


def test_cancer_bio_sample(sheet_cancer):
    """Test for ``CancerBioSample``"""
    cancer_cases = shortcuts.CancerCaseSheet(sheet_cancer)
    tumor_sample = cancer_cases.donors[0].primary_pair.tumor_sample
    assert tumor_sample.name == 'EX_001-T1-000005'
    assert tumor_sample.is_tumor
    normal_sample = cancer_cases.donors[0].primary_pair.normal_sample
    assert normal_sample.name == 'EX_001-N1-000002'
    assert not normal_sample.is_tumor
