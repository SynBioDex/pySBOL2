Installation
======================

Currently, we support Python 3.6 or higher.
Python by default comes with package manager. Follow the steps below to install pySBOL2.

*Note: Python 2 is not supported.*

----------------------
Using Pip
----------------------

pySBOL2 is available for Python 3 on any platform. 
To install pySBOL using pip, run following line in a console or terminal:

``pip install sbol2``

If you encounter permission errors, you may install pySBOL2 to your user site-packages directory as follows:

``pip install sbol2 --user``

Or alternatively, you may install as a super-user:

``sudo -H pip install sbol2``

To update pySBOL using pip, run:

``pip install -U sbol2``

----------------------
Using Python
----------------------

1 - `Download the source code of latest release here <https://github.com/SynBioDex/pysbol2/releases/latest>`_ and extract it.
If you would like to try out our latest snapshot, use `git <https://git-scm.com/>`_ and type following command in the console or terminal which will clone the source under pysbol folder.

``git clone https://github.com/SynBioDex/sbol2.git``

2 - Open your console or terminal. Go to package's root directory and Run the installer script by using the following command line. This will install pySBOL2 to the Python release associated with the console or terminal you are using.

``python setup.py install``

**If you are having problems, make sure your console/terminal is associated with the right Python environment you wish to use.**

3 - Test the installation by importing it in Python.

``import sbol2``

**If you have trouble importing the module with the setup script, check to see if there are multiple Python installations on your machine and also check the output of the setup script to see which version of Python is the install target.**

----------------------
Installing on macOS
----------------------

.. See Issue #258

Macs do not ship with Python 3 so it is necessary to download and
install Python 3 before installing pySBOL2. You can download the
latest Python 3 release from `python.org
<https://www.python.org>`_. After Python 3 is installed please follow
the instructions above to install pySBOL2.
