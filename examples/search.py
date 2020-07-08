import time
import sbol2

# This example is from the documentation at
# https://pysbol.readthedocs.io/en/latest/repositories.html

igem = sbol2.PartShop('https://synbiohub.org/public/igem')
records = []
search_term = 'plasmid'
limit = 25
total_hits = igem.searchCount(search_term)
print(f'Expecting {total_hits} records')
for offset in range(0, total_hits, limit):
    records.extend(igem.search(search_term, sbol2.SBOL_COMPONENT_DEFINITION,
                               offset, limit))
    time.sleep(0.1)
print(f'Received {len(records)} records')
