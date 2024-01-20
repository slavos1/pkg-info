# pkg info readme

TBD

## Prerequisites

* [`hatch`](https://hatch.pypa.io/) -- install via `pipx hatch` or `pip install --user hatch`

## Project organization

```
├── LICENSE
├── Makefile
├── coverage.cfg        <- setup for test coverage ('tox -e cov')
├── pyproject.toml      <- instead of setup.py, recognized by tox too
├── README.md           <- this file
├── tests
│   └── test_foo.py     <- write your own tests here
└── pkg_info   <- your package files
    ├── __init__.py
    ├── ...
```

## How to use

```console
# run the CLI
hatch run cli
make cli

# run the CLI help
hatch run help
make help

# or append any CLI-defined args, like --help
hatch run cli --help
make cli EXTRA='...'

# run mypy
hatch run types:check
make mypy

# run tests
hatch run test

# go to the venv shell
hatch shell
```
