# -*- coding: utf-8 -*-
"""Tests for loading the compressed cancer TSV file
"""

import io
import json
import textwrap

import pytest

from biomedsheets import io_tsv

__author__ = 'Manuel Holtgrewe <manuel.holtgrewe@bihealth.de>'


@pytest.fixture
def tsv_sheet_cancer_header():
    f = io.StringIO(textwrap.dedent("""
    [Metadata]
    schema\ttumor_matched
    schema_version\tv1
    title\tExample matched cancer tumor/normal study
    description\tThe study has two patients, P001 has one tumor sample, P002 has two

    [Data]
    patientName\tsampleName\tisTumor\tlibraryType\tfolderName
    P001\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P001\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P001\tT1\tY\tmRNA_seq\tP001-T1-RNA1-mRNAseq1
    P002\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-RNA1-RNAseq1
    P002\tT2\tY\tWES\tP001-T2-DNA1-WES1
    P002\tT2\tY\tmRNA_seq\tP001-T2-RNA1-mRNAseq1
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_cancer_no_header():
    """Tumor TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    patientName\tsampleName\tisTumor\tlibraryType\tfolderName
    P001\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P001\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P001\tT1\tY\tmRNA_seq\tP001-T1-RNA1-mRNAseq1
    P002\tN1\tN\tWES\tP001-N1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-DNA1-WES1
    P002\tT1\tY\tWES\tP001-T1-RNA1-RNAseq1
    P002\tT2\tY\tWES\tP001-T2-DNA1-WES1
    P002\tT2\tY\tmRNA_seq\tP001-T2-RNA1-mRNAseq1
    """.lstrip()))
    return f


# Expected value for the cancer sheet JSON with header
EXPECTED_CANCER_SHEET_JSON_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Example matched cancer tumor/normal study",
    "description": "The study has two patients, P001 has one tumor sample, P002 has two",
    "extraInfoDefs": {
        "bioEntity": {
            "ncbiTaxon": {
                "docs": "Reference to NCBI taxonomy",
                "key": "taxon",
                "type": "string",
                "pattern": "^NCBITaxon_[1-9][0-9]*$"
            }
        },
        "bioSample": {
            "isTumor": {
                "docs": "Boolean flag for distinguishing tumor/normal samples",
                "key": "isTumor",
                "type": "boolean"
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
        "P001": {
            "pk": 1,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 2,
                    "extraInfo": {
                        "isTumor": false
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-N1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        }
                    }
                },
                "T1": {
                    "pk": 5,
                    "extraInfo": {
                        "isTumor": true
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 6,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 7,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        },
                        "RNA1": {
                            "pk": 8,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "mRNA_seq1": {
                                    "pk": 9,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-RNA1-mRNAseq1",
                                        "libraryType": "mRNA_seq"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "P002": {
            "pk": 10,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 11,
                    "extraInfo": {
                        "isTumor": false
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 12,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-N1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        }
                    }
                },
                "T1": {
                    "pk": 14,
                    "extraInfo": {
                        "isTumor": true
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 15,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 16,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                },
                                "WES2": {
                                    "pk": 18,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-RNA1-RNAseq1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        }
                    }
                },
                "T2": {
                    "pk": 19,
                    "extraInfo": {
                        "isTumor": true
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 20,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 21,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T2-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        },
                        "RNA1": {
                            "pk": 22,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "mRNA_seq1": {
                                    "pk": 23,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T2-RNA1-mRNAseq1",
                                        "libraryType": "mRNA_seq"
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

# Expected value for the cancer sheet JSON without header
EXPECTED_CANCER_SHEET_JSON_NO_HEADER = r"""
{
    "identifier": "file://<unknown>",
    "title": "Cancer Sample Sheet",
    "description": "Sample Sheet constructed from cancer matched samples compact TSV file",
    "extraInfoDefs": {
        "bioEntity": {
            "ncbiTaxon": {
                "docs": "Reference to NCBI taxonomy",
                "key": "taxon",
                "type": "string",
                "pattern": "^NCBITaxon_[1-9][0-9]*$"
            }
        },
        "bioSample": {
            "isTumor": {
                "docs": "Boolean flag for distinguishing tumor/normal samples",
                "key": "isTumor",
                "type": "boolean"
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
        "P001": {
            "pk": 1,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 2,
                    "extraInfo": {
                        "isTumor": false
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-N1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        }
                    }
                },
                "T1": {
                    "pk": 5,
                    "extraInfo": {
                        "isTumor": true
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 6,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 7,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        },
                        "RNA1": {
                            "pk": 8,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "mRNA_seq1": {
                                    "pk": 9,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-RNA1-mRNAseq1",
                                        "libraryType": "mRNA_seq"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "P002": {
            "pk": 10,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606"
            },
            "bioSamples": {
                "N1": {
                    "pk": 11,
                    "extraInfo": {
                        "isTumor": false
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 12,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 13,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-N1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        }
                    }
                },
                "T1": {
                    "pk": 14,
                    "extraInfo": {
                        "isTumor": true
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 15,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 16,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                },
                                "WES2": {
                                    "pk": 18,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-RNA1-RNAseq1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        }
                    }
                },
                "T2": {
                    "pk": 19,
                    "extraInfo": {
                        "isTumor": true
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 20,
                            "extraInfo": {
                                "extractionType": "DNA"
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 21,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T2-DNA1-WES1",
                                        "libraryType": "WES"
                                    }
                                }
                            }
                        },
                        "RNA1": {
                            "pk": 22,
                            "extraInfo": {
                                "extractionType": "RNA"
                            },
                            "ngsLibraries": {
                                "mRNA_seq1": {
                                    "pk": 23,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T2-RNA1-mRNAseq1",
                                        "libraryType": "mRNA_seq"
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


def test_read_cancer_sheet_header(tsv_sheet_cancer_header):
    sheet = io_tsv.read_cancer_tsv_sheet(tsv_sheet_cancer_header)
    assert EXPECTED_CANCER_SHEET_JSON_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_cancer_sheet_no_header(tsv_sheet_cancer_no_header):
    sheet = io_tsv.read_cancer_tsv_sheet(tsv_sheet_cancer_no_header)
    assert EXPECTED_CANCER_SHEET_JSON_NO_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_tumor_json_header(tsv_sheet_cancer_header):
    sheet_struc = io_tsv.read_cancer_tsv_json_data(tsv_sheet_cancer_header)
    assert EXPECTED_CANCER_SHEET_JSON_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_tumor_json_no_header(tsv_sheet_cancer_no_header):
    sheet_struc = io_tsv.read_cancer_tsv_json_data(tsv_sheet_cancer_no_header)
    assert EXPECTED_CANCER_SHEET_JSON_NO_HEADER == json.dumps(
        sheet_struc, indent='    ')
