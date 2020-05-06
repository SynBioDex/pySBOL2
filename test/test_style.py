import os
import pathlib
import unittest

MODULE_LOCATION = os.path.dirname(os.path.abspath(__file__))
# The sbol2 directory is a sibling to the test directory where this file
# lives.
SBOL_PATH = os.path.join(os.path.dirname(MODULE_LOCATION), 'sbol2')

# Please don't increase this number!
MAX_WILDCARD_IMPORTS = 1

# -----------------------------------------------------------------
# Locale Fix
#
# If you get an ascii conversion error, you probably do not have a
# local set.
#
# Follow these steps, substituting for "en_US.utf8" as appropriate:
#
#     apt update
#     apt install locales
#     locale-gen en_US.utf8
#     export LANG=en_US.utf8
#
# -----------------------------------------------------------------


class TestStyle(unittest.TestCase):

    def test_wildcard_imports(self):
        wildcard_count = 0
        sbol_path = pathlib.Path(SBOL_PATH)
        for f in sbol_path.glob('**/*.py'):
            with open(f) as fp:
                for line in fp:
                    if 'import' in line:
                        if '*' in line and 'constants' not in line:
                            msg = 'Wildcard import in {}: {}'
                            msg = msg.format(f, line)
                            # self.fail(msg)
                            # print(msg)
                            wildcard_count += 1
        # Limit the number of wildcard imports that do not involve
        # constants.py to 8. Let's try to reduce this number.
        if wildcard_count < MAX_WILDCARD_IMPORTS:
            msg = 'Reduce MAX_WILDCARD_IMPORTS to {} in test_style.py'
            msg = msg.format(wildcard_count)
            print(msg)
        self.assertLessEqual(wildcard_count, MAX_WILDCARD_IMPORTS)
