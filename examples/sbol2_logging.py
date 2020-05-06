import logging

import sbol2

# This example shows how to configure logging for sbol2


# Configure the Python logging system
logging.basicConfig()

# Set the 'sbol2' logger to debug level
logging.getLogger('sbol2').setLevel(logging.DEBUG)

# This will generate lots of debug logging
doc = sbol2.Document('data/BBa_I0462.xml')
