# foobar-api

[![Travis CI](https://travis-ci.org/uppsaladatavetare/foobar-api.svg)](https://travis-ci.org/uppsaladatavetare/foobar-api)
[![Codecov](https://codecov.io/gh/uppsaladatavetare/foobar-api/coverage.svg?branch=master)](https://codecov.io/gh/uppsaladatavetare/foobar-api/)

This repository contains the backend for the FooBar kiosk and inventory system.

## Requirements

- Python 3.4+
- Django 1.10+
- [pdftotext](https://linux.die.net/man/1/pdftotext) for delivery report parsing

## Setup

    $ git clone git@github.com:uppsaladatavetare/foobar-api.git
    $ cd foobar-api
    $ virtualenv -p /usr/local/bin/python3.4 venv
    $ venv/bin/pip install -r requirements.txt

## How do I run tests?

We use [tox](https://tox.readthedocs.org/en/latest/) to automate testing against all supported Python and Django versions. To run test, simply execute following command in the root directory:

    $ tox

## Can I contribute?

Sure thing! Any contributions are welcome.

## License

MIT License. Please see the LICENSE file.
