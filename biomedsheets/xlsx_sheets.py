# -*- coding: utf-8 -*-
"""Support code for writing, reading, and interpreting XLS-based sample
sheets
"""

import sys

from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment


class RareDisaseSheetCreator:
    """Create rare disease XLSX sheet"""

    def run(self, output_path):
        """Create empty sheet for rare disease scheme to ``path``"""
        wb = Workbook()
        ws = wb.active
        self._setup_sheet(ws)
        wb.save(output_path)

    def _setup_sheet(self, ws):
        ws.title = 'Germline Sample Sheet'
        self._setup_header(ws)
        self._setup_validation(ws)
        self._add_example_rows(ws)
        self._setup_column_sizes(ws)
        ws.freeze_panes = ws['A2']

    def _setup_header(self, ws):
        ws.append((
            'DONOR ID',
            'FATHER ID',
            'MOTHER ID',
            'SEX',
            'AFFECTED',
            'BIO SAMPLE ID',
            'SAMPLE TYPE',
            'TEST SAMPLE ID',
            'LIBRARY ID',
            'LIBRARY TYPE',
            'KIT TYPE',
            'KIT VERSION',
        ))

    def _setup_column_sizes(self, ws):
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max((dims.get(cell.column, 0),
                                            len(cell.value)))
        for col, value in dims.items():
            ws.column_dimensions[col].width = dims[col]

    def _setup_validation(self, ws):
        """Setup data validation, creates list cells"""
        # Column: D/sex
        dv_sex = DataValidation(
            type='list', formula1='"male,female,unknown"', allow_blank=True)
        dv_sex.ranges.append('D2:D1000')
        dv_sex.error = 'Sex must be one of male, female, unknown'
        dv_sex.errorTitle = 'Invalid sex'
        ws.add_data_validation(dv_sex)
        # Column: E/affected state
        dv_affected = DataValidation(
            type='list', formula1='"yes,no,unknown"', allow_blank=True)
        dv_affected.ranges.append('E2:E1000')
        dv_affected.error = 'Affected must be one of yes, no, unknown'
        dv_affected.errorTitle = 'Invalid affected'
        ws.add_data_validation(dv_affected)
        # Column: G/sample type
        dv_source = DataValidation(
            type='list', formula1='"blood,saliva,unknown,other"',
            allow_blank=True)
        dv_source.ranges.append('G2:G1000')
        dv_source.error = (
            'Sample source must be one of blood, saliva, unknown, other')
        dv_source.errorTitle = 'Invalid sample source'
        ws.add_data_validation(dv_source)
        # Column: J/library type
        dv_library = DataValidation(
            type='list',
            formula1=('"Agilent_SureSelect_Human_All_Exon,'
                      'Illumina_TruSeq_DNA_PCR_Free_Library_Preparation_Kit,'
                      'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit,'
                      'Illumina_TruSeq_Exome"'),
            allow_blank=True)
        dv_library.ranges.append('J2:J1000')
        dv_library.error = 'Kit type must be in the list'
        dv_library.errorTitle = 'Kit type'

    def _add_example_rows(self, ws):
        """Add example rows to sheet"""
        ws.append(('01_001', '01_002', '01_003', 'male', 'affected',
                   '01_001-S1', 'blood',
                   '01_001-S1-DNA1',
                   '01_001-S1-DNA1-WES1', 'WES',
                   'Agilent_SureSelect_Human_All_Exon', 'V6'))
        ws.append(('01_002', '', '', 'male', 'unaffected',
                   '01_001-S1', 'blood',
                   '01_001-S1-DNA1',
                   '01_001-S1-DNA1-WES1', 'WES',
                   'Agilent_SureSelect_Human_All_Exon', 'V6'))
        ws.append(('01_003', '', '', 'female', 'unaffected',
                   '01_001-S1', 'blood',
                   '01_001-S1-DNA1',
                   '01_001-S1-DNA1-WES1', 'WES',
                   'Agilent_SureSelect_Human_All_Exon', 'V6'))


class CancerMatchedSheetCreator:
    """Create cancer matched tumor/normal sheet"""

    def run(self, output_path):
        """Create empty sheet for cancer matched study schema to ``path``"""
        wb = Workbook()
        ws = wb.active
        self._setup_sheet(ws)
        wb.save(output_path)

    def _setup_sheet(self, ws):
        ws.title = 'Cancer Matched Sample Sheet'
        self._setup_header(ws)
        self._setup_validation(ws)
        self._add_example_rows(ws)
        self._setup_column_sizes(ws)
        ws.freeze_panes = ws['A2']

    def _setup_header(self, ws):
        ws.append((
            'DONOR ID',
            'SEX',
            'BIO SAMPLE ID',
            'ICD-10 ENTRY (2016)',
            'IS CANCER',
            'TNM STAGE',
            'PRESERVATION',
            'TEST SAMPLE ID',
            'EXTRACTION',
            'LIBRARY ID',
            'LIBRARY TYPE',
            'KIT TYPE',
            'KIT VERSION'
        ))

    def _setup_column_sizes(self, ws):
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max(
                        (dims.get(cell.column, 0), len(cell.value)))
        for col, value in dims.items():
            ws.column_dimensions[col].width = dims[col]

    def _setup_validation(self, ws):
        """Setup data validation, creates list cells"""
        # Column: B/sex
        dv_sex = DataValidation(
            type='list', formula1='"male,female,unknown"', allow_blank=True)
        dv_sex.ranges.append('B2:B1000')
        dv_sex.error = 'Sex must be one of male, female, unknown'
        dv_sex.errorTitle = 'Invalid sex'
        ws.add_data_validation(dv_sex)
        # Column: E/is cancer
        dv_cancer = DataValidation(
            type='list', formula1='"yes,no"', allow_blank=True)
        dv_cancer.ranges.append('E2:E1000')
        dv_cancer.error = 'Is Cancer? must be one of yes, no, unknown'
        dv_cancer.errorTitle = 'Invalid flag'
        # Column: G/preservation
        dv_preservation = DataValidation(
            type='list', formula1='"FFPE,fresh-frozen,other"',
            allow_blank=True)
        dv_preservation.ranges.append('G2:G1000')
        dv_preservation.error = (
            'Preservation must be one of FFPE, fresh-frozen, other')
        dv_preservation.errorTitle = 'Invalid preservation'
        ws.add_data_validation(dv_preservation)
        # Column: I/extraction
        dv_extraction = DataValidation(
            type='list', formula1='"RNA,DNA,other"', allow_blank=True)
        dv_extraction.ranges.append('I2:I1000')
        dv_extraction.error = 'Preservation must be one of RNA, DNA, other'
        dv_extraction.errorTitle = 'Invalid extraction'
        ws.add_data_validation(dv_extraction)
        # Column: K/library type
        dv_library = DataValidation(
            type='list',
            formula1='"WES,Panel-seq,WGS,mRNA-seq,tRNA-seq,other"',
            allow_blank=True)
        dv_library.ranges.append('K2:K1000')
        dv_library.error = 'Library type must be in the list'
        dv_library.errorTitle = 'Invalid library type'
        ws.add_data_validation(dv_library)
        # Column: L/kit type
        dv_library = DataValidation(
            type='list',
            formula1=('"Agilent_SureSelect_Human_All_Exon,'
                      'Illumina_TruSeq_DNA_PCR_Free_Library_Preparation_Kit,'
                      'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit,'
                      'Illumina_TruSeq_Exome"'),
            allow_blank=True)
        dv_library.ranges.append('L2:L1000')
        dv_library.error = 'Kit type must be in the list'
        dv_library.errorTitle = 'Kit type'
        ws.add_data_validation(dv_library)

    def _add_example_rows(self, ws):
        """Add example rows to sheet"""
        ws.append(('P001', 'male', 'P001-S1', '', 'no', '',
                   'other', 'P001-S1-DNA1', 'DNA',
                   'P001-S1-DNA1-WES1', 'WES',
                   'Agilent_SureSelect_Human_All_Exon', 'V6'))
        ws.append(('P001', 'male', 'P001-T1', 'C18.9', 'yes', 'T1 S1 M0',
                   'fresh-frozen', 'P001-T1-DNA1', 'DNA',
                   'P001-T1-DNA1-WES1', 'WES',
                   'Agilent_SureSelect_Human_All_Exon', 'V6'))
        ws.append(('P001', 'male', 'P001-T1', 'C18.9', 'yes', 'T1 S1 M0',
                   'fresh-frozen', 'P001-T1-RNA1', 'RNA',
                   'P001-T1-RNA1-RNAseq1', 'mRNA-seq',
                   'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit', '1'))


class GenericExperimentSheetCreator:

    def run(self, output_path):
        """Create empty sheet for generic experiments to ``path``"""
        wb = Workbook()
        ws = wb.active
        self._setup_sheet(ws)
        wb.save(output_path)

    def _setup_sheet(self, ws):
        ws.title = 'Generic Experiment Sample Sheet'
        self._setup_header(ws)
        self._setup_validation(ws)
        self._add_example_rows(ws)
        self._setup_column_sizes(ws)
        ws.freeze_panes = ws['A2']

    def _setup_header(self, ws):
        ws.append((
            'BIO ENTITY ID',
            'BIO SAMPLE ID',
            'TEST SAMPLE ID',
            'LIBRARY ID',
            'LIBRARY TYPE',
            'KIT TYPE',
            'KIT VERSION',
        ))

    def _setup_column_sizes(self, ws):
        dims = {}
        for row in ws.rows:
            for cell in row:
                if cell.value:
                    dims[cell.column] = max(
                        (dims.get(cell.column, 0), len(cell.value)))
        for col, value in dims.items():
            ws.column_dimensions[col].width = dims[col]

    def _setup_validation(self, ws):
        """Setup data validation, creates list cells"""
        # Column: E/library type
        dv_library = DataValidation(
            type='list',
            formula1='"WES,Panel-seq,WGS,mRNA-seq,tRNA-seq,other"',
            allow_blank=True)
        dv_library.ranges.append('E2:E1000')
        dv_library.error = 'Library type must be in the list'
        dv_library.errorTitle = 'Invalid library type'
        ws.add_data_validation(dv_library)
        # Column: F/kit type
        dv_kit = DataValidation(
            type='list',
            formula1=('"Agilent_SureSelect_Human_All_Exon,'
                      'Illumina_TruSeq_DNA_PCR_Free_Library_Preparation_Kit,'
                      'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit,'
                      'Illumina_TruSeq_Exome"'),
            allow_blank=True)
        dv_kit.ranges.append('F2:F1000')
        dv_kit.error = 'Kit type must be in the list'
        dv_kit.errorTitle = 'Kit type'
        ws.add_data_validation(dv_kit)

    def _add_example_rows(self, ws):
        """Add example rows to sheet"""
        ws.append(('X001', 'X001-S1', 'X001-S1-RNA1', 'X001-S1-RNA1-RNAseq1',
                   'mRNA-seq',
                   'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit', '1'))
        ws.append(('X002', 'X002-S1', 'X002-S1-RNA1', 'X001-S1-RNA1-RNAseq1',
                   'mRNA-seq',
                   'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit', '1'))
        ws.append(('X003', 'X003-S1', 'X003-S1-RNA1', 'X001-S1-RNA1-RNAseq1',
                   'mRNA-seq',
                   'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit', '1'))
        ws.append(('X004', 'X004-S1', 'X004-S1-RNA1', 'X001-S1-RNA1-RNAseq1',
                   'mRNA-seq',
                   'Illumina_TruSeq_Stranded_mRNA_Library_Prep_Kit', '1'))
