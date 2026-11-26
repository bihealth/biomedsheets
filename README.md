[![readthedocs](https://readthedocs.org/projects/biomedsheets/badge/?version=master)](https://biomedsheets.readthedocs.io/en/master)


# BioMed Sheets

This project contains the documentation for the BioMedical sample sheets project.
Further, it contains the implementation of a Python API for I/O and comfortable access to the sample sheets and some CLI tools.

## Installation

```
$ pip install biomedsheets
```

## Development

The project uses [uv](https://docs.astral.sh/uv/) for environment management.
`uv sync` creates `.venv` with the package installed in editable mode plus all
development dependencies.

```
$ uv sync
$ make lint      # ruff lint and format check
$ make test      # pytest
$ make docs      # Sphinx HTML, see docs/build/html/index.html
```

Versioning and the changelog are handled by release-please from conventional
commit messages, so do not edit `CHANGELOG.md` or the version by hand.
