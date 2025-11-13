##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


"""
fMRIprep functions.
"""

import json
import shutil

import numpy as np
import pandas as pd
from nilearn import (
    datasets,
    image,
    plotting,
)
from nilearn.connectome import ConnectivityMeasure
from nilearn.interfaces.fmriprep import load_confounds
from nilearn.maskers import NiftiLabelsMasker

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    outputdir,
    parse_bids_keys,
    sidecar_from_file,
)
from ..wrappers import (
    cmdwrapper,
    pywrapper,
)


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@cmdwrapper
def fmriprep_wf(
        t1_file: File,
        func_files: list[File],
        dataset_description_file: File,
        freesurfer_dir: Directory,
        workspace_dir: Directory,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[list[File]]]:
    """
    Compute fMRI prep-processing using fMRIPrep.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w image file.
    func_files : list[File]
        Path to the input functional image files of one subject.
    dataset_description_file : File
        Path to the BIDS dataset description file.
    freesurfer_dir : Directory
        Path to an existing FreeSurfer subjects directory where the reconall
        command has already been performed.
    workspace_dir: Directory
        Working directory with the workspace of the current processing, and
        where subject specific data are symlinked.
    output_dir : Directory
        Directory where the prep-processing related outputs will be saved
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
       Pre-processing command-line.
    mask_files : File
       Brain masks in template spaces.
    fmri_rest_image_files : list[File]
       Pre-processed rfMRI volumes: 2mm MNI152NLin6Asym and
        MNI152NLin2009cAsym.
    fmri_rest_surf_file: File
       Pre-processed rfMRI surfaces: fsLR23k.
    confounds_file : File
       File with calculated confounds.
    qc_file : File
        Visual report.

    Notes
    -----
    - Creates BIDS subject specific working directory using copy in
      'rawdata'.
    - Store intermediate pre-processing outputs in 'work'.
    """
    rawdata_dir = workspace_dir / "rawdata"
    anat_dir = rawdata_dir / "anat"
    func_dir = rawdata_dir / "func"
    work_dir = workspace_dir / "work"
    for path in (anat_dir, func_dir, work_dir):
        path.mkdir(parents=True, exist_ok=True)
    subject, session = entities["sub"], entities["ses"]

    for source_file, target_dir in zip(
            [t1_file, *func_files],
            [anat_dir] + [func_dir] * len(func_files)):
        sidecar_source_file = sidecar_from_file(source_file)
        if not (target_dir / source_file.name).is_file():
            shutil.copy(
                source_file,
                target_dir / source_file.name,
            )
            shutil.copy(
                sidecar_source_file,
                target_dir / sidecar_source_file.name,
            )
    if not (rawdata_dir / dataset_description_file.name).is_file():
        shutil.copy(
            dataset_description_file,
            rawdata_dir / dataset_description_file.name,
        )

    fmriprep_dir = (
        output_dir / f"sub-{subject}" / f"ses-{session}"
    )
    qc_file = (
        fmriprep_dir / f"sub-{subject}.html"
    )
    rfmri_outputs = []
    for func_file in func_files:
        func_entities = parse_bids_keys(func_file)
        if func_entities["task"] == "rest":
            basename = (
                "sub-{sub}_ses-{ses}_task-rest_run-{run}".format(
                    **func_entities)
            )
            mask_files = [
                (
                    fmriprep_dir /
                    "func" /
                    f"{basename}_space-{template}_desc-brain_mask.nii.gz"
                )
                for template in ("MNI152NLin6Asym_res-2",
                                 "MNI152NLin2009cAsym")
            ]
            fmri_rest_image_files = [
                (
                    fmriprep_dir /
                    "func" /
                    f"{basename}_space-{template}_desc-preproc_bold.nii.gz",
                )
                for template in ("MNI152NLin6Asym_res-2",
                                 "MNI152NLin2009cAsym")
            ]
            fmri_rest_surf_file = (
                fmriprep_dir /
                "func" /
                f"{basename}_space-fsLR_den-91k_bold.dtseries.nii",

            )
            confounds_file = (
                fmriprep_dir /
                "func" /
                f"{basename}_desc-confounds_timeseries.tsv"
            )
            rfmri_outputs.append([
                mask_files,
                fmri_rest_image_files,
                fmri_rest_surf_file,
                confounds_file,
            ])

    command = [
        "fmriprep",
        str(rawdata_dir),
        str(output_dir),
        "participant",
        "--fs-subjects-dir", str(freesurfer_dir),
        "-w", str(work_dir),
        "--n_cpus", "1",
        "--stop-on-first-crash",
        "--fs-license-file", "/code/freesurfer.txt",
        "--skip_bids_validation",
        "--force bbr",
        "--no-msm",
        "--cifti-output", "91k",
        "--output-spaces", (
            "MNI152NLin2009cAsym MNI152NLin6Asym:res-2 fsaverage fsLR"),
        "--ignore", "slicetiming",
        "--participant_label", subject,
    ]

    return command, (rfmri_outputs, qc_file)


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def func_vol_connectivity(
        fmri_rest_image_file: File,
        mask_file: File,
        counfounds_file: File,
        output_dir: Directory,
        entities: dict,
        low_pass: float = 0.1,
        high_pass: float = 0.01,
        scrub: int = 5,
        fd_threshold: float = 0.2,
        std_dvars_threshold: int = 3,
        detrend: bool = True,
        standardize: bool = True,
        remove_volumes: bool = True,
        fwhm: float = 0.,
        dryrun: bool = False):
    """
    ROI-based functional connectivity from volumetric fMRI data.

    This function uses Nilearn to extract ROI time series and compute
    functional connectivity based on the Schaefer 200 ROI atlas. It applies
    the Yeo et al. (2011) preprocessing pipeline, including detrending,
    filtering, confound regression, and standardization.

    Connectivity is computed using Pearson correlation and saved as a TSV file
    following BIDS derivatives conventions. The output filename includes BIDS
    entities and specifies the atlas and metric used.

    Preprocessing steps:
    1. Detrending
    2. Low-pass and high-pass filtering
    3. Confound regression
    4. Standardization

    Filtering:
    - Low-pass removes high-frequency noise (> 0.1 Hz by default).
    - High-pass removes scanner drift and low-frequency fluctuations
      (< 0.01 Hz by default).

    Confounds:
    - 1 global signal
    - 12 motion parameters + derivatives
    - 8 discrete cosine basis regressors
    - 2 tissue-based confounds (white matter and CSF)
    Total: 23 base confound regressors

    Scrubbing:
    - Volumes with excessive motion (FD > 0.2 mm or standardized DVARS > 3)
      are removed.
    - Segments shorter than `scrub` frames are discarded.
    - One-hot regressors are added for scrubbed volumes.

    Parameters
    ----------
    fmri_rest_image_file : File
       Pre-processed resting-state fMRI volumes.
    mask_file : File
        Brain mask used to restrict signal cleaning.
    counfounds_file : File
        Confounds file from fMRIPrep.
    output_dir : Directory
        Output directory for generated files.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    low_pass : float, default 0.1
        Low-pass filter cutoff frequency in Hz. Set to None to disable.
    high_pass : float, default 0.01
        High-pass filter cutoff frequency in Hz. Set to None to disable.
    scrub : int, default 5
        After accounting for time frames with excessive motion, further remove
        segments shorter than the given number. The default value is 5. When
        the value is 0, remove time frames based on excessive framewise
        displacement and DVARS only. One-hot encoding vectors are added as
        regressors for each scrubbed frame.
    fd_threshold : float, default 0.2
        Framewise displacement threshold for scrub. This value is typically
        between 0 and 1 mm.
    std_dvars_threshold : float, default 3
        Standardized DVARS threshold for scrub. DVARs is defined as root mean
        squared intensity difference of volume N to volume N + 1. D refers
        to temporal derivative of timecourses, VARS referring to root mean
        squared variance over voxels.
    detrend : bool, default True
        Detrend data prior to confound removal.
    standardize : default True
        Set this flag if you want to standardize the output signal between
        [0 1].
    remove_volumes : bool, default True
        This flag determines whether contaminated volumes should be removed
        from the output data.
    fwhm : float or list, default 0.
        Smoothing strength, expressed as as Full-Width at Half Maximum
        (fwhm), in millimeters. Can be a single number ``fwhm=8``, the width
        is identical along x, y and z or ``fwhm=0``, no smoothing is performed.
        Can be three consecutive numbers, ``fwhm=[1,1.5,2.5]``, giving the fwhm
        along each axis.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    connectivity_file : File
        Path to the TSV file containing the ROI-to-ROI connectivity matrix.

    Notes
    -----
    - ROI atlas used: Schaefer 2018 (200 regions)
    - Connectivity metric: Pearson correlation
    """
    subject, session = entities["sub"], entities["ses"]
    fmriprep_dir = (
        output_dir / f"sub-{subject}" / f"ses-{session}"
    )
    basename = "sub-{sub}_ses-{ses}_task-rest_run-{run}_space-{space}".format(
        **entities)
    if "res" in entities:
        basename += f"_res-{entities['res']}"
    basename = f"{basename}_atlas-schaefer200_desc-correlation_connectivity"
    connectivity_file = (
        fmriprep_dir /
        f"{basename}.tsv"
    )

    if not dryrun:
        atlas_dir = output_dir / "atlases"
        atlas_dir.mkdir(parents=True, exist_ok=True)
        atlas = datasets.fetch_atlas_schaefer_2018(
            n_rois=200,
            data_dir=atlas_dir,
        )
        plotting.plot_roi(
            atlas.maps,
            cut_coords=(8, -4, 9),
            colorbar=True,
            cmap="Paired",
            output_file=atlas_dir / "schaefer.png",
        )

        sidecar_file = (
            fmri_rest_image_file.with_suffix("").with_suffix(".json")
        )
        with open(sidecar_file) as of:
            info = json.load(of)
        tr = info["RepetitionTime"]

        select_confounds, sample_mask = load_confounds(
            fmri_rest_image_file,
            strategy=["high_pass", "motion", "wm_csf", "global_signal"],
            motion="derivatives",
            wm_csf="basic",
            global_signal="basic",
            scrub=scrub,
            fd_threshold=fd_threshold,
            std_dvars_threshold=std_dvars_threshold
        )
        if not remove_volumes:
            sample_mask = None

        clean_im = image.clean_img(
            fmri_rest_image_file,
            standardize=standardize,
            detrend=detrend,
            confounds=select_confounds,
            t_r=tr,
            high_pass=high_pass,
            low_pass=low_pass,
            mask_img=mask_file
        )

        if np.array(fwhm).sum() > 0.0:
            clean_im = image.smooth_img(clean_im, fwhm)

        masker = NiftiLabelsMasker(
            labels_img=atlas.maps,
            verbose=5,
        )
        timeseries = masker.fit_transform(
            clean_im,
            sample_mask=sample_mask
        )

        correlation_measure = ConnectivityMeasure(kind="correlation")
        correlation_matrix = correlation_measure.fit_transform(
            [timeseries],
        )[0]
        np.fill_diagonal(correlation_matrix, 0)
        correlation_df = pd.DataFrame(
            correlation_measure, index=atlas.labels, columns=atlas.labels
        )
        correlation_df.to_csv(connectivity_file, sep="\t")
        display = plotting.plot_matrix(
            correlation_matrix,
            figure=(10, 8),
            labels=atlas.labels,
            reorder=True,
        )
        display.figure.savefig(fmriprep_dir / f"{basename}.png")

    return (connectivity_file, )
