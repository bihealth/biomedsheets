# -*- coding: utf-8 -*-
"""Tests for loading succing cancer TSV files with custom fields
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
    schema\tcancer_matched
    schema_version\tv1
    title\tExample matched cancer tumor/normal study
    description\tThe study has two patients, P001 has one tumor sample, P002 has two

    [Custom Fields]
    key\tannotatedEntity\tdocs\ttype\tminimum\tmaximum\tunit\tchoices\tpattern
    ncbiTaxon\tbioEntity\tNCBI taxon ID\tpattern\t.\t.\t.\t.\t^NCBITaxon_[1-9][0-9]*$
    mycnCn\tbioSample\tMYCN copy number\tnumber\t0.0\t.\t.\t.\t.
    inssStage\tbioSample\tInternational Neuroblastoma Staging System\tenum\t.\t.\t.\t1,2,2A,2B,3,4,4S\t.
    shimada4Class\tbioEntity\tShimada 4 classification\tenum\t.\t.\t.\tfavorable,unfavorable\t.
    lohChr1p\tbioSample\tChromosome arm 1p deleted\tboolean\t.\t.\t.\t.\t.
    patientStatus\tbioSample\tStatus of patient\tenum\t.\t.\t.\tDeceased_from_disease,No_disease_event,Relapse_progression\t.
    timeToEventDays\tbioEntity\tTime to event in days\tinteger\t0\t.\td\t.\t.
    timeToDeathDays\tbioEntity\tTime to death in days\tinteger\t0\t.\td\t.\t.
    testSampleNice\ttestSample\tIs test sample nice?\tboolean\t.\t.\t.\t.\t.
    ngsLibraryNice\tngsLibrary\tIs NGS library nice?\tboolean\t.\t.\t.\t.\t.

    [Data]
    patientName\tsampleName\tisTumor\tlibraryType\tfolderName\tncbiTaxon\tmycnCn\tinssStage\tshimada4Class\tlohChr1p\tpatientStatus\ttimeToEventDays\ttimeToDeathDays\ttestSampleNice\tngsLibraryNice
    P001\tN1\tN\tWES\tP001-N1-DNA1-WES1\tNCBITaxon_9606\t.\t1\tfavorable\ttrue\tNo_disease_event\t.\t.\ttrue\ttrue
    P001\tT1\tY\tWES\tP001-T1-DNA1-WES1\tNCBITaxon_9606\t2\t1\tfavorable\ttrue\tNo_disease_event\t.\t.\ttrue\tfalse
    P001\tT1\tY\tmRNA_seq\tP001-T1-RNA1-mRNAseq1\tNCBITaxon_9606\t2\t1\tfavorable\ttrue\tNo_disease_event\t.\t.\ttrue\ttrue
    P002\tN1\tN\tWES\tP001-N1-DNA1-WES1\tNCBITaxon_9606\t.\t2\tunfavorable\ttrue\tRelapse_progression\t.\t.\tfalse\ttrue
    P002\tT1\tY\tWES\tP001-T1-DNA1-WES1\tNCBITaxon_9606\t.\t2\tunfavorable\ttrue\tRelapse_progression\t.\t.\ttrue\ttrue
    P002\tT1\tY\tWES\tP001-T1-RNA1-RNAseq1\tNCBITaxon_9606\t.\t2\tunfavorable\ttrue\tRelapse_progression\t.\t.\tfalse\tfalse
    P002\tT2\tY\tWES\tP001-T2-DNA1-WES1\tNCBITaxon_9606\t.\t3\tunfavorable\ttrue\tRelapse_progression\t.\t.\ttrue\ttrue
    P002\tT2\tY\tmRNA_seq\tP001-T2-RNA1-mRNAseq1\tNCBITaxon_9606\t.\t3\tunfavorable\ttrue\tRelapse_progression\t.\t.\ttrue\ttrue
    """.lstrip()))
    return f


@pytest.fixture
def tsv_sheet_cancer_no_header():
    """Tumor TSV sheet without header"""
    f = io.StringIO(textwrap.dedent("""
    patientName\tsampleName\tisTumor\tlibraryType\tfolderName\tncbiTaxon\tmycnCn\tinssStage\tshimada4Class\tlohChr1p\tpatientStatus\ttimeToEventDays\ttimeToDeathDays\ttestSampleNice\tngsLibraryNice
    P001\tN1\tN\tWES\tP001-N1-DNA1-WES1\tNCBITaxon_9606\t.\t1\tfavorable\ttrue\tNo_disease_event\t.\t.\ttrue\ttrue
    P001\tT1\tY\tWES\tP001-T1-DNA1-WES1\tNCBITaxon_9606\t2\t1\tfavorable\ttrue\tNo_disease_event\t.\t.\ttrue\tfalse
    P001\tT1\tY\tmRNA_seq\tP001-T1-RNA1-mRNAseq1\tNCBITaxon_9606\t2\t1\tfavorable\ttrue\tNo_disease_event\t.\t.\ttrue\ttrue
    P002\tN1\tN\tWES\tP001-N1-DNA1-WES1\tNCBITaxon_9606\t.\t2\tunfavorable\ttrue\tRelapse_progression\t.\t.\tfalse\ttrue
    P002\tT1\tY\tWES\tP001-T1-DNA1-WES1\tNCBITaxon_9606\t.\t2\tunfavorable\ttrue\tRelapse_progression\t.\t.\ttrue\ttrue
    P002\tT1\tY\tWES\tP001-T1-RNA1-RNAseq1\tNCBITaxon_9606\t.\t2\tunfavorable\ttrue\tRelapse_progression\t.\t.\tfalse\tfalse
    P002\tT2\tY\tWES\tP001-T2-DNA1-WES1\tNCBITaxon_9606\t.\t3\tunfavorable\ttrue\tRelapse_progression\t.\t.\ttrue\ttrue
    P002\tT2\tY\tmRNA_seq\tP001-T2-RNA1-mRNAseq1\tNCBITaxon_9606\t.\t3\tunfavorable\ttrue\tRelapse_progression\t.\t.\ttrue\ttrue
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
            },
            "shimada4Class": {
                "docs": "Shimada 4 classification",
                "key": "shimada4Class",
                "type": "enum",
                "choices": [
                    "favorable",
                    "unfavorable"
                ]
            },
            "timeToEventDays": {
                "docs": "Time to event in days",
                "key": "timeToEventDays",
                "type": "integer",
                "minimum": 0,
                "unit": "d"
            },
            "timeToDeathDays": {
                "docs": "Time to death in days",
                "key": "timeToDeathDays",
                "type": "integer",
                "minimum": 0,
                "unit": "d"
            }
        },
        "bioSample": {
            "isTumor": {
                "docs": "Boolean flag for distinguishing tumor/normal samples",
                "key": "isTumor",
                "type": "boolean"
            },
            "mycnCn": {
                "docs": "MYCN copy number",
                "key": "mycnCn",
                "type": "number",
                "minimum": 0.0
            },
            "inssStage": {
                "docs": "International Neuroblastoma Staging System",
                "key": "inssStage",
                "type": "enum",
                "choices": [
                    "1",
                    "2",
                    "2A",
                    "2B",
                    "3",
                    "4",
                    "4S"
                ]
            },
            "lohChr1p": {
                "docs": "Chromosome arm 1p deleted",
                "key": "lohChr1p",
                "type": "boolean"
            },
            "patientStatus": {
                "docs": "Status of patient",
                "key": "patientStatus",
                "type": "enum",
                "choices": [
                    "Deceased_from_disease",
                    "No_disease_event",
                    "Relapse_progression"
                ]
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
            "testSampleNice": {
                "docs": "Is test sample nice?",
                "key": "testSampleNice",
                "type": "boolean"
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
            "ngsLibraryNice": {
                "docs": "Is NGS library nice?",
                "key": "ngsLibraryNice",
                "type": "boolean"
            }
        }
    },
    "bioEntities": {
        "P001": {
            "pk": 1,
            "extraInfo": {
                "ncbiTaxon": "NCBITaxon_9606",
                "shimada4Class": "favorable"
            },
            "bioSamples": {
                "N1": {
                    "pk": 2,
                    "extraInfo": {
                        "inssStage": "1",
                        "lohChr1p": true,
                        "patientStatus": "No_disease_event",
                        "isTumor": false
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 3,
                            "extraInfo": {
                                "extractionType": "DNA",
                                "testSampleNice": true
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 4,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-N1-DNA1-WES1",
                                        "libraryType": "WES",
                                        "ngsLibraryNice": true
                                    }
                                }
                            }
                        }
                    }
                },
                "T1": {
                    "pk": 5,
                    "extraInfo": {
                        "isTumor": true,
                        "mycnCn": 2.0,
                        "inssStage": "1",
                        "lohChr1p": true,
                        "patientStatus": "No_disease_event"
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 6,
                            "extraInfo": {
                                "extractionType": "DNA",
                                "testSampleNice": true
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 7,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-DNA1-WES1",
                                        "libraryType": "WES",
                                        "ngsLibraryNice": false
                                    }
                                }
                            }
                        },
                        "RNA1": {
                            "pk": 8,
                            "extraInfo": {
                                "extractionType": "RNA",
                                "testSampleNice": true
                            },
                            "ngsLibraries": {
                                "mRNA_seq1": {
                                    "pk": 9,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-RNA1-mRNAseq1",
                                        "libraryType": "mRNA_seq",
                                        "ngsLibraryNice": true
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
                "ncbiTaxon": "NCBITaxon_9606",
                "shimada4Class": "unfavorable"
            },
            "bioSamples": {
                "N1": {
                    "pk": 11,
                    "extraInfo": {
                        "inssStage": "2",
                        "lohChr1p": true,
                        "patientStatus": "Relapse_progression",
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
                                        "libraryType": "WES",
                                        "ngsLibraryNice": true
                                    }
                                }
                            }
                        }
                    }
                },
                "T1": {
                    "pk": 14,
                    "extraInfo": {
                        "isTumor": true,
                        "inssStage": "2",
                        "lohChr1p": true,
                        "patientStatus": "Relapse_progression"
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 15,
                            "extraInfo": {
                                "extractionType": "DNA",
                                "testSampleNice": true
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 16,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-DNA1-WES1",
                                        "libraryType": "WES",
                                        "ngsLibraryNice": true
                                    }
                                },
                                "WES2": {
                                    "pk": 18,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T1-RNA1-RNAseq1",
                                        "libraryType": "WES",
                                        "ngsLibraryNice": false
                                    }
                                }
                            }
                        }
                    }
                },
                "T2": {
                    "pk": 19,
                    "extraInfo": {
                        "isTumor": true,
                        "inssStage": "3",
                        "lohChr1p": true,
                        "patientStatus": "Relapse_progression"
                    },
                    "testSamples": {
                        "DNA1": {
                            "pk": 20,
                            "extraInfo": {
                                "extractionType": "DNA",
                                "testSampleNice": true
                            },
                            "ngsLibraries": {
                                "WES1": {
                                    "pk": 21,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T2-DNA1-WES1",
                                        "libraryType": "WES",
                                        "ngsLibraryNice": true
                                    }
                                }
                            }
                        },
                        "RNA1": {
                            "pk": 22,
                            "extraInfo": {
                                "extractionType": "RNA",
                                "testSampleNice": true
                            },
                            "ngsLibraries": {
                                "mRNA_seq1": {
                                    "pk": 23,
                                    "extraInfo": {
                                        "seqPlatform": "Illumina",
                                        "folderName": "P001-T2-RNA1-mRNAseq1",
                                        "libraryType": "mRNA_seq",
                                        "ngsLibraryNice": true
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


def test_read_cancer_sheet_custom_fields_header(tsv_sheet_cancer_header):
    sheet = io_tsv.read_cancer_tsv_sheet(tsv_sheet_cancer_header)
    assert EXPECTED_CANCER_SHEET_JSON_HEADER == json.dumps(
        sheet.json_data, indent='    ')


def test_read_cancer_sheet_custom_fields_no_header(tsv_sheet_cancer_no_header):
    with pytest.raises(io_tsv.TSVSheetException) as e_info:
        io_tsv.read_cancer_tsv_sheet(tsv_sheet_cancer_no_header)
    EXPECTED = (
        'Unexpected column seen in header row of body: inssStage, lohChr1p, '
        'mycnCn, ncbiTaxon, ngsLibraryNice, patientStatus, shimada4Class, '
        'testSampleNice, timeToDeathDays, timeToEventDays')
    assert EXPECTED == str(e_info.value)


def test_read_cancer_json_custom_fields_header(tsv_sheet_cancer_header):
    sheet_struc = io_tsv.read_cancer_tsv_json_data(tsv_sheet_cancer_header)
    assert EXPECTED_CANCER_SHEET_JSON_HEADER == json.dumps(
        sheet_struc, indent='    ')


def test_read_cancer_json_custom_fields_no_header(tsv_sheet_cancer_no_header):
    with pytest.raises(io_tsv.TSVSheetException) as e_info:
        io_tsv.read_cancer_tsv_json_data(tsv_sheet_cancer_no_header)
    EXPECTED = (
        'Unexpected column seen in header row of body: inssStage, lohChr1p, '
        'mycnCn, ncbiTaxon, ngsLibraryNice, patientStatus, shimada4Class, '
        'testSampleNice, timeToDeathDays, timeToEventDays')
    assert EXPECTED == str(e_info.value)
