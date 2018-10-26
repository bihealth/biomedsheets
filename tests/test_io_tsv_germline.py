# -*- coding: utf-8 -*-
"""Tests for loading the compressed germline TSV file
"""

import io
import json
import textwrap

import pytest

from biomedsheets import io_tsv

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def tsv_sheet_germline_header():
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\tgermline_variants
    schema_version\tv1
    title\tExample germline study
    description\tThe study has two patients, P001 has one tumor sample, P002 has two

    [Data]
    patientName\tfatherName\tmotherName\tsex\tisAffected\tlibraryType\tfolderName\thpoTerms
    12_345\t12_346\t12_347\tM\tY\tWGS\t12_345\tHP:0009946,HP:0009899
    12_348\t12_346\t12_347\tM\tN\tWGS\t12_348\t.
    12_346\t.\t.\tM\tN\t.\t.\t.
    12_347\t.\t.\tF\tN\tWGS\t12_347\t.
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_germline_no_header():
    """Germline TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    patientName\tfatherName\tmotherName\tsex\tisAffected\tlibraryType\tfolderName\thpoTerms
    12_345\t12_346\t12_347\tM\tY\tWGS\t12_345\tHP:0009946,HP:0009899
    12_348\t12_346\t12_347\tM\tN\tWGS\t12_348\t.
    12_346\t.\t.\tM\tN\t.\t.\t.
    12_347\t.\t.\tF\tN\tWGS\t12_347\t.
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_germline_platform_name():
    """Germline TSV sheet with seqPlatform name"""
    f = io.StringIO(textwrap.dedent("""
    patientName\tfatherName\tmotherName\tsex\tisAffected\tlibraryType\tfolderName\thpoTerms\tseqPlatform
    12_347\t.\t.\tF\tN\tWGS\t12_347\t.\tIllumina
    12_347\t.\t.\tF\tN\tWGS\t12_347\t.\tPacBio
    """.lstrip()))
    return f


# Expected value for the germline sheet JSON with header
EXPECTED_GERMLINE_SHEET_JSON_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Example germline study",
    "description": "The study has two patients, P001 has one tumor sample, P002 has two",
    "extraInfoDefs": {
        "bioEntity": {
            "ncbiTaxon": {
                "docs": "Reference to NCBI taxonomy",
                "key": "taxon",
                "type": "string",
                "pattern": "^NCBITaxon_[1-9][0-9]*$"
            },
            "fatherPk": {
                "docs": "Primary key of mother",
                "key": "fatherPk",
                "type": "string"
            },
            "motherPk": {
                "docs": "Primary key of mother",
                "key": "motherPk",
                "type": "string"
            },
            "fatherName": {
                "docs": "secondary_id of father, used for construction only",
                "key": "fatherName",
                "type": "string"
            },
            "motherName": {
                "key": "motherName",
                "docs": "secondary_id of mother, used for construction only",
                "type": "string"
            },
            "sex": {
                "docs": "Biological sex of individual",
                "key": "sex",
                "type": "enum",
                "choices": [
                    "male",
                    "female",
                    "unknown"
                ]
            },
            "isAffected": {
                "docs": "Flag for marking individiual as (un-)affected",
                "key": "isAffected",
                "type": "enum",
                "choices": [
                    "affected",
                    "unaffected",
                    "unknown"
                ]
            },
            "hpoTerms": {
                "docs": "HPO terms for individual",
                "key": "hpoTerms",
                "type": "array",
                "entry": "string",
                "pattern": "^HPO:[0-9]+$"
            }
        },
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
        "12_345": {
            "pk": 1,
            "extraInfo": {
                "fatherName": "12_346",
                "motherName": "12_347",
                "sex": "male",
                "isAffected": "affected",
                "hpoTerms": [
                    "HP:0009946",
                    "HP:0009899"
                ],
                "ncbiTaxon": "NCBITaxon_9606",
                "fatherPk": 9,
                "motherPk": 10
            },
            "bioSamples": {
                "N1": {
                    "pk": 2,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_345",
                                        "libraryType": "WGS"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "12_348": {
            "pk": 5,
            "extraInfo": {
                "fatherName": "12_346",
                "motherName": "12_347",
                "sex": "male",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606",
                "fatherPk": 9,
                "motherPk": 10
            },
            "bioSamples": {
                "N1": {
                    "pk": 6,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 7,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 8,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_348",
                                        "libraryType": "WGS"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "12_346": {
            "pk": 9,
            "extraInfo": {
                "sex": "male",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {}
        },
        "12_347": {
            "pk": 10,
            "extraInfo": {
                "sex": "female",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 11,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 12,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_347",
                                        "libraryType": "WGS"
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

# Expected value for the germline sheet JSON without header
EXPECTED_GERMLINE_SHEET_JSON_NO_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Germline Sample Sheet",
    "description": "Sample Sheet constructed from germline compact TSV file",
    "extraInfoDefs": {
        "bioEntity": {
            "ncbiTaxon": {
                "docs": "Reference to NCBI taxonomy",
                "key": "taxon",
                "type": "string",
                "pattern": "^NCBITaxon_[1-9][0-9]*$"
            },
            "fatherPk": {
                "docs": "Primary key of mother",
                "key": "fatherPk",
                "type": "string"
            },
            "motherPk": {
                "docs": "Primary key of mother",
                "key": "motherPk",
                "type": "string"
            },
            "fatherName": {
                "docs": "secondary_id of father, used for construction only",
                "key": "fatherName",
                "type": "string"
            },
            "motherName": {
                "key": "motherName",
                "docs": "secondary_id of mother, used for construction only",
                "type": "string"
            },
            "sex": {
                "docs": "Biological sex of individual",
                "key": "sex",
                "type": "enum",
                "choices": [
                    "male",
                    "female",
                    "unknown"
                ]
            },
            "isAffected": {
                "docs": "Flag for marking individiual as (un-)affected",
                "key": "isAffected",
                "type": "enum",
                "choices": [
                    "affected",
                    "unaffected",
                    "unknown"
                ]
            },
            "hpoTerms": {
                "docs": "HPO terms for individual",
                "key": "hpoTerms",
                "type": "array",
                "entry": "string",
                "pattern": "^HPO:[0-9]+$"
            }
        },
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
        "12_345": {
            "pk": 1,
            "extraInfo": {
                "fatherName": "12_346",
                "motherName": "12_347",
                "sex": "male",
                "isAffected": "affected",
                "hpoTerms": [
                    "HP:0009946",
                    "HP:0009899"
                ],
                "ncbiTaxon": "NCBITaxon_9606",
                "fatherPk": 9,
                "motherPk": 10
            },
            "bioSamples": {
                "N1": {
                    "pk": 2,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_345",
                                        "libraryType": "WGS"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "12_348": {
            "pk": 5,
            "extraInfo": {
                "fatherName": "12_346",
                "motherName": "12_347",
                "sex": "male",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606",
                "fatherPk": 9,
                "motherPk": 10
            },
            "bioSamples": {
                "N1": {
                    "pk": 6,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 7,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 8,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_348",
                                        "libraryType": "WGS"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "12_346": {
            "pk": 9,
            "extraInfo": {
                "sex": "male",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {}
        },
        "12_347": {
            "pk": 10,
            "extraInfo": {
                "sex": "female",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 11,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 12,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_347",
                                        "libraryType": "WGS"
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


# Expected value when platform name is given
EXPECTED_GERMLINE_SHEET_JSON_PLATFORM_NAME = r"""
{
    "identifier": "file://<unknown>",
    "title": "Germline Sample Sheet",
    "description": "Sample Sheet constructed from germline compact TSV file",
    "extraInfoDefs": {
        "bioEntity": {
            "ncbiTaxon": {
                "docs": "Reference to NCBI taxonomy",
                "key": "taxon",
                "type": "string",
                "pattern": "^NCBITaxon_[1-9][0-9]*$"
            },
            "fatherPk": {
                "docs": "Primary key of mother",
                "key": "fatherPk",
                "type": "string"
            },
            "motherPk": {
                "docs": "Primary key of mother",
                "key": "motherPk",
                "type": "string"
            },
            "fatherName": {
                "docs": "secondary_id of father, used for construction only",
                "key": "fatherName",
                "type": "string"
            },
            "motherName": {
                "key": "motherName",
                "docs": "secondary_id of mother, used for construction only",
                "type": "string"
            },
            "sex": {
                "docs": "Biological sex of individual",
                "key": "sex",
                "type": "enum",
                "choices": [
                    "male",
                    "female",
                    "unknown"
                ]
            },
            "isAffected": {
                "docs": "Flag for marking individiual as (un-)affected",
                "key": "isAffected",
                "type": "enum",
                "choices": [
                    "affected",
                    "unaffected",
                    "unknown"
                ]
            },
            "hpoTerms": {
                "docs": "HPO terms for individual",
                "key": "hpoTerms",
                "type": "array",
                "entry": "string",
                "pattern": "^HPO:[0-9]+$"
            }
        },
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
        "12_347": {
            "pk": 1,
            "extraInfo": {
                "sex": "female",
                "isAffected": "unaffected",
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 2,
                    "extraInfo": {},
                    "testSamples": {
                        "DNA1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WGS1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "12_347",
                                        "libraryType": "WGS"
                                    }
                                },
                                "WGS2": {
                                    "pk": 6,
                                    "extraInfo": {
                                        "seqPlatform": "PacBio",
                                        "folderName": "12_347",
                                        "libraryType": "WGS"
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


def test_read_germline_sheet_header(tsv_sheet_germline_header):
    sheet = io_tsv.read_germline_tsv_sheet(tsv_sheet_germline_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_germline_sheet_no_header(tsv_sheet_germline_no_header):
    sheet = io_tsv.read_germline_tsv_sheet(tsv_sheet_germline_no_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_NO_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_germline_sheet_platform_name(tsv_sheet_germline_platform_name):
    sheet = io_tsv.read_germline_tsv_sheet(tsv_sheet_germline_platform_name)
    assert EXPECTED_GERMLINE_SHEET_JSON_PLATFORM_NAME == json.dumps(
        sheet.json_data, indent='    ')


def test_read_tumor_json_header(tsv_sheet_germline_header):
    sheet_struc = io_tsv.read_germline_tsv_json_data(tsv_sheet_germline_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_tumor_json_no_header(tsv_sheet_germline_no_header):
    sheet_struc = io_tsv.read_germline_tsv_json_data(tsv_sheet_germline_no_header)
    assert EXPECTED_GERMLINE_SHEET_JSON_NO_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_tumor_json_platform_name(tsv_sheet_germline_platform_name):
    sheet_struc = io_tsv.read_germline_tsv_json_data(tsv_sheet_germline_platform_name)
    assert EXPECTED_GERMLINE_SHEET_JSON_PLATFORM_NAME == json.dumps(
        sheet_struc, indent='    ')
