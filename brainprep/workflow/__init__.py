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
)
from .brain_parcellation import (
    brainprep_brainparc,
    brainprep_group_brainparc,
)
from .vbm import (
    brainprep_group_vbm,
    brainprep_longitudinal_vbm,
    brainprep_vbm,
)
from .fmriprep import (
    brainprep_fmriprep,
)
from .quasiraw import (
    brainprep_quasiraw,
    # brainprep_group_quasiraw,
)
from .quality_assurance import (
    brainprep_group_quality_assurance,
    brainprep_quality_assurance,
)
# from .tbss import brainprep_tbss_preproc, brainprep_tbss
from .dmriprep import (
    brainprep_dmriprep,
    brainprep_group_dmriprep,
)

__all__ = []
