# pySBOL2 For Developers

[![Build Status](https://travis-ci.org/SynBioDex/pySBOL2.svg?branch=master)](https://travis-ci.org/SynBioDex/pySBOL2)

**pySBOL2** is a pure Python implementation of the SBOL standard
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
# Create and activate the virtual environment
python3 -m venv sbol2env
source sbol2env/bin/activate
pip install -U pip

# Clone and install pySBOL2
git clone --recurse-submodules https://github.com/SynBioDex/pySBOL2.git 
cd pySBOL2
pip install -e .
```

You should now be able to run the unit tests in the `test` directory:

```shell
python3 -m unittest
```

## CODE STYLE

We use [pycodestyle](https://pypi.org/project/pycodestyle/) for our coding guidelines. `pycodestyle`
follows PEP8.  Please ensure that any contributions pass pycodestyle
with a max line width of 90 characters.

## GIT PRE-COMMIT HOOK

If you are a developer, please run `./dev/bootstrap.sh` to set up the pre-commit hooks.
This will ensure that unit tests and style checking is performed before each commit.

<p align="center">
  <img src="./logo.jpg" height="100" />
</p>
