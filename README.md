pytest-cairo: pytest support for cairo-lang and starknet
---

## Usage
To install:
```bash
$ pip install pytest-cairo
```
The plugin will automatically run any function with a `test` prefix, from files with a `test_` prefix and a `.cairo` extension.

For examples see [test resources](/tests/resources).

## Development
To install development dependencies, run:
```bash
$ pip install -r requirements-dev.txt
```
Run tests with:
```bash
$ pytest
```
or:
```bash
$ docker-compose run test
```
To run tests against all supported interpreters (using `docker-compose`):
```bash
$ tox
```
This assumes `tox`, `docker` and `docker-compose` are installed.
