# -*- coding: utf-8 -*-
"""Tests for loading the compressed generic TSV file
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

    [Data]
    bioEntity\tbioSample\ttestSample\tngsLibrary\textractionType\tlibraryType\tfolderName
    E001\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS1-TS1-LIB1
    E001\tBS2\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS2-TS1-LIB1
    E002\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB1
    E002\tBS1\tTS1\tLIB2\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB2
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_generic_no_header():
    """Generic TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    bioEntity\tbioSample\ttestSample\tngsLibrary\textractionType\tlibraryType\tfolderName
    E001\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS1-TS1-LIB1
    E001\tBS2\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE001-BS2-TS1-LIB1
    E002\tBS1\tTS1\tLIB1\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB1
    E002\tBS1\tTS1\tLIB2\tRNA\ttotal_RNA_seq\tE002-BS1-TS1-LIB2
    """.lstrip()))
    return f


# Expected value for the generic sheet JSON with header
EXPECTED_GENERIC_SHEET_JSON_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Example generic study",
    "description": "Simple example of a generic study sample sheet.",
    "extraInfoDefs": {
        "bioEntity": {},
        "bioSample": {},
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
            }
        }
    },
    "bioEntities": {
        "E001": {
            "pk": 1,
            "extraInfo": {},
            "bioSamples": {
                "BS1": {
                    "pk": 2,
                    "extraInfo": {},
                    "testSamples": {
                        "TS1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E001-BS1-TS1-LIB1",
                                        "libraryType": "total_RNA_seq"
                                    }
                                }
                            }
                        }
                    }
                },
                "BS2": {
                    "pk": 5,
                    "extraInfo": {},
                    "testSamples": {
                        "TS1": {
                            "pk": 6,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 7,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E001-BS2-TS1-LIB1",
                                        "libraryType": "total_RNA_seq"
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
            "extraInfo": {},
            "bioSamples": {
                "BS1": {
                    "pk": 9,
                    "extraInfo": {},
                    "testSamples": {
                        "TS1": {
                            "pk": 10,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 11,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E002-BS1-TS1-LIB1",
                                        "libraryType": "total_RNA_seq"
                                    }
                                },
                                "LIB2": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E002-BS1-TS1-LIB2",
                                        "libraryType": "total_RNA_seq"
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

# Expected value for the generic sheet JSON without header
EXPECTED_GENERIC_SHEET_JSON_NO_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Generic Sample Sheet",
    "description": "Sample Sheet constructed from generic compact TSV file",
    "extraInfoDefs": {
        "bioEntity": {},
        "bioSample": {},
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
            }
        }
    },
    "bioEntities": {
        "E001": {
            "pk": 1,
            "extraInfo": {},
            "bioSamples": {
                "BS1": {
                    "pk": 2,
                    "extraInfo": {},
                    "testSamples": {
                        "TS1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E001-BS1-TS1-LIB1",
                                        "libraryType": "total_RNA_seq"
                                    }
                                }
                            }
                        }
                    }
                },
                "BS2": {
                    "pk": 5,
                    "extraInfo": {},
                    "testSamples": {
                        "TS1": {
                            "pk": 6,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 7,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E001-BS2-TS1-LIB1",
                                        "libraryType": "total_RNA_seq"
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
            "extraInfo": {},
            "bioSamples": {
                "BS1": {
                    "pk": 9,
                    "extraInfo": {},
                    "testSamples": {
                        "TS1": {
                            "pk": 10,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "LIB1": {
                                    "pk": 11,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E002-BS1-TS1-LIB1",
                                        "libraryType": "total_RNA_seq"
                                    }
                                },
                                "LIB2": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "E002-BS1-TS1-LIB2",
                                        "libraryType": "total_RNA_seq"
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


def test_read_generic_sheet_header(tsv_sheet_generic_header):
    sheet = io_tsv.read_generic_tsv_sheet(tsv_sheet_generic_header)
    assert EXPECTED_GENERIC_SHEET_JSON_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_generic_sheet_no_header(tsv_sheet_generic_no_header):
    sheet = io_tsv.read_generic_tsv_sheet(tsv_sheet_generic_no_header)
    assert EXPECTED_GENERIC_SHEET_JSON_NO_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_tumor_json_header(tsv_sheet_generic_header):
    sheet_struc = io_tsv.read_generic_tsv_json_data(tsv_sheet_generic_header)
    assert EXPECTED_GENERIC_SHEET_JSON_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_tumor_json_no_header(tsv_sheet_generic_no_header):
    sheet_struc = io_tsv.read_generic_tsv_json_data(tsv_sheet_generic_no_header)
    assert EXPECTED_GENERIC_SHEET_JSON_NO_HEADER == json.dumps(
        sheet_struc, indent='    ')
