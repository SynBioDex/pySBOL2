from sbol2 import *

setHomespace('http://sys-bio.org')
doc = Document()

gene = ComponentDefinition('gene_example')
r0010 = ComponentDefinition('R0010')
b0032 = ComponentDefinition('B0032')
e0040 = ComponentDefinition('E0040')
b0012 = ComponentDefinition('B0012')

r0010.roles = SO_PROMOTER
b0032.roles = SO_CDS
e0040.roles = SO_RBS
b0012.roles = SO_TERMINATOR

doc.addComponentDefinition(gene)
doc.addComponentDefinition([r0010, b0032, e0040, b0012])

gene.assemblePrimaryStructure([r0010, b0032, e0040, b0012])

first = gene.getFirstComponent()
print(first.identity)
last = gene.getLastComponent()
print(last.identity)

r0010.sequence = Sequence('R0010', 'ggctgca')
b0032.sequence = Sequence('B0032', 'aattatataaa')
e0040.sequence = Sequence('E0040', "atgtaa")
b0012.sequence = Sequence('B0012', 'attcga')

target_sequence = gene.compile()
print(gene.sequence.elements)

result = doc.write('gene_cassette.xml')
print(result)
