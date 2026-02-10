##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements interfaces.
"""

from .ants import (
    biasfield,
)
from .cat12 import (
    cat12vbm_morphometry,
    cat12vbm_stats,
    cat12vbm_wf,
    write_catbatch,
)
from .fmriprep import (
    fmriprep_stats,
    fmriprep_wf,
    func_vol_connectivity,
)
from .freesurfer import (
    brainmask,
    freesurfer_command_status,
    freesurfer_euler_numbers,
    freesurfer_features_summary,
    freesurfer_tissues,
    fsaveragesym_projection,
    fsaveragesym_surfreg,
    localgi,
    mgz_to_nii,
    nextbrain,
    reconall,
    reconall_longitudinal,
)
from .fsl import (
    affine,
    applyaffine,
    applymask,
    deface,
    reorient,
    scale,
)
from .mriqc import (
    group_level_qa,
    subject_level_qa,
)
from .plotting import (
    plot_brainparc,
    plot_defacing_mosaic,
    plot_histogram,
    plot_pca,
)
from .utils import (
    copyfiles,
    incremental_pca,
    mask_diff,
    mean_correlation,
    movedir,
    ungzfile,
)

__all__ = [
    "deface",
    "reorient",
]
