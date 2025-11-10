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

from typing import Union

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    outputdir,
)
from ..wrappers import cmdwrapper


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def reorient(
        image_file: File,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Reorients a BIDS-compliant anatomical image using FSL's `fslreorient2std`.

    Parameters
    ----------
    image_file : File
        Path to the input image file.
    output_dir : Directory
        Directory where the reoriented image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Reorientation command-line.
    reorient_image_file : File
        Reoriented input image file.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_reorient".format(
        **entities)
    reorient_image_file = output_dir / f"{basename}.nii.gz"

    command = [
        "fslreorient2std",
        str(image_file),
        str(reorient_image_file)
    ]

    return command, (reorient_image_file, )


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def deface(
        t1_file: File,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[Union[File, list[File]]]]:
    """
    Defaces a BIDS-compliant T1-weighted anatomical image using FSL's
    `fsl_deface`.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w image file.
    output_dir : Directory
        Directory where the defaced T1w image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

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
        If the input image is not a T1-weighted image.
    """
    modality = entities.get("mod")
    if modality is None or modality != "T1w":
        raise ValueError(
            f"The '{t1_file}' input anatomical file must be a T1w image."
        )

    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_deface".format(
        **entities)
    deface_file = output_dir / f"{basename}.nii.gz"
    mask_file = output_dir / f"{basename}mask.nii.gz"
    snap_pattern = output_dir / basename

    command = [
        "fsl_deface",
        str(t1_file),
        str(deface_file),
        "-d", str(mask_file),
        "-f", "0.5",
        "-B",
        "-p", str(snap_pattern),
    ]
    vol_files = [f"{snap_pattern}_{idx}.png" for idx in range(1, 3)]

    return command, (deface_file, mask_file, vol_files)


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def applymask(
        image_file: File,
        mask_file: File,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Apply an isotropic resampling transformation to a BIDS-compliant image
    file using FSL's `fslmaths`.

    Parameters
    ----------
    image_file : File
        Path to the input image file.
    mask_file : File
        Path to a binary mask file.
    output_dir : Directory
        Directory where the masked image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Masking command-line.
    masked_image_file : File
        masked input image file.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-{mod}_applymask".format(
        **entities)
    masked_image_file = output_dir / f"{basename}.nii.gz"

    command = [
        "fslmaths",
        str(image_file),
        "-mas", str(mask_file),
        str(masked_image_file),
    ]

    return command, (masked_image_file, )


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def scale(
        image_file: File,
        scale: int,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Apply an isotropic resampling transformation to a BIDS-compliant image
    file using FSL's `flirt`.

    Parameters
    ----------
    image_file : File
        Path to the input image file.
    scale : int
        Scale factor applied in all directions.
    output_dir : Directory
        Directory where the scaled image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Scaling command-line.
    scaled_anatomical_file : File
        Scaled input image file.
    transform_file : File
        The associated transformaton file.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-{mod}_scale".format(
        **entities)
    scaled_anatomical_file = output_dir / f"{basename}.nii.gz"
    transform_file = output_dir / f"{basename}.txt"

    command = [
        "flirt",
        "-in", str(image_file),
        "-ref", str(image_file),
        "-applyisoxfm", str(scale),
        "-out", str(scaled_anatomical_file),
        "-omat", str(transform_file),
        "-verbose", "1",
    ]

    return command, (scaled_anatomical_file, transform_file)


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def affine(
        anatomical_file: File,
        template_file: File,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Affinely register a BIDS-compliant anatomical image to a template file
    using FSL's `flirt`.

    Parameters
    ----------
    image_file : File
        Path to the input image file.
    template_file: File
        Path to the image file defining the template space.
    output_dir : Directory
        Directory where the affine transformation will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Registration command-line.
    aligned_anatomical_file : File
        Aligned input image file.
    transform_file : File
        The affine transformaton file.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-{mod}_affine".format(
        **entities)
    aligned_anatomical_file = output_dir / f"{basename}.nii.gz"
    transform_file = output_dir / f"{basename}.txt"

    command = [
        "flirt",
        "-in", str(anatomical_file),
        "-ref", str(template_file),
        "-cost", "normmi",
        "-searchcost", "normmi",
        "-anglerep", "euler",
        "-bins", "256",
        "-interp", "trilinear",
        "-dof", "9",
        "-out", str(aligned_anatomical_file),
        "-omat", str(transform_file),
        "-verbose", "1"
    ]

    return command, (aligned_anatomical_file, transform_file)


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def applyaffine(
        image_file: File,
        template_file: File,
        transform_file: File,
        output_dir: Directory,
        entities: dict,
        interpolation: str = "spline") -> tuple[list[str], tuple[File]]:
    """
    Apply an affine transformaton to a BIDS-compliant image file using FSL's
    `flirt`.

    Parameters
    ----------
    image_file : File
        Path to the input image file.
    template_file: File
        Path to the image file defining the template space.
    transform_file : File
        Path to the affine tranformation file.
    output_dir : Directory
        Directory where the aligned image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    interpolation: str, default 'spline'
        The interpolation method: 'trilinear', 'nearestneighbour', 'sinc', or
        'spline'.

    Returns
    -------
    command : list[str]
        Alignement command-line.
    aligned_image_file : File
        Aligned input image file.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-{mod}_applyaffine".format(
        **entities)
    aligned_image_file = output_dir / f"{basename}.nii.gz"

    command = [
        "flirt",
        "-in", str(image_file),
        "-ref", str(template_file),
        "-init", str(transform_file),
        "-interp", str(interpolation),
        "-applyxfm",
        "-out", str(aligned_image_file),
    ]

    return command, (aligned_image_file, )
