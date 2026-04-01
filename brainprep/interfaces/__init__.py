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
    cat12vbm_wf,
    write_catbatch,
)
from .fmriprep import (
    fmriprep_wf,
    func_vol_connectivity,
)
from .freesurfer import (
    brainmask,
    freesurfer_command_status,
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
from .morphologist import (
    morphologist_wf,
)
from .mriqc import (
    group_level_qa,
    subject_level_qa,
)
from .plotting import (
    plot_brainparc,
    plot_defacing_mosaic,
    plot_histogram,
    plot_network,
    plot_pca,
)
from .qualcheck import (
    euler_numbers,
    fmriprep_metrics,
    incremental_pca,
    mask_overlap,
    mean_correlation,
    mriqc_metrics,
    network_entropy,
    vbm_metrics,
)
from .utils import (
    anonfile,
    copyfiles,
    maskdiff,
    movedir,
    ungzfile,
    write_uuid_mapping,
)

__all__ = [
    "affine",
    "anonfile",
    "applyaffine",
    "applymask",
    "biasfield",
    "brainmask",
    "cat12vbm_morphometry",
    "cat12vbm_wf",
    "copyfiles",
    "deface",
    "euler_numbers",
    "fmriprep_metrics",
    "fmriprep_wf",
    "freesurfer_command_status",
    "freesurfer_features_summary",
    "freesurfer_tissues",
    "fsaveragesym_projection",
    "fsaveragesym_surfreg",
    "func_vol_connectivity",
    "group_level_qa",
    "incremental_pca",
    "localgi",
    "mask_overlap",
    "maskdiff",
    "mean_correlation",
    "mgz_to_nii",
    "morphologist_wf",
    "movedir",
    "mriqc_metrics",
    "network_entropy",
    "nextbrain",
    "plot_brainparc",
    "plot_defacing_mosaic",
    "plot_histogram",
    "plot_network",
    "plot_pca",
    "reconall",
    "reconall_longitudinal",
    "reorient",
    "scale",
    "subject_level_qa",
    "ungzfile",
    "vbm_metrics",
    "write_catbatch",
    "write_uuid_mapping",
]
