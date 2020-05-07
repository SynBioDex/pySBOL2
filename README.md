# pySBOL2
[![Build Status](https://travis-ci.org/SynBioDex/pySBOL2.svg?branch=master)](https://travis-ci.org/SynBioDex/pySBOL2)

**pySBOL2** is a pure Python implementation of the
SBOL 2.3.0 standard [Synthetic Biology Open Language (SBOL)](https://sbolstandard.org/) - 
an open standard for the representation of *in silico* biological designs. It draws from [libSBOL](https://github.com/SynBioDex/libSBOL)
and [pySBOL](https://github.com/SynBioDex/pySBOL).

This native Python library is intended to eventually supplant the original [pySBOL](https://github.com/SynBioDex/pySBOL) based on C++ wrappers.

For developers, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## INSTALLATION

Use [pip](https://pip.pypa.io/) to install pySBOL2:

```shell
pip install sbol2
```

If you get a permission error, try using the `--user` flag:

```shell
pip install --user sbol2
```

Alternatively if you want to be able to run unit tests (starting with 1.0b3)
please install the source distribution using the `--no-binary sbol2` flag.
The location of the unit tests will vary based on platform and other
pip command line options you may have used.

```shell
pip install --no-binary sbol2 sbol2
```

## CODE EXAMPLE

This short example creates a Document, adds a ComponentDefinition
to the Document, and then writes the resulting Document to an SBOL
file.

```
import sbol2

doc = sbol2.Document()
cd = sbol2.ComponentDefinition('cd1')
doc.add(cd)
doc.write('my-sbol.xml')
```

## DOCUMENTATION

This module should be largely compatible with
[pySBOL](https://github.com/SynBioDex/pySBOL).
The [pySBOL documentation](https://pysbol2.readthedocs.io/en/latest/index.html)
should be used until this module has its own documentation.

## ACKNOWLEDGEMENTS

Development of this library has been supported by the 
[DARPA Synergistic Discovery and Design (SD2)](https://www.darpa.mil/program/synergistic-discovery-and-design)
program and [Raytheon BBN Technologies](http://bbn.com/).


<p align="center">
  <img src="./logo.jpg" height="100" />
</p>
