##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements all user workflows.
"""

from .defacing import brainprep_defacing
from .brain_parcellation import (
    brainprep_brainparc,
    brainprep_group_brainparc,
)
# from .cat12vbm import (brainprep_cat12vbm, brainprep_cat12vbm_qc,
#                        brainprep_cat12vbm_roi)
from .quasiraw import (
    brainprep_quasiraw,
    # brainprep_group_quasiraw,
)
# from .fmriprep import brainprep_fmriprep, brainprep_fmriprep_conn
from .quality_assurance import (
    brainprep_group_quality_assurance,
    brainprep_quality_assurance,
)
# from .tbss import brainprep_tbss_preproc, brainprep_tbss
# from .prequal import brainprep_prequal, brainprep_prequal_qc

__all__ = []
