import unittest

import sbol2


GSOC_SBH_URL = 'https://synbiohub.org'


class TestSearchQuery(unittest.TestCase):

    def test_search_query1(self):
        query = sbol2.SearchQuery()
        query[sbol2.SBOL_TYPES] = sbol2.BIOPAX_DNA
        self.assertIn(sbol2.SBOL_TYPES, query.properties)
        self.assertEqual(sbol2.BIOPAX_DNA, query[sbol2.SBOL_TYPES])

    def test_gsoc_example_1_title(self):
        # See issue #240
        collection = 'https://synbiohub.org/public/igem/igem_collection/1'
        title = 'GFP'
        query = sbol2.SearchQuery()
        query[sbol2.SBOL_COLLECTION] = collection
        query[sbol2.SBOL_NAME] = title
        # GSOC is always looking for DNA Region
        query[sbol2.SBOL_TYPES] = sbol2.BIOPAX_DNA
        part_shop = sbol2.PartShop(GSOC_SBH_URL)
        response = part_shop.search(query)
        # At least one item in return should be the
        # expected return: https://synbiohub.org/public/igem/BBa_E0040/1
        identities = [r.identity for r in response]
        self.assertIn('https://synbiohub.org/public/igem/BBa_E0040/1', identities)
        #
        # All items in response should have name == GFP exactly.
        names = [r.name == title for r in response]
        self.assertTrue(all(names))

    def test_gsoc_example_1_display_id(self):
        # See issue #240
        collection = 'https://synbiohub.org/public/igem/igem_collection/1'
        display_id = 'BBa_E0040'
        query = sbol2.SearchQuery()
        query[sbol2.SBOL_COLLECTION] = collection
        query[sbol2.SBOL_DISPLAY_ID] = display_id
        # GSOC is always looking for DNA Region
        query[sbol2.SBOL_TYPES] = sbol2.BIOPAX_DNA
        part_shop = sbol2.PartShop(GSOC_SBH_URL)
        response = part_shop.search(query)
        # At least one item in return should be the
        # expected return: https://synbiohub.org/public/igem/BBa_E0040/1
        identities = [r.identity for r in response]
        self.assertIn('https://synbiohub.org/public/igem/BBa_E0040/1', identities)
        #
        # All items in response should have name == GFP exactly.
        display_ids = [r.displayId == display_id for r in response]
        self.assertTrue(all(display_ids))


if __name__ == '__main__':
    unittest.main()
