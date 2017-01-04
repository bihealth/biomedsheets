# -*- coding: utf-8 -*-
"""Demonstrate shortcuts for cancer sample sheet
"""

import collections
import os

from biomedsheets import io, ref_resolver, shortcuts


def load_sheet():
    """Return ``Sheet`` instance for the cancer example"""
    path = os.path.join(os.path.abspath(
        os.path.dirname(__file__)), 'example_cancer.json')
    sheet_json = io.json_loads_ordered(open(path, 'rt').read())
    resolver = ref_resolver.RefResolver(dict_class=collections.OrderedDict)
    return io.SheetBuilder(
        resolver.resolve('file://' + path, sheet_json)).run()


def main():
    """Main program entry point"""
    cancer_cases = shortcuts.CancerCaseSheet(load_sheet())
    print('Donors\n')
    for donor in cancer_cases.donors:
        print('  {}'.format(donor.name))
    print('\nLibraries of all tumor/normal pairs\n')
    for pair in cancer_cases.all_sample_pairs:
        print('  {}'.format(pair.donor.name))
        print('    normal DNA: {}'.format(pair.normal_sample.dna_ngs_library.name))
        if pair.normal_sample.rna_ngs_library:
            print('    normal RNA: {}'.format(pair.normal_sample.rna_ngs_library.name))
        print('    tumor DNA:  {}'.format(pair.tumor_sample.dna_ngs_library.name))
        if pair.tumor_sample.rna_ngs_library:
            print('    tumor RNA:  {}'.format(pair.tumor_sample.rna_ngs_library.name))


if __name__ == '__main__':
    main()
