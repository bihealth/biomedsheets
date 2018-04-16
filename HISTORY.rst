=======================
BioMed Sheets Changelog
=======================

-----------------------
HEAD (work in progress)
-----------------------

------
v0.5.4
------

- Fixing ``setup.py`` to work with pip v10.t

------
v0.5.3
------

- Fixing packaging to use base and not test dependencies.

------
v0.5.2
------

- Removing some hard (transitive) dependencies.

------
v0.5.1
------

- Fixing manifest so the package contains the JSON file.

----
v0.5
----

- Allow cancer sheets for use in germline calling.
- Only warn if index has no NGS library, no error.

----
v0.4
----

- Fixin TSV I/O.
- Bumping ruamel.yaml version.
- Fixing cancer sheet iteration.
- Allowing cancer-only samples in cance case sheets.
- Fixing ``float``-related bug.
- Fixing bug in reference resolving (+tests)

------
v0.3.1
------

- Fixing ``setup.py`` to work with pip v10.

----
v0.3
----

- Adding possibility for generic TSV sample sheets.
- Many updates to make documentation more clear.
- Various updates, fixing Codacy issues.
- Adding routines for writing out PED file from germline sample sheets.

----
v0.2
----

- Auto-deployment to pypi
- Fixing shortcuts to father/mother during cohort loading
- Cleanup code (according to Flake 8)
- Adding more tests, replacing examples by TSV files
- Removing protein pools
- Adding Sphinx-based ocumentation
- Restructuring requirements txt files
- Configurable entity name generation.
  This allows to use secondary id only for naming, e.g.
- Fixing ``requirements*.txt`` files for always using SSH
- Fixing sample naming for germline sample sheets
- Adding versioneer integration

------
v0.1.1
------

- First actual release, versioning done using versioneer
- Everything is new!
