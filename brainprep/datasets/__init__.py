##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements datasets.
"""


from .anatomical import (
    AnatomicalDataset,
)
from .multi_modal import (
    MultiModalDataset,
)
from .utils import (
    git_download,
)

__all__ = [
    "AnatomicalDataset",
    "git_download"
]
