##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Plotting functions.
"""

import os
from pathlib import Path
from typing import Union

from nilearn import plotting
import numpy as np
import matplotlib.pyplot as plt

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    outputdir,
)
from ..wrappers import pywrapper


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
@coerceparams
def defacing_mosaic(
        im_file: File,
        mask_file: File,
        output_dir: Directory,
        entities: dict,
        dryrun: bool = False) -> tuple[File]:
    """
    Generates a defacing mosaic image by overlaying a mask on an anatomical
    image.

    Parameters
    ----------
    im_file : File
        Path to the anatomical image.
    mask_file : File
        Path to the defacing mask.
    output_dir : Directory
        Directory where the mosaic image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    mosaic_file : File
        Path to the saved mosaic image.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_deface".format(
        **entities)
    mosaic_file = output_dir / f"{basename}mosaic.png"

    if not dryrun:
        plotting.plot_roi(
            mask_file,
            bg_img=im_file,
            display_mode="z",
            cut_coords=25,
            black_bg=True,
            alpha=0.6,
            colorbar=False,
            output_file=mosaic_file
        )
        arr = plt.imread(mosaic_file)
        cut = int(arr.shape[1] / 5)
        plt.figure()
        arr = np.concatenate(
            [arr[:, idx * cut: (idx + 1) * cut] for idx in range(5)], axis=0)
        plt.imshow(arr)
        plt.axis("off")
        plt.savefig(mosaic_file)

    return (mosaic_file, )
