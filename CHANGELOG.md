# BioMed Sheets Changelog

### [0.11.7](https://www.github.com/bihealth/biomedsheets/compare/v0.11.6...v0.11.7) (2023-02-22)


### Bug Fixes

* MANIFEST.in file for CHANGELOG.md ([#32](https://www.github.com/bihealth/biomedsheets/issues/32)) ([c093555](https://www.github.com/bihealth/biomedsheets/commit/c093555c937bd65d2c0cd3f06f62fd404e5364fd))

### [0.11.6](https://www.github.com/bihealth/biomedsheets/compare/v0.11.5...v0.11.6) (2023-02-22)


### Bug Fixes

* implementing release-please ([#30](https://www.github.com/bihealth/biomedsheets/issues/30)) ([2076440](https://www.github.com/bihealth/biomedsheets/commit/20764408458898b1f65cc550f5c1ae0514657b12))

### v0.11.5

-   Fixing consistency check for Duo Cases (#26).

### v0.11.4

-   Fixing issues with ResourceAdapter (#21).

### v0.11.3

-   Fixing warnings in the tests (#19).

### v0.11.2

-   Updating/modernizing dependencies.

### v0.11.1

-   Adding property to shortcut sheets that indicates available kwargs.

### v0.11.0

-   Adding custom option to join pedigrees by fields such as `familyId`.

### v0.10.0

-   Adding functionality for filtering pedigrees.

### v0.9.1

-   Fixing sorting bug.

### v0.9.0

-   Sorting donors for picking the index in germline sample sheets.

### v0.8.1

-   Fixing mapping of `Unknown` values.

### v0.8.0

-   Changed behaviour in case of no affected donor has library. In this
    case, the first donor becomes the index. Consequently, the index
    must have an NGS library.

### v0.7.1

-   Removing superflous print.

### v0.7.0

-   Allowing to specify `bioSample` and `testSample` in germline TSV
    files.
-   Fixing some tests.

### v0.6.2

-   Proper merging with recent `ruamel.yaml` updates.

### v0.6.1

-   Interpreting `#` in TSV files in more locations.

### v0.6.0

-   Allowing to comment out lines in TSV files by prefixing them with
    `#`.

### v0.5.6

-   Fixing bug in computing index (for real).

### v0.5.5

-   Fixing bug in computing index.

### v0.5.4

-   Fixing `setup.py` to work with pip v10.t

### v0.5.3

-   Fixing packaging to use base and not test dependencies.

### v0.5.2

-   Removing some hard (transitive) dependencies.

### v0.5.1

-   Fixing manifest so the package contains the JSON file.

### v0.5

-   Allow cancer sheets for use in germline calling.
-   Only warn if index has no NGS library, no error.

### v0.4

-   Fixin TSV I/O.
-   Bumping ruamel.yaml version.
-   Fixing cancer sheet iteration.
-   Allowing cancer-only samples in cance case sheets.
-   Fixing `float`-related bug.
-   Fixing bug in reference resolving (+tests)

### v0.3.1

-   Fixing `setup.py` to work with pip v10.

### v0.3

-   Adding possibility for generic TSV sample sheets.
-   Many updates to make documentation more clear.
-   Various updates, fixing Codacy issues.
-   Adding routines for writing out PED file from germline sample
    sheets.

### v0.2

-   Auto-deployment to pypi
-   Fixing shortcuts to father/mother during cohort loading
-   Cleanup code (according to Flake 8)
-   Adding more tests, replacing examples by TSV files
-   Removing protein pools
-   Adding Sphinx-based ocumentation
-   Restructuring requirements txt files
-   Configurable entity name generation. This allows to use secondary id
    only for naming, e.g.
-   Fixing `requirements*.txt` files for always using SSH
-   Fixing sample naming for germline sample sheets
-   Adding versioneer integration

### v0.1.1

-   First actual release, versioning done using versioneer
-   Everything is new!
