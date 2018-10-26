# -*- coding: utf-8 -*-
"""Tests for loading the compressed generic TSV file with custom fields
"""

import io
import json
import textwrap

import pytest

from biomedsheets import io_tsv

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def tsv_sheet_generic_header():
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\tgeneric
    schema_version\tv1
    title\tExample generic study
    description\tSimple example of a generic study sample sheet.

    [Custom Fields]
    key\tannotatedEntity\tdocs\ttype\tminimum\tmaximum\tunit\tchoices\tpattern
    ncbiTaxon\tbioEntity\tNCBI taxon ID\tpattern\t.\t.\t.\t.\t^NCBITaxon_[1-9][0-9]*$
    uberonCellSource\tbioSample\tUberon cell source\tpattern\t.\t.\t.\t.\t^UBERON:[0-9]+$
    testSampleConcentration\ttestSample\tConcentration in test sample\tnumber\t.\t.\tug/ml\t.\t.
    ngsLibraryConcentration\tngsLibrary\tConcentration in NGS library\tnumber\t.\t.\tug/ml\t.\t.

    [Data]
    bioEntity\tbioSample\ttestSample\tngsLibrary\textractionType\tlibraryType\tfolderName\tncbiTaxon\tuberonCellSource\ttestSampleConcentration\tngsLibraryConcentration
    E001\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS1-TS1-LIB1\tNCBITaxon_9606\tUBERON:0002107\t0.03\t0.001
    E001\tBS2\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS2-TS1-LIB1\tNCBITaxon_9606\tUBERON:0002107\t0.05\t0.002
    E002\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB1\tNCBITaxon_9606\tUBERON:0002107\t0.06\t0.004
    E002\tBS1\tTS1\tLIB2\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB2\tNCBITaxon_9606\tUBERON:0002107\t0.06\t0.005
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_generic_no_header():
    """Generic TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    bioEntity\tbioSample\ttestSample\tngsLibrary\textractionType\tlibraryType\tfolderName\tncbiTaxon\tuberonCellSource\ttestSampleConcentration\tngsLibraryConcentration
    E001\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS1-TS1-LIB1\tNCBITaxon_9606\tUBERON:0002107\t0.03\t0.001
    E001\tBS2\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS2-TS1-LIB1\tNCBITaxon_9606\tUBERON:0002107\t0.05\t0.002
    E002\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB1\tNCBITaxon_9606\tUBERON:0002107\t0.06\t0.004
    E002\tBS1\tTS1\tLIB2\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB2\tNCBITaxon_9606\tUBERON:0002107\t0.06\t0.005
    """.lstrip()))
    return f


# Expected value for the generic sheet JSON with header
EXPECTED_GENERIC_SHEET_JSON_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Example generic study",
    "description": "Simple example of a generic study sample sheet.",
    "extraInfoDefs": {
        "bioEntity": {
            "ncbiTaxon": {
                "docs": "NCBI taxon ID",
                "key": "ncbiTaxon",
                "type": "pattern",
                "pattern": "^NCBITaxon_[1-9][0-9]*$"
            }
        },
        "bioSample": {
            "uberonCellSource": {
                "docs": "Uberon cell source",
                "key": "uberonCellSource",
                "type": "pattern",
                "pattern": "^UBERON:[0-9]+$"
            }
        },
        "testSample": {
            "extractionType": {
                "docs": "Describes extracted",
                "key": "extractionType",
                "type": "enum",
                "choices": [
                    "DNA",
                    "RNA",
                    "other"
                ]
            },
            "testSampleConcentration": {
                "docs": "Concentration in test sample",
                "key": "testSampleConcentration",
                "type": "number",
                "unit": "ug/ml"
            }
        },
        "ngsLibrary": {
            "seqPlatform": {
                "docs": "Sequencing platform used",
                "key": "kitName",
                "type": "enum",
                "choices": [
                    "Illumina",
                    "PacBio",
                    "other"
                ]
            },
            "libraryType": {
                "docs": "Rough classificiation of the library type",
                "key": "libraryType",
                "type": "enum",
                "choices": [
                    "Panel-seq",
                    "WES",
                    "WGS",
                    "mRNA-seq",
                    "tRNA-seq",
                    "other"
                ]
            },
            "folderName": {
                "docs": "Name of folder with FASTQ files",
                "key": "folderName",
                "type": "string"
            },
            "ngsLibraryConcentration": {
                "docs": "Concentration in NGS library",
                "key": "ngsLibraryConcentration",
                "type": "number",
                "unit": "ug/ml"
            }
        }
    },
    "bioEntities": {
        "E001": {
            "pk": 1,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "BS1": {
                    "pk": 2,
                    "extraInfo": {
                        "uberonCellSource": "UBERON:0002107"
                    },
                    "testSamples": {
                        "TS1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "RNA",
                                "testSampleConcentration": 0.03
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E001-BS1-TS1-LIB1",
                                        "libraryType": "total_RNA_seq",
                                        "ngsLibraryConcentration": 0.001
                                    }
                                }
                            }
                        }
                    }
                },
                "BS2": {
                    "pk": 5,
                    "extraInfo": {
                        "uberonCellSource": "UBERON:0002107"
                    },
                    "testSamples": {
                        "TS1": {
                            "pk": 6,
                            "extraInfo": {
                                "extractionType": "RNA",
                                "testSampleConcentration": 0.05
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 7,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E001-BS2-TS1-LIB1",
                                        "libraryType": "total_RNA_seq",
                                        "ngsLibraryConcentration": 0.002
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "E002": {
            "pk": 8,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "BS1": {
                    "pk": 9,
                    "extraInfo": {
                        "uberonCellSource": "UBERON:0002107"
                    },
                    "testSamples": {
                        "TS1": {
                            "pk": 10,
                            "extraInfo": {
                                "extractionType": "RNA",
                                "testSampleConcentration": 0.06
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 11,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E002-BS1-TS1-LIB1",
                                        "libraryType": "total_RNA_seq",
                                        "ngsLibraryConcentration": 0.004
                                    }
                                },
                                "LIB2": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E002-BS1-TS1-LIB2",
                                        "libraryType": "total_RNA_seq",
                                        "ngsLibraryConcentration": 0.005
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}""".lstrip()


def test_read_generic_custom_fields_sheet_header(tsv_sheet_generic_header):
    sheet = io_tsv.read_generic_tsv_sheet(tsv_sheet_generic_header)
    assert EXPECTED_GENERIC_SHEET_JSON_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_generic_custom_fields_sheet_no_header(tsv_sheet_generic_no_header):
    with pytest.raises(io_tsv.TSVSheetException) as e_info:
        io_tsv.read_generic_tsv_json_data(tsv_sheet_generic_no_header)
    EXPECTED = (
        'Unexpected column seen in header row of body: ncbiTaxon, '
        'ngsLibraryConcentration, testSampleConcentration, uberonCellSource')
    assert EXPECTED == str(e_info.value)


def test_read_generic_sheet_custom_fields_json_header(tsv_sheet_generic_header):
    sheet_struc = io_tsv.read_generic_tsv_json_data(tsv_sheet_generic_header)
    assert EXPECTED_GENERIC_SHEET_JSON_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_generic_sheet_custom_fields_json_no_header(tsv_sheet_generic_no_header):
    with pytest.raises(io_tsv.TSVSheetException) as e_info:
        io_tsv.read_generic_tsv_json_data(tsv_sheet_generic_no_header)
    EXPECTED = (
        'Unexpected column seen in header row of body: ncbiTaxon, '
        'ngsLibraryConcentration, testSampleConcentration, uberonCellSource')
    assert EXPECTED == str(e_info.value)
