import sbol2

# This example uses the SBOL Validator (http://synbiodex.github.io/SBOL-Validator/)
# to convert an SBOL document to a GenBank file.

# Create a new Document and read the SBOL file
doc = sbol2.Document('data/BBa_I0462.xml')

# Export the document in 'GenBank' format.
# Write the output to the destination file.
doc.exportToFormat('GenBank', 'BBa_I0462.gb')
