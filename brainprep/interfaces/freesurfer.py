##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


"""
FreeSurfer functions.
"""

import os
from pathlib import Path
from typing import Optional, Union

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    outputdir,
    print_info,
    print_warn,
)
from ..wrappers import (
    cmdwrapper,
    pywrapper,
)


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def brainmask(
        image_file: File,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Skull-strip a BIDS-compliant anatomical image using FreeSurfer's
    `mri_synthstrip`.

    `mri_synthstrip` is a FreeSurfer command-line tool that applies
    SynthStrip, a deep learning–based skull-stripping method developed to
    work across diverse imaging modalities, resolutions, and subject
    population :footcite:p:`hoopes2022brainmask`.

    Parameters
    ----------
    image_file : File
        Path to the input image file (T1w, T2w, FLAIR, etc.).
    output_dir : Directory
        Directory where the reoriented image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Skull-stripping command-line.
    mask_file : File
        Skull-stripped brain image file.

    References
    ----------

    .. footbibliography::
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-{mod}_brainmask".format(
        **entities)
    mask_file = output_dir / f"{basename}.nii.gz"

    command = [
        "mri_synthstrip",
        "-i", str(image_file),
        "-m", str(mask_file),
        "--no-csf",
    ]

    return command, (mask_file, )


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def reconall(
        t1_file: File,
        output_dir: Directory,
        entities: dict,
        t2_file: Optional[File] = None,
        flair_file: Optional[File] = None,
        resume: bool = False) -> tuple[list[str], tuple[File]]:
    """
    Brain parcellation using FreeSurfer's `recon-all`.

    In FreeSurfer, `recon-all` is the main command used to perform automated
    cortical reconstruction and volumetric segmentation from structural MRI
    data. It includes multiple processing steps such as skull stripping,
    surface reconstruction, and anatomical labeling
    :footcite:p:`fischl2012freesurfer`.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w image file.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    t2_file : Optional[File], default None
        Path to the input T2w image file - used to improve the pial surface.
    flair_file : Optional[File], default None
        Path to the input FLAIR image file - used to improve the pial surface.
    resume : bool, default False
        If True, try to resume `recon-all`. This option is particulary usefull
        when a custom segmentation is used in `recon-all`.

    Returns
    -------
    command : list[str]
        Brain parcellation command-line.
    log_file : File
        The generated log file.

    References
    ----------

    .. footbibliography::
    """
    subject = f"sub-{entities['sub']}"
    log_file = output_dir / subject / "scripts" / "recon-all.log"

    command = [
        "recon-all", "-all",
        "-subjid", subject,
        "-i", str(t1_file),
        "-sd", str(output_dir),
        "-noappend",
        "-no-isrunning"
    ]
    if t2_file is not None:
        command.extend([
            "-T2", str(t2_file),
            "-T2pial"
        ])
    if flair_file is not None:
        command.extend([
            "-FLAIR", str(flair_file),
            "-FLAIRpial"
        ])
    if resume:
        command[1] = "-make all"

    return command, (log_file, )


@log_runtime(
    bunched=False)
@pywrapper
@coerceparams
def freesurfer_command_status(
        log_file: File,
        command: str,
        dryrun: bool = False) -> None:
    """
    Check the status of a FreeSurfer `recon-all` process from its log file.

    Parameters
    ----------
    log_file : File
        Path to the recon-all.log file.
    command : str
        The name of the command-line that pproduces the log file - used as
        a selector to define the success phrase.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Raises
    ------
    FileNotFoundError
        If no input log file.
    ValueError
        If the command-line is not supported.
    RuntimeError
        If recon-all failed or its status is unclear.

    Notes
    -----
    - Success is determined by the presence of the phrase
      "finished without error" in the last lines of the log.
    - Errors are detected by scanning for lines containing "ERROR:" or
      "FATAL:".
    - This function raises exceptions to signal failure or ambiguity, and
      does not return any value.

    Examples
    --------
    >>> reconall_status("/subjects/subj01/scripts/recon-all.log")
    # Raises no exception if successful
    """
    if not dryrun:

        if not log_file.is_file():
            raise FileNotFoundError(f"Log file not found: {log_file}")

        if command == "recon-all":
            success_phrase = "finished without error"
        elif command == "xhemireg":
            success_phrase = "xhemireg done"
        else:
            raise ValueError(
                "Command line not supported."
            )
        error_keywords = ["ERROR:", "FATAL:"]

        lines = log_file.read_text().splitlines()
        last_lines = lines[-20:]

        if any(success_phrase in line for line in last_lines):
            return
        errors = [
            line
            for line in lines
            if any(err in line for err in error_keywords)
        ]
        if errors:
            raise RuntimeError(
                f"Recon-all failed. Found {len(errors)} error(s):\n"
                f"{'\n'.join(errors)}"
            )
        raise RuntimeError(
            "Recon-all status unclear. No success or error markers found."
        )


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def localgi(
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Local Gyrification Index (localGI or lGI).

    It quantifies how much cortex is buried within the sulcal folds compared
    to the exposed outer surface - providing a localized version of the
    classical gyrification index :footcite:p:`schaer2008lgi`.

    Parameters
    ----------
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        LocalGI command-line.
    left_lgi_file : File
        The generated left hemisphere localGI file.
    right_lgi_file : File
        The generated right hemisphere localGI file.

    References
    ----------

    .. footbibliography::
    """
    subject = f"sub-{entities['sub']}"
    left_lgi_file = output_dir / subject / "surf" / "lh.pial_lgi"
    right_lgi_file = output_dir / subject / "surf" / "rh.pial_lgi"

    command = [
        "recon-all", "-localGI",
        "-subjid", subject, 
        "-sd", output_dir,
        "-no-isrunning"
    ]

    return command, (left_lgi_file, right_lgi_file)


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def surfreg(
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Surface-based registration to `fsaverage_sym` symmetric template.

    1) Registers the left hemisphere to the `fsaverage_sym` symmetric template.
    2) Registers the right hemisphere (already aligned to the left via
       xhemireg) to `fsaverage_sym` - use the interhemispheric registration
       surface (rh.sphere.reg.xhemi) instead of the standard one
       (rh.sphere.reg).

    Parameters
    ----------
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Registration command-line.
    left_reg_file : File
        Left hemisphere registered to `fsaverage_sym` symmetric template
    right_reg_file : File
        Right hemisphere registered to `fsaverage_sym` symmetric template
        via xhemi.
    """
    subject = f"sub-{entities['sub']}"
    left_reg_file = (
        output_dir / subject / "surf" / "lh.fsaverage_sym.sphere.reg"
    )
    right_reg_file = (
        output_dir / subject / "surf" / "xhemi" / "lh.fsaverage_sym.sphere.reg"
    )

    commands = [
        [
            "surfreg",
            "--s", subject, 
            "--lh",
            "--t", "fsaverage_sym",
            "--no-annot",
        ],
        [
            "surfreg",
            "--s", subject, 
            "--lh",
            "--t", "fsaverage_sym",
            "--no-annot",
            "--xhemi",
        ],
    ]

    return commands, (left_reg_file, right_reg_file)


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def xhemireg(
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[File]]:
    """
    Symmetric mapping of the right hemisphere to the left hemisphere space.
    within the subject's own space.

    Parameters
    ----------
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
        Mapping command-line.
    left_log_file : File
        The log of the left to right registration process.
    right_log_file : File
        The log of the right to left registration process.
    """
    subject = f"sub-{entities['sub']}"
    left_log_file = output_dir / subject / "xhemi" / "xhemireg.lh.log"
    right_log_file = output_dir / subject / "xhemi" / "xhemireg.rh.log"

    command = [
        "xhemireg",
        "--s", subject,
    ]

    return command, (left_log_file, right_log_file)


@log_runtime(
    bunched=False)
@outputdir
@coerceparams
def fsaveragesym_surfreg(
        template_dir: Directory,
        output_dir: Directory,
        entities: dict) -> tuple[File]:
    """
    Interhemispheric surface-based registration using the `fsaverage_sym`
    template, and FreeSurfer's `xhemireg` and `surfreg`.

    Applies the interhemispheric cortical surface-based pre-processing
    described in :footcite:p:`greve2013xhemi`. This includes:

    1) Registers the right hemisphere to the left hemisphere within the
       subject's own space.
    2) Registers the left hemisphere to the `fsaverage_sym` symmetric template.
    3) Registers the right hemisphere (already aligned to the left via
       xhemireg) to `fsaverage_sym` - use the interhemispheric registration
       surface (rh.sphere.reg.xhemi) instead of the standard one
       (rh.sphere.reg).

    Parameters
    ----------
    template_dir : Directory
        Path to the 'fsaverage_sym' template.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    left_reg_file : File
        Left hemisphere registered to `fsaverage_sym` symmetric template.
    right_reg_file : File
        Right hemisphere registered to `fsaverage_sym` symmetric template
        via xhemi.

    Notes
    -----
    - Removing the `left_reg_file` if trying to resume.

    References
    ----------

    .. footbibliography::
    """
    _template_dir = output_dir / "fsaverage_sym"
    if not _template_dir.is_symlink():
        os.symlink(template_dir, _template_dir)
    template_dir = _template_dir

    subject = f"sub-{entities['sub']}"
    os.environ["SUBJECTS_DIR"] = str(output_dir)
    left_reg_file = (
        output_dir / subject / "surf" / "lh.fsaverage_sym.sphere.reg"
    )
    if left_reg_file.is_file():
        print_info(f"removing: {left_reg_file}")
        os.remove(left_reg_file)

    left_log_file, right_log_file = xhemireg(
        output_dir,
        entities,
    )
    freesurfer_command_status(
        left_log_file,
        command="xhemireg",
    )
    freesurfer_command_status(
        right_log_file,
        command="xhemireg",
    )
    left_reg_file, right_reg_file = surfreg(
        output_dir,
        entities,
    )

    return (left_reg_file, right_reg_file)


@log_runtime(
    bunched=False)
@cmdwrapper
@coerceparams
def mris_apply_reg(
        src_file: File,
        trg_file: File,
        srcreg_file: File,
        targreg_file: File) -> tuple[list[str], tuple[File]]:
    """
    Apply a surface-based registration to a cortical surface data file.

    It transforms data from one surface space to another using a precomputed
    registration.

    Parameters
    ----------
    src_file : File
        Source cortical features.
    trg_file : File
        Target cortical features.
    srcreg_file : File
        Source reg file.
    targreg_file : File
        Target reg file.

    Returns
    -------
    command : list[str]
        Apply registration command-line.
    trg_file : File
        Target cortical features.
    """
    command = [
        "mris_apply_reg",
        "--src", str(src_file),
        "--trg", str(trg_file),
        "--streg", str(srcreg_file), str(targreg_file),
    ]

    return command, (trg_file, )


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
@coerceparams
def fsaveragesym_projection(
        left_reg_file: File,
        right_reg_file: File,
        template_dir: Directory,
        output_dir: Directory,
        entities: dict,
        dryrun: bool = False) -> tuple[File]:
    """
    Project the different cortical features to the 'fsaverage_sym' template
    space using FreeSurfer's `mris_apply_reg`.

    Map the left and right hemisphere cortical features to 'fsaverage_sym'
    left hemisphere. This includes the following features:
    - thickness
    - curvature
    - area
    - localGI
    - sulc

    Parameters
    ----------
    left_reg_file : File
        Left hemisphere registered to `fsaverage_sym` symmetric template.
    right_reg_file : File
        Right hemisphere registered to `fsaverage_sym` symmetric template
        via xhemi.
    template_dir : Directory
        Path to the 'fsaverage_sym' template.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    features: tuple
        A tuple containing features in the `fsaverage_sym` symmetric template.
        Each feature file is a MGH file with the suffix "fsaverage_sym". The
        features are returned in the following order:
        - lh_thickness_file
        - rh_thickness_file
        - lh_curv_file
        - rh_curv_file
        - lh_area_file
        - rh_area_file
        - lh_pial_lgi_file
        - rh_pial_lgi_file
        - lh_sulc_file
        - rh_sulc_file

    Notes
    -----
    - This function is resilient if a feature is missing. In this case a
      None is returned.
    """
    subject = f"sub-{entities['sub']}"
    reg_map = {
        "lh": left_reg_file,
        "rh": right_reg_file,
        "template": template_dir / "surf" / "lh.sphere.reg"
    }

    features = []
    for name in ("thickness", "curv", "area", "pial_lgi", "sulc"):
        for hemi in ("lh", "rh"):
            src_feature_file = (
                output_dir / subject / "surf" / f"{hemi}.{name}"
            )
            if not src_feature_file.is_file():
                print_warn(f"feature missing: {src_feature_file}")
                if not dryrun:
                    features.append(None)
                    continue
            trg_feature_file = (
                output_dir / subject / "surf" /
                f"{hemi}.{name}.fsaverage_sym.mgh"
            )
            if trg_feature_file.is_file():
                print_warn(f"overwrite file: {trg_feature_file}")
            mris_apply_reg(
                src_feature_file,
                trg_feature_file,
                reg_map[hemi],
                reg_map["template"],
            )
            features.append(trg_feature_file)

    return tuple(features)


@log_runtime(
    bunched=False)
@cmdwrapper
@coerceparams
def mri_convert(
        src_file: File,
        trg_file: File,
        reference_file: File) -> tuple[list[str], tuple[File]]:
    """
    Convert a source image and resample it to match the resolution,
    orientation, and voxel grid of a reference image using FreeSurfer's
    `mri_convert`.

    Parameters
    ----------
    src_file : File
        Source image.
    trg_file : File
        Target image.
    reference_file : File
        Reference image.

    Returns
    -------
    command : list[str]
        Conversion command-line.
    trg_file : File
        Target image.
    """
    command = [
        "mri_convert",
        "--resample_type", "nearest",
        "--reslice_like", str(reference_file),
        str(src_file),
        str(trg_file),
    ]

    return command, (trg_file, )


@log_runtime(
    bunched=False)
@outputdir
@coerceparams
def mgz_to_nii(
        output_dir: Directory,
        entities: dict) -> tuple[File]:
    """
    Convert FreeSurfer images back to original Nifti space.

    Convert FreeSurfer MGZ file in Nifti format and reslice the generated image
    as the 'mri/rawavg.mgz' image. A nearest neighbor interpolation is used.
    This includes the following images:
    - aparc+aseg
    - aparc.a2009s+aseg
    - aseg
    - wm
    - rawavg
    - ribbon
    - brain

    Parameters
    ----------
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    images: tuple
        A tuple containing converted images. The images are returned in the
        following order:
        - aparc_aseg_file
        - aparc_a2009s_aseg_file
        - aseg_file
        - wm_file
        - rawavg_file
        - ribbon_file
        - brain_file
    """
    subject = f"sub-{entities['sub']}"
    reference_file = output_dir / subject / "mri" / "rawavg.mgz"

    images = []
    for name in ("aparc+aseg", "aparc.a2009s+aseg", "aseg", "wm", "rawavg",
                 "ribbon", "brain"):
        src_file = output_dir / subject / "mri" / f"{name}.mgz"
        trg_file = output_dir / subject / "mri" / f"{name}.nii.gz"
        mri_convert(
            src_file,
            trg_file,
            reference_file,
        )
        images.append(trg_file)

    return tuple(images)
