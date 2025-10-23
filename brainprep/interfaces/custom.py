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
import shutil
from pathlib import Path
from typing import Union

import nibabel

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
def defacing_mask_diff(
        im1_file: File,
        im2_file: File,
        output_dir: Directory,
        entities: dict,
        threshold: float = 0.6,
        dryrun: bool = False) -> tuple[File]:
    """
    Computes a defacing mask by thresholding the intensity difference between
    two input images.

    Parameters
    ----------
    im1_file : File
        Path to the first image.
    im2_file : File
        Path to the second image.
    output_dir : Directory
        Directory where the defacing mask will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    threshold : float, default 0.6
        Threshold for intensity difference to define the mask.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    mask_file : File
        Path to the saved mask image.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_defacemask".format(
        **entities)
    mask_file = output_dir / f"{basename}.nii.gz"

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


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
def copyfiles(
        source_image_files: list[File],
        destination_image_files: list[File],
        output_dir: Directory,
        dryrun: bool = False) -> tuple[File]:
    """
    Move input image file to detination folder.

    Parameters
    ----------
    source_image_files : list[File]
        Path to the image to be copied.
    destination_image_files : list[File]
        Path to the locations where images will be copied.
    output_dir : Directory
        Directory where the images are copied.
    dryrun : bool, default False
        If True, skip actual computation and file writing.
    """
    if not dryrun:
        for src_path, dest_path in zip(source_image_files,
                                       destination_image_files):
            shutil.copy(src_path, dest_path)
