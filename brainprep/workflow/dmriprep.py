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

import shutil

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
    print_info,
)


@coerceparams
@bids(
    process="dmriprep",
    bids_file="t1_file",
    add_subjects=True,
    container="neurospin/brainprep-dmriprep")
@log_runtime(
    title="Subject Level Diffusion Pre-Processing")
@save_runtime
def brainprep_dmriprep(
        t1_file: File,
        dwi_file: File,
        bvec_file: File,
        bval_file: File,
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Diffusion MRI pre-processing.

    Applies the pre-processing described in :footcite:p:`cai2021prequal`.
    This includes:

    1) Gradient direction sanity check.
    2) MP-PCA denoising.
    3) Gibbs unringing.
    4) N4 B1 bias field correction.
    5) Head Motion Correction (shelled schemes).
    6) Fieldmapless Distortion Correction: Synb0.
    7) HTML Report.

    Parameters
    ----------
    t1_file : File
        Path to the t1 image (used during Synb0 - synthesized b0 for diffusion
        distortion correction).
    dwi_file : File
        Path to the diffusion weighted image.
    bvec_file : File
        Path to the bvec file.
    bval_file : File
        Path to the bval file.
    output_dir : Directory
        Path to the output directory.
    keep_intermediate : bool
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging. Default False.

    Returns
    -------
    Bunch
        A dictionary-like object containing:

        - dwi_file: File - path to the NIIGZ pre-processed diffusion weighted
          image.
        - bvec_file: File - path to the TXT pre-processed bvec file.
        - bval_file: File - path to the TXT pre-processed bval file.
        - qc_file: File - path to the PDF visual report.

    Raises
    ------
    ValueError
        If the T1w file do not follow BIDS convension.

    Notes
    -----
    - For the Synb0 feature to work you must bind your FreeSurfer license in
      the '/APPS/freesurfer/license.txt' location.

    References
    ----------

    .. footbibliography::
    """
    workspace_dir = output_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)

    entities = parse_bids_keys(t1_file)
    if len(entities) == 0:
        raise ValueError(
            f"The T1w file '{t1_file}' is not BIDS-compliant."
        )

    dwi_file, bvec_file, bval_file, qc_file = interfaces.prequal_wf(
        t1_file,
        dwi_file,
        bvec_file,
        bval_file,
        workspace_dir,
        output_dir,
        entities,
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        dwi_file=dwi_file,
        bvec_file=bvec_file,
        bval_file=bval_file,
        qc_file=qc_file,
    )


@coerceparams
@bids(
    process="dmriprep",
    container="neurospin/brainprep-dmriprep")
@log_runtime(
    title="Group Level Diffusion Pre-Processing")
@save_runtime
def brainprep_group_dmriprep(
        output_dir: Directory,
        lower_fa_threshold: float = 0.3,
        upper_fa_threshold: float = 0.75,
        keep_intermediate: bool = False) -> Bunch:
    """
    Group level diffusion MRI pre-processing.

    Parameters
    ----------
    output_dir : Directory
        Working directory containing all the subjects.
    lower_fa_threshold : float
        Quality control lower threshold on the fractional anisotropy (FA).
        Default 0.3
    upper_fa_threshold : float
        Quality control upper threshold on the fractional anisotropy (FA).
        Default 0.75
    keep_intermediate : bool
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging. Default False

    Returns
    -------
    Bunch
        A dictionary-like object containing:

        - group_stats_file : File - a TSV file containing summary information
          on fiber bunbles and displacements.
        - histogram_files : list[File] - PNG files containing histograms of
          selected important information.
    """
    bundles = (
        "Genu_of_corpus_callosum_med_fa",
        "Body_of_corpus_callosum_med_fa",
        "Splenium_of_corpus_callosum_med_fa",
        "Corticospinal_tract_L_med_fa",
        "Corticospinal_tract_R_med_fa",
    )

    group_stats_file = interfaces.prequal_stats(
        output_dir / "qc",
        bundles,
        lower_fa_threshold,
        upper_fa_threshold,
    )

    histogram_files = [
        interfaces.plot_histogram(
            group_stats_file,
            "eddy_avg_abs_displacement",
            output_dir / "qc",
        ),
        *[
            interfaces.plot_histogram(
                group_stats_file,
                fa_bundle,
                output_dir / "qc",
                bar_coords=[lower_fa_threshold, upper_fa_threshold],
            ) for fa_bundle in bundles
        ],
    ]

    return Bunch(
        group_stats_file=group_stats_file,
        histogram_files=histogram_files,
    )
