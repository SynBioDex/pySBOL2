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

    def gsoc_search_title(self, part_shop, collection, title):
        query = sbol2.SearchQuery()
        query[sbol2.SBOL_COLLECTION] = collection
        query[sbol2.SBOL_NAME] = title
        # GSOC is always looking for DNA Region
        query[sbol2.SBOL_TYPES] = sbol2.BIOPAX_DNA
        return part_shop.search(query)

    def gsoc_search_display_id(self, part_shop, collection, display_id):
        query = sbol2.SearchQuery()
        query[sbol2.SBOL_COLLECTION] = collection
        query[sbol2.SBOL_DISPLAY_ID] = display_id
        # GSOC is always looking for DNA Region
        query[sbol2.SBOL_TYPES] = sbol2.BIOPAX_DNA
        return part_shop.search(query)

    def do_gsoc_search(self, collection, term):
        part_shop = sbol2.PartShop(GSOC_SBH_URL)
        results = self.gsoc_search_title(part_shop, collection, term)
        results.extend(self.gsoc_search_display_id(part_shop, collection, term))
        return results

    def test_gsoc_example_2(self):
        # Looking for: https://synbiohub.org/public/igem/BBa_R0010/1
        #              and/or https://synbiohub.org/public/igem/BBa_C0012/1
        # Collection: https://synbiohub.org/public/igem/igem_collection/1
        # Search term: "LacI"
        # Don't want: https://synbiohub.org/public/igem/BBa_S03334/1
        #             or https://synbiohub.org/public/igem/BBa_K1444015/1
        collection = 'https://synbiohub.org/public/igem/igem_collection/1'
        results = self.do_gsoc_search(collection,
                                      'LacI')
        identities = [r.identity for r in results]
        self.assertIn('https://synbiohub.org/public/igem/BBa_R0010/1', identities)
        # This item requires case-insensitive search. I don't see a way to do that.
        # self.assertIn('https://synbiohub.org/public/igem/BBa_C0012/1', identities)
        self.assertNotIn('https://synbiohub.org/public/igem/BBa_S03334/1', identities)
        self.assertNotIn('https://synbiohub.org/public/igem/BBa_K1444015/1', identities)

    def test_gsoc_example_3(self):
        # Looking for: https://synbiohub.org/public/igem/BBa_R0010/1
        # Collection: https://synbiohub.org/public/igem/igem_collection/1
        # Search term: "BBa_R0010"
        # Don't want: https://synbiohub.org/public/igem/BBa_S03334/1
        #             or https://synbiohub.org/public/igem/BBa_K1444015/1
        collection = 'https://synbiohub.org/public/igem/igem_collection/1'
        results = self.do_gsoc_search(collection,
                                      'BBa_R0010')
        identities = [r.identity for r in results]
        self.assertIn('https://synbiohub.org/public/igem/BBa_R0010/1', identities)
        self.assertNotIn('https://synbiohub.org/public/igem/BBa_S03334/1', identities)
        self.assertNotIn('https://synbiohub.org/public/igem/BBa_K1444015/1', identities)

    def test_gsoc_example_4(self):
        # Looking for: https://synbiohub.org/public/igem/BBa_B0034/1
        # Collection: https://synbiohub.org/public/igem/igem_collection/1
        # Search term: "BBa_B0034"
        # Don't want: https://synbiohub.org/public/igem/BBa_I13617/1
        collection = 'https://synbiohub.org/public/igem/igem_collection/1'
        results = self.do_gsoc_search(collection,
                                      'BBa_B0034')
        identities = [r.identity for r in results]
        self.assertIn('https://synbiohub.org/public/igem/BBa_B0034/1', identities)
        self.assertNotIn('https://synbiohub.org/public/igem/BBa_I13617/1', identities)

    def test_gsoc_example_5(self):
        # Looking for: https://synbiohub.org/public/bsu/BO_28874/1
        # Collection: https://synbiohub.org/public/bsu/bsu_collection/1
        # Search term: "acca"
        # Don't want: https://synbiohub.org/public/bsu/BO_26604/1
        collection = 'https://synbiohub.org/public/bsu/bsu_collection/1'
        results = self.do_gsoc_search(collection,
                                      # If we can do case-insensitive, use 'acca'
                                      'accA')
        identities = [r.identity for r in results]
        self.assertIn('https://synbiohub.org/public/bsu/BO_28874/1', identities)
        self.assertNotIn('https://synbiohub.org/public/bsu/BO_26604/1', identities)

    def test_gsoc_count_5(self):
        part_shop = sbol2.PartShop(GSOC_SBH_URL)
        query = sbol2.SearchQuery()
        collection = 'https://synbiohub.org/public/bsu/bsu_collection/1'
        query[sbol2.SBOL_COLLECTION] = collection
        query[sbol2.SBOL_NAME] = 'accA'
        # GSOC is always looking for DNA Region
        query[sbol2.SBOL_TYPES] = sbol2.BIOPAX_DNA
        count = part_shop.searchCount(query)
        self.assertEqual(1, count)


if __name__ == '__main__':
    unittest.main()
