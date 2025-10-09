##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Custom functions.
"""

import numpy as np
import os
from pathlib import Path
from typing import Union

import nibabel

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import parse_bids_keys
from ..wrappers import pywrapper


@log_runtime(
    bunched=False)
@pywrapper
def defacing_mask_diff(
        im1_file: File,
        im2_file: File,
        output_dir: Directory,
        threshold: float = 0.6,
        dryrun: bool = False) -> tuple[File]:
    """
    Computes a defacing mask by thresholding the intensity difference between
    two input images.

    Parameters
    ----------
    im1_file: File
        Path to the first image.
    im2_filee: File
        Path to the second image.
    output_dir : Directory
        Directory where the defacing mask will be saved.
    threshold : float, default 0.6
        Threshold for intensity difference to define the mask.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    mask_file : File
        Path to the saved mask image.
    """
    im1_file = str(im1_file)
    im2_file = str(im2_file)
    output_dir = os.path.abspath(str(output_dir))

    entities = parse_bids_keys(im1_file)
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_defacemask".format(
        **entities)
    mask_file = os.path.join(output_dir, f"{basename}.nii.gz")

    if not dryrun:
        im1 = nibabel.load(im1_file)
        im2 = nibabel.load(im2_file)
        mask = np.abs(im1.get_fdata() - im2.get_fdata())
        indices = np.where(mask > threshold)
        mask[...] = 0
        mask[indices] = 1
        im_mask = nibabel.Nifti1Image(mask, im1.affine)
        nibabel.save(im_mask, mask_file)

    return (mask_file, )
