# pySBOL2
[![Build Status](https://travis-ci.org/SynBioDex/pySBOL2.svg?branch=master)](https://travis-ci.org/SynBioDex/pySBOL2)
[![Documentation Status](https://readthedocs.org/projects/pysbol/badge/?version=latest)](https://pysbol.readthedocs.io/en/latest/?badge=latest)

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

### Java dependency for offline validation/conversion

By default, pySBOL2 executes its validation and conversion with the online validator/converter. 
These can also be done offline using the Java JAR file packaged with the library.

Java requirements are: openjdk8 or later 

Java location defaults to `/usr/bin/java`, and can be adjusted by setting the `JAVA_LOCATION` config option:

```
Config.setOption(ConfigOptions.JAVA_LOCATION, '/my/java/path')
```

## CODE EXAMPLE

This short example creates a Document, adds a ComponentDefinition
to the Document, and then writes the resulting Document to an SBOL
file. Other examples are in the [examples](examples) directory.

```
import sbol2

doc = sbol2.Document()
cd = sbol2.ComponentDefinition('cd1')
doc.add(cd)
doc.write('my-sbol.xml')
```

## UNIT TESTS

The unit tests are not included when installing via pip. The unit
tests are included in the source distribution. To access and
run the unit tests without [checking out from git](CONTRIBUTING.md),
download the source distribution, unpack it, and run the unit tests.

```shell script
pip download --no-binary sbol2 sbol2
tar zxf sbol2-VERSION.tar.gz
cd sbol2-VERSION
python3 -m unittest discover test
```

## DOCUMENTATION

[Full documentation for pySBOL2 is available here](https://pysbol.readthedocs.io).

## ACKNOWLEDGEMENTS

Development of this library has been supported by the 
[DARPA Synergistic Discovery and Design (SD2)](https://www.darpa.mil/program/synergistic-discovery-and-design)
program and [Raytheon BBN Technologies](http://bbn.com/).


<p align="center">
  <img src="./logo.jpg" height="100" />
</p>
