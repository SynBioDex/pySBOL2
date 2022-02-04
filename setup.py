from setuptools import setup

setup(name='sbol2',
      version='1.4',
      description='Pure Python implementation of SBOL 2 standard',
      python_requires='>=3.7',
      url='https://github.com/SynBioDex/pySBOL2',
      author='Bryan Bartley',
      author_email='editors@sbolstandard.org',
      license='Apache-2',
      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: Apache Software License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3'
      ],
      # What does your project relate to?
      keywords='synthetic biology',
      packages=['sbol2'],
      install_requires=[
            'rdflib>=5.0',
            'python-dateutil',
            'deprecated',
            'lxml',
            'requests',
            'urllib3',
            'packaging>=20.0'
      ],
      package_data={'sbol2': ['libSBOLj.jar']},
      tests_require=[
            'pycodestyle>=2.6.0'
      ])
