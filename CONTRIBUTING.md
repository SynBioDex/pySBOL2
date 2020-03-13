# SBOL For Developers

[![Build Status](https://travis-ci.com/llotneb/SBOL.svg?branch=master)](https://travis-ci.com/llotneb/SBOL)

**SBOL** is a pure Python implementation of the SBOL standard
 [Synthetic Biology Open Language (SBOL)](http://www.sbolstandard.org/) - 
an open standard for the representation of *in silico* biological designs.
It draws from [libSBOL](https://github.com/SynBioDex/libSBOL)
and [pySBOL](https://github.com/SynBioDex/pySBOL).

## INSTALLATION

We recommend installing with a virtual environment.

Please note that this project uses
[git submodules](https://git-scm.com/book/en/v2/Git-Tools-Submodules),
so please use the `--recurse-submodules` option when cloning.

```shell
git clone --recurse-submodules https://github.com/llotneb/SBOL.git 
python3 -m venv myenv
source myenv/bin/activate
pip install -U pip
cd SBOL
pip install -e .
```

You should now be able to run the unit tests

```shell
python3 -c "import sbol; sbol.testSBOL()"
```

## TESTING

SBOL comes with a testing function to check the integrity of the library. To run the unit tests, simply execute the following command.
```python
import sbol
sbol.testSBOL()
```
SBOL also comes with a suite of 'round-trip' tests to verify that serialization and deserialization of SBOL files works correctly.
To run the round-trip tests, execute the following command.
```python
import sbol
sbol.testRoundTrip()
```

## CODE STYLE

We use [pycodestyle]() for our coding guidelines. `pycodestyle`
follows PEP8.  Please ensure that any contributions pass pycodetyle
with a max line width of 90 characters.

## GIT PRE-COMMIT HOOK

If you are a developer, please run `./dev/bootstrap.sh` to set up the pre-commit hooks.
This will ensure that unit tests and style checking is performed before each commit.

<p align="center">
  <img src="./logo.jpg" height="100" />
</p>
