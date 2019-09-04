import unittest
from sbol.partshop import PartShop
from sbol.document import Document


class TestPartShop(unittest.TestCase):
    def test_pull(self):
        doc = Document()
        igem = PartShop('https://synbiohub.org')
        igem.pull('https://synbiohub.org/public/igem/BBa_R0010/1', doc)
        igem.pull('https://synbiohub.org/public/igem/BBa_B0032/1', doc)
        # igem.pull('https://synbiohub.org/public/igem/BBa_E0040/1', doc)
        # igem.pull('https://synbiohub.org/public/igem/BBa_B0012/1', doc)
        print(doc)
        print(len(doc))
        for obj in doc:
            print(obj)

    def test_login(self):
        # NOTE: Add /login because login pages may be different depending on what site you're accessing
        igem = PartShop('https://synbiohub.org/login')
        igem.login('johndoe@example.org', 'test')

