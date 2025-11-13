##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

import brainprep
import doctest
import importlib
import pkgutil
import unittest


def load_tests(loader, tests, ignore):
    for _, module_name, ispkg in pkgutil.walk_packages(
            brainprep.__path__,
            brainprep.__name__ + "."):
        module = importlib.import_module(module_name)
        tests.addTests(
            doctest.DocTestSuite(
                module,
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
            )
        )
    return tests


if __name__ == "__main__":
    unittest.main()
