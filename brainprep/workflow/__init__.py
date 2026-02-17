# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2022
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements all user workflows.
"""

# Imports
from .cat12vbm import brainprep_cat12vbm, brainprep_cat12vbm_qc, brainprep_cat12vbm_roi
from .deface import brainprep_deface, brainprep_deface_qc
from .fmriprep import brainprep_fmriprep, brainprep_fmriprep_conn
from .fsreconall import (
    brainprep_fsreconall,
    brainprep_fsreconall_longitudinal,
    brainprep_fsreconall_qc,
    brainprep_fsreconall_summary,
)
from .mriqc import brainprep_mriqc, brainprep_mriqc_summary
from .prequal import brainprep_prequal, brainprep_prequal_qc
from .quasiraw import brainprep_quasiraw, brainprep_quasiraw_qc
from .tbss import brainprep_tbss, brainprep_tbss_preproc
