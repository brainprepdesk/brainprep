##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Available workflows.
"""

from .defacing import (
    brainprep_defacing,
    brainprep_group_defacing,
)
from .fmriprep import (
    brainprep_fmriprep,
    brainprep_group_fmriprep,
)
from .quality_assurance import (
    brainprep_group_quality_assurance,
    brainprep_quality_assurance,
)
from .quasiraw import (
    brainprep_group_quasiraw,
    brainprep_quasiraw,
)
from .sbm import (
    brainprep_group_sbm,
    brainprep_longitudinal_sbm,
    brainprep_sbm,
)
from .vbm import (
    brainprep_group_vbm,
    brainprep_longitudinal_vbm,
    brainprep_vbm,
)

__all__ = []
