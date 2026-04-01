##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements dataset fetchers.
"""

from .ibc import (
    IBCDataset,
)
from .openms import (
    OpenMSDataset,
)
from .utils import (
    git_download,
    openneuro_download,
)

__all__ = [
    "IBCDataset",
    "OpenMSDataset",
    "git_download",
    "openneuro_download",
]
