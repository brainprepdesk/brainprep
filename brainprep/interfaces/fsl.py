##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


"""
FSL functions.
"""

import os
from pathlib import Path
from typing import Union

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import parse_bids_keys
from ..wrappers import cmdwrapper


@log_runtime(
    bunched=False)
@cmdwrapper
def reorient(
        image_file: File,
        output_dir: Directory) -> tuple[list[str], tuple[File]]:
    """
    Reorients a BIDS-compliant anatomical image using FSL's `fslreorient2std`.

    Parameters
    ----------
    image_file : File
        Path to the input image file.
    output_dir : Directory
        Directory where the reoriented image will be saved.

    Returns
    -------
    command : list[str]
        Reorientation command-line.
    reorient_file : File
        Reoriented input image file.

    Raises
    ------
    ValueError
        If the output directory does not exist or the input file is not
        BIDS-compliant.
    """
    image_file = str(image_file)
    output_dir = os.path.abspath(str(output_dir))
    entities = parse_bids_keys(image_file)

    if not os.path.isdir(output_dir):
        raise ValueError(
            f"The output directory '{output_dir}' does not exist."
        )
    if len(entities) == 0:
        raise ValueError(
            f"The input file '{image_file}' is not BIDS-compliant."
        )

    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_reorient".format(
        **entities)
    reorient_file = os.path.join(output_dir, f"{basename}.nii.gz")
    command = [
        "fslreorient2std",
        image_file,
        reorient_file
    ]

    return command, (reorient_file, )


@log_runtime(
    bunched=False)
@cmdwrapper
def deface(
        t1_file: File,
        output_dir: Directory) -> tuple[list[str],
                                        tuple[Union[File, list[File]]]]:
    """
    Defaces a BIDS-compliant T1-weighted anatomical image using FSL's
    `fsl_deface`.

    Parameters
    ----------
    t1_file : Path or str
        Path to the input T1w image file.
    output_dir : str
        Directory where the defaced T1w image will be saved.

    Returns
    -------
    command : list[str]
        Defacing command-line.
    deface_file : File
        Defaced input T1w image file.
    mask_file : File
        Defacing binary mask.
    vol_files : list[File]
        Defacing 3d rendering.

    Raises
    ------
    ValueError
        If the output directory does not exist or the input file is not
        BIDS-compliant.
    """
    t1_file = str(t1_file)
    output_dir = os.path.abspath(str(output_dir))
    entities = parse_bids_keys(t1_file)

    if not os.path.isdir(output_dir):
        raise ValueError(
            f"The output directory '{output_dir}' does not exist."
        )
    if len(entities) == 0:
        raise ValueError(
            f"The input file '{t1_file}' is not BIDS-compliant."
        )
    modality = entities.get("mod", entities.get("modality"))
    if modality is None or modality != "T1w":
        raise ValueError(
            f"The '{t1_file}' input anatomical file must be a T1w image."
        )

    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_deface".format(
        **entities)
    deface_file = os.path.join(output_dir, f"{basename}.nii.gz")
    mask_file = os.path.join(output_dir, basename + "mask.nii.gz")
    snap_pattern = os.path.join(output_dir, basename)
    command = [
        "fsl_deface",
        t1_file,
        deface_file,
        "-d", mask_file,
        "-f", "0.5",
        "-B",
        "-p", snap_pattern
    ]
    vol_files = [f"{snap_pattern}_{idx}.png" for idx in range(1, 3)]

    return command, (deface_file, mask_file, vol_files)
