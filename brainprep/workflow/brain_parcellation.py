##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Brain parcellation pre-processing.
"""

import shutil
from typing import Optional

import brainprep.interfaces as interfaces

from ..reporting import (
    log_runtime,
    save_runtime,
)
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    Bunch,
    bids,
    coerceparams,
    parse_bids_keys,
    print_deprecated,
    print_info,
)


@bids(
    process="brain_parcellation",
    bids_file="t1_file",
    add_subjects=True,
    container="neurospin/brainprep-brainparc")
@log_runtime(
    title="Subject Level Brain Parcellation")
@save_runtime
@coerceparams
def brainprep_brainparc(
        t1_file: File,
        template_dir: Directory,
        output_dir: Directory,
        do_lgi: bool = False,
        wm_file: Optional[File] = None,
        keep_intermediate: bool = False) -> Bunch:
    """
    Brain parcellation pre-processing.

    Applies the brain parcellation pre-processing described in
    :footcite:p:`dufumier2022openbhb`. This includes:

    1) Automated cortical reconstruction and volumetric segmentation from
       structural T1w MRI data using FreeSurfer's `recon-all`.
    2) Compute local Gyrification Index (localGI or lGI) - optional.
    3) Interhemispheric surface-based registration using the `fsaverage_sym`
       template.
    4) Project the different cortical features to the 'fsaverage_sym' template
       space.
    5) Convert FreeSurfer images back to original Nifti space.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w image file.
    template_dir : Directory
        Path to the 'fsaverage_sym' template.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    do_lgi : bool, default False
        Perform the Local Gyrification Index (LGI) computation - requires
        Matlab.
    wm_file : Optional[File], default None
        Path to the custom white matter mask - we assume `recon-all` has been
        run at least upto the 'wm.mgz' file creation. It has to be
        in the subject's FreeSurfer space (1mm iso + aligned with brain.mgz)
        with values in [0, 1] (i.e. probability of being white matter).
        For example, it can be the 'brain_pve_2.nii.gz' white matter
        probability map created by FSL `fast`.

        .. deprecated:: 1.0.0

        .. admonition:: Do not use ``wm_file``!
           :class: important

           This option was removed as it is never used in Population Imaging
           studies. This parameter has no effect!
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - subject_dir: Directory - the FreeSurfer subject directory.
        - left_reg_file : File - left hemisphere registered to
          `fsaverage_sym` symmetric template.
        - right_reg_file : File - right hemisphere registered to
          `fsaverage_sym` symmetric template via xhemi.
        - features : tuple[File] - a tuple containing features in the
          `fsaverage_sym` symmetric template - each feature file is a MGH
          file with the suffix "fsaverage_sym" and is available in the
          'surf' folder.
        - images : tuple[File] — a tuple containing converted images - a
          Nifti file available in the 'mri' folder.
        - brainparc_image_file : File - a PNG image of the GM mask and GM, WM,
          CSF tissues histograms.

    Notes
    -----
    This workflow assumes the T1w image is organized in BIDS.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_brainparc
    >>> brainprep_brainparc(t1_file, template_dir, output_dir)

    Raises
    ------
    ValueError
        If the input T1w file is not BIDS-compliant.

    References
    ----------

    .. footbibliography::
    """
    workspace_dir = output_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"setting workspace directory: {workspace_dir}")

    entities = parse_bids_keys(t1_file)
    if len(entities) == 0:
        raise ValueError(
            f"The T1w file '{t1_file}' is not BIDS-compliant."
        )
    if wm_file is not None:
        print_deprecated(
            "You passed a white matter file as input. This behavior is "
            "deprecated and will be removed in version >1."
        )

    log_file = interfaces.reconall(
        t1_file,
        output_dir,
        entities,
        resume=False,
    )
    interfaces.freesurfer_command_status(
        log_file,
        command="recon-all",
    )
    if do_lgi:
        left_lgi_file, right_lgi_file = interfaces.localgi(
            output_dir,
            entities,
        )
        interfaces.freesurfer_command_status(
            log_file,
            command="recon-all",
        )
    left_reg_file, right_reg_file = interfaces.fsaveragesym_surfreg(
        template_dir,
        output_dir,
        entities,
    )
    (lh_thickness_file, rh_thickness_file, lh_curv_file, rh_curv_file,
     lh_area_file, rh_area_file, lh_pial_lgi_file, rh_pial_lgi_file,
     lh_sulc_file, rh_sulc_file) = interfaces.fsaveragesym_projection(
        left_reg_file,
        right_reg_file,
        template_dir,
        output_dir,
        entities,
    )
    (aparc_aseg_file, aparc_a2009s_aseg_file, aseg_file, wm_file,
     rawavg_file, ribbon_file, brain_file) = interfaces.mgz_to_nii(
        output_dir,
        entities,
    )
    (wm_mask_file, gm_mask_file, csf_mask_file,
     brain_mask_file) = interfaces.freesurfer_tissues(
        workspace_dir,
        output_dir,
        entities,
    )
    brainparc_image_file = interfaces.plot_brainparc(
        wm_mask_file,
        gm_mask_file,
        csf_mask_file,
        brain_mask_file,
        output_dir,
        entities,
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        subject_dir=output_dir / f"run-{entities['run']}",
        left_reg_file=left_reg_file,
        right_reg_file=right_reg_file,
        lh_thickness_file=lh_thickness_file,
        rh_thickness_file=rh_thickness_file,
        lh_curv_file=lh_curv_file,
        rh_curv_file=rh_curv_file,
        lh_area_file=lh_area_file,
        rh_area_file=rh_area_file,
        lh_pial_lgi_file=lh_pial_lgi_file,
        rh_pial_lgi_file=rh_pial_lgi_file,
        lh_sulc_file=lh_sulc_file,
        rh_sulc_file=rh_sulc_file,
        aparc_aseg_file=aparc_aseg_file,
        aparc_a2009s_aseg_file=aparc_a2009s_aseg_file,
        aseg_file=aseg_file,
        wm_file=wm_file,
        rawavg_file=rawavg_file,
        ribbon_file=ribbon_file,
        brain_file=brain_file,
        brainparc_image_file=brainparc_image_file,
    )


@bids(
    process="brain_parcellation",
    bids_file="t1_files",
    add_subjects=True,
    longitudinal=True,
    container="neurospin/brainprep-brainparc")
@log_runtime(
    title="Longitudinal Brain Parcellation")
@save_runtime(
    parent=True)
@coerceparams
def brainprep_longitudinal_brainparc(
        t1_files: list[File],
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Longitudinal brain parcellation preprocessing.

    Applies the longitudinal brain parcellation pre-processing described in
    :footcite:p:`reuter2012freesurferlong`. This includes:

    1) the creation of a template for this subject.
    2) the parcellation refinementsfrom the new generated template.

    Parameters
    ----------
    t1_files : list[File]
        Path to the t1 images.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - subject_dirs: list[Directory] - the FreeSurfer subject directories.

    Notes
    -----
    This workflow assumes the T1w images are organized in BIDS.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_longitudinal_brainparc
    >>> brainprep_longitudinal_brainparc(t1_files, output_dir)

    Raises
    ------
    ValueError
        If the input T1w files are not BIDS-compliant.

    References
    ----------

    .. footbibliography::
    """
    workspace_dir = (
        output_dir.parent /
        "workspace"
    )
    workspace_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"setting workspace directory: {workspace_dir}")

    entities = [
        parse_bids_keys(path) for path in t1_files
    ]
    for info, path in zip(entities, t1_files):
        if len(info) == 0:
            raise ValueError(
                f"The T1w file '{path}' is not BIDS-compliant."
            )

    log_template_file, log_files = interfaces.reconall_longitudinal(
        workspace_dir,
        output_dir.parent,
        entities,
    )
    for log_file in [log_template_file, *log_files]:
        interfaces.freesurfer_command_status(
            log_file,
            command="recon-all",
        )
    subject_dirs = []
    for log_file in log_files:
        identifier = log_file.parent.parent.name.split(".long.")[0]
        subject_name, session_name, run_name = identifier.split("_")
        subject_dirs.append(
            interfaces.movedir(
                source_dir=log_file.parent.parent.parent,
                output_dir=(
                    output_dir.parent /
                    session_name /
                    run_name
                ),
                content=True,
            )
        )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        subject_dirs=subject_dirs,
    )


@bids(
    process="brain_parcellation",
    container="neurospin/brainprep-brainparc")
@log_runtime(
    title="Group Level Brain Parcellation")
@save_runtime
@coerceparams
def brainprep_group_brainparc(
        output_dir: Directory,
        euler_threshold: int = -217,
        longitudinal: bool = False,
        keep_intermediate: bool = False) -> Bunch:
    """
    Group level brain parcellation pre-processing.

    Summarizes the generated FreeSurfer features and applies the quality
    control described in :footcite:p:`rosen2018euler`. This includes:

    1) Generate text/ascii tables of FreeSurfer parcellation stats data
       '?h.aparc.stats' for both templates (Desikan & Destrieux) and
       volumetric data for subcortical brain structures 'aseg.stats'.
    2) Apply the FreeSurfer's Euler number, which summarizes the topological
       complexity of the reconstructed cortical surface as a quality
       control.
    3) Generate a histogram showing the distribution of Euler numbers.

    Parameters
    ----------
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    euler_threshold : int, default -217
        Quality control threshold on the Euler number.
    longitudinal : bool, default False
        If True, consider the longitudinal data as inputs.
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - summary_files : tuple[File] - a tuple containing FreeSurfer summary
          stats - each file is a CSV file with the prefix 'aparc_*_stats' for
          Desikan cortical feautes, 'aparc2009s_*_stats' for Destrieux cortical
          features, and 'aseg_*_stats' for volumetric subcortical brain
          structure features.

    Notes
    -----
    - This workflow can either be used on cross-sectional or longitudinal
      data.

    References
    ----------

    .. footbibliography::
    """
    if longitudinal:
        output_dir /= "longitudinal"
    workspace_dir = output_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"setting workspace directory: {workspace_dir}")

    summary_files = interfaces.freesurfer_features_summary(
        workspace_dir,
        output_dir,
    )
    euler_numbers_file = interfaces.freesurfer_euler_numbers(
        output_dir,
    )
    euler_numbers_histogram_file = interfaces.plot_histogram(
        euler_numbers_file,
        "euler_number",
        output_dir / "qc",
        bar_coords=[euler_threshold],
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
            summary_files=summary_files,
            euler_numbers_file=euler_numbers_file,
            euler_numbers_histogram_file=euler_numbers_histogram_file,
        )
