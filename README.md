# pySBOL2
[![Build Status](https://travis-ci.org/SynBioDex/pySBOL2.svg?branch=master)](https://travis-ci.org/SynBioDex/pySBOL2)

**pySBOL2** is a pure Python implementation of the SBOL 2.3.0 standard [Synthetic Biology Open Language (SBOL)](http://www.sbolstandard.org/) - 
an open standard for the representation of *in silico* biological designs. It draws from [libSBOL](https://github.com/SynBioDex/libSBOL)
and [pySBOL](https://github.com/SynBioDex/pySBOL).

This native Python library is intended to eventually supplant the original [pySBOL](https://github.com/SynBioDex/pySBOL) based on C++ wrappers.

For developers, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## INSTALLATION

This library is currently under development. Please consider using a
virtual environment for your installation.

```shell
# Name the virtual environment
DIR=myenv

# Create the virtual environment
python3 -m venv "${DIR}"

# Activate the virtual environment
source "${DIR}"/bin/activate

# Recommended: upgrade pip
pip install -U pip

# Install the sbol module
pip install sbol2
```

Alternatively if you want to be able to run unit tests (starting with 1.0b3)
please install the source distribution:

```shell
pip install --no-binary sbol2 sbol2
```

## CODE EXAMPLE

```
import sbol2

doc = sbol2.Document()
```

## DOCUMENTATION

This module should be largely compatible with
[pySBOL](https://github.com/SynBioDex/pySBOL).
The [pySBOL documentation](https://pysbol2.readthedocs.io/en/latest/index.html)
should be used until this module has its own documentation.

## ACKNOWLEDGEMENTS

Development of this library has been supported by the DARPA Synergistic Discovery & Design program and BBN Technologies.

<p align="center">
  <img src="./logo.jpg" height="100" />
</p>
