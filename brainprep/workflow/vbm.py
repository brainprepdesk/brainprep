##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


"""
Diffusion MRI pre-processing.
"""

import brainprep.interfaces as interfaces

from ..config import (
    DEFAULT_OPTIONS,
    brainprep_options,
)
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
)


@coerceparams
@bids(
    process="vbm",
    bids_file="t1_file",
    add_subjects=True,
    container="neurospin/brainprep-vbm")
@log_runtime(
    title="Subject Level VBM Pre-Processing")
@save_runtime
def brainprep_vbm(
        t1_file: File,
        output_dir: Directory,
        keep_intermediate: bool = False):
    """
    Voxel based morphometry (VBM) pre-processing.

    Applies the VBM pre-processing described in
    :footcite:p:`dufumier2022openbhb`.

    Parameters
    ----------
    t1_file : File
        Path to the t1 image.
    output_dir : Directory
        Path to the output directory.
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - gm_file : File - path to the NIIGZ modulated, normalized gray matter
          segmentation of the input T1-weighted MRI image.
        - qc_file : File - path to the PDF visual report.
        - batch_file : File - path to the CAT12 batch file.

    References
    ----------

    .. footbibliography::
    """
    entities = parse_bids_keys(t1_file)
    if len(entities) == 0:
        raise ValueError(
            f"The T1w file '{t1_file}' is not BIDS-compliant."
        )

    batch_file = interfaces.write_catbatch(
        [t1_file],
        output_dir.parent,
        [entities],
    )
    gm_files, qc_files = interfaces.cat12vbm_wf(
        [t1_file],
        batch_file,
        output_dir.parent,
        [entities],
    )

    return Bunch(
        gm_file=gm_files[0],
        qc_file=qc_files[0],
        batch_file=batch_file,
    )


@coerceparams
@bids(
    process="vbm",
    bids_file="t1_files",
    add_subjects=True,
    longitudinal=True,
    container="neurospin/brainprep-vbm")
@log_runtime(
    title="Longitudinal VBM Pre-Processing")
@save_runtime(
    parent=True)
def brainprep_longitudinal_vbm(
        t1_files: list[File],
        model: int,
        output_dir: Directory,
        keep_intermediate: bool = False):
    """
    Longitudinal voxel based morphometry (VBM) pre-processing.

    Applies the VBM pre-processing described in
    :footcite:p:`dufumier2022openbhb`.

    Parameters
    ----------
    t1_file : File
        Path to the t1 image.
    model : int
        Longitudinal model choice: 1  short time (weeks), 2 long time (years)
        between images sessions.
    output_dir : Directory
        Path to the output directory.
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - gm_files : list[File] - path to the NIIGZ modulated, normalized gray
          matter segmentations of the input T1-weighted MRI images.
        - qc_files : list[File] - path to the PDF visual reports.
        - batch_file : File - path to the CAT12 batch file.

    References
    ----------

    .. footbibliography::
    """
    entities = [
        parse_bids_keys(path) for path in t1_files
    ]
    for info, path in zip(entities, t1_files):
        if len(info) == 0:
            raise ValueError(
                f"The T1w file '{path}' is not BIDS-compliant."
            )

    batch_file = interfaces.write_catbatch(
        t1_files,
        output_dir.parent,
        entities,
    )
    gm_files, qc_files = interfaces.cat12vbm_wf(
        t1_files,
        batch_file,
        output_dir.parent,
        entities,
    )

    return Bunch(
        gm_files=gm_files,
        qc_files=qc_files,
        batch_file=batch_file,
    )


@coerceparams
@bids(
    process="vbm",
    container="neurospin/brainprep-vbm")
@log_runtime(
    title="Group Level VBM Pre-Processing")
@save_runtime
def brainprep_group_vbm(
        output_dir: Directory,
        ncr_threshold: float = 4.5,
        iqr_threshold: float = 4.5,
        correlation_threshold: float = 0.5,
        longitudinal: bool = False,
        keep_intermediate: bool = False) -> Bunch:
    """
    Group-level voxel based morphometry (VBM) pre-processing.

    Summarizes the generated ROI-based features and applies the quality
    control described in :footcite:p:`dufumier2022openbhb`. This includes:

    1) Generate TSV tables of CAT12 VBM GM, WM and CSF features for different
       atlases.
    2) Apply quality checks on the quality metrics described below.
    3) Generate a histogram showing the distribution of the selected
       quality metrics.

    The following quuality metrics are considered:
    - Image Correlation Ratio (ICR) - Measures how well the subject's image
      aligns with a reference template. High ICR suggests good
      registration quality.
    - Noise to Contrast Ratio (NCR) - Assesses image clarity by comparing
      noise levels to tissue contrast. Lower NCR may indicate poor image
      quality.
    - Image Quality Rating (IQR) - A composite score summarizing overall
      scan quality. Combines multiple metrics like noise, resolution,
      and bias field. Higher IQR = better quality.

    Parameters
    ----------
    output_dir : Directory
        Working directory containing all the subjects.
    ncr_threshold : float, default 4.5
         Quality control threshold on the NCR scores.
    iqr_threshold : float, default 4.5
         Quality control threshold on the IQR scores.
    correlation_threshold : float, default 0.5
        Quality control threshold on the correlation score.
    longitudinal : bool, default False
        If True, consider the longitudinal data as inputs.
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - morphometry_files : list[File] - a TSV file containing ROI-based
          GM, WM and CSF features for different atlases.
        - correlations_file : File - a TSV file containing mean correlation
          of each input image to the atlas image.
        - group_stats_file : File - a TSV file containing quality metrics
          such as NCR, ICR and IQR.
        - histogram_files : list[File] - PNG files containing histograms of
          selected important information.

    Notes
    -----
    - This workflow can either be used on cross-sectional or longitudinal
      data.
    """
    if longitudinal:
        output_dir /= "longitudinal"
    opts = brainprep_options.get()
    darteltpm_file = opts.get(
        "darteltpm_file", DEFAULT_OPTIONS["darteltpm_file"]
    )

    morphometry_files = interfaces.cat12vbm_morphometry(
        output_dir / "morphometry",
    )

    correlations_file = interfaces.mean_correlation(
        output_dir / "subjects" / "sub-*" / "ses-*" / "mri" / "wm*_T1w.nii",
        darteltpm_file,
        output_dir / "qc",
        correlation_threshold,
    )
    group_stats_file = interfaces.cat12vbm_stats(
        output_dir / "qc",
        ncr_threshold,
        iqr_threshold,
    )
    histogram_files = [
        interfaces.plot_histogram(
            correlations_file,
            "mean_correlation",
            output_dir / "qc",
            bar_coords=[correlation_threshold],
        ),
        interfaces.plot_histogram(
            group_stats_file,
            "NCR",
            output_dir / "qc",
            bar_coords=[ncr_threshold],
        ),
        interfaces.plot_histogram(
            group_stats_file,
            "IQR",
            output_dir / "qc",
            bar_coords=[iqr_threshold],
        ),
    ]

    return Bunch(
        morphometry_files=morphometry_files,
        correlations_file=correlations_file,
        group_stats_file=group_stats_file,
        histogram_files=histogram_files,
    )
