##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Types or Type aliases used by BrainPrep.
"""

from pathlib import Path
from typing import TypeAlias

Url: TypeAlias = str | None
File: TypeAlias = str | Path | None
Directory: TypeAlias = str | Path | None
