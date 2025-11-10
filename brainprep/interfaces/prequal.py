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

import glob
import os
import shutil

import pandas as pd

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    outputdir,
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
def prequal(
        t1_file: File,
        dwi_file: File,
        bvec_file: File,
        bval_file: File,
        workspace_dir: Directory,
        output_dir: Directory,
        entities: dict) -> tuple[list[str], tuple[list[File]]]:
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
    workspace_dir: Directory
        Working directory with the workspace of the current processing.
    output_dir : Directory
        Directory where the prep-processing related outputs will be saved
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[str]
       Pre-processing command-line.
    dwi_file : File
        Path to the pre-processed diffusion weighted image.
    bvec_file : File
        Path to the pre-processed bvec file.
    bval_file : File
        Path to the pre-processed bval file.
    qc_file : File
        Visual report.

    Notes
    -----
    - For the Synb0 feature to work you must bind your FreeSurfer license in
      the '/APPS/freesurfer/license.txt' location.

    References
    ----------

    .. footbibliography::
    """
    # FIXME: update dataset for valid sidecars
    # sidecar_file = (
    #     dwi_file.with_suffix("").with_suffix(".json")
    # )
    # with open(sidecar_file) as of:
    #     info = json.load(of)
    pe = "i"  # info["PhaseEncodingAxis"]
    readout_time = 1  # info["EstimatedTotalReadoutTime"]

    if pe not in ("i", "j", "k", "i-", "j-", "k-"):
        raise ValueError(
            f"Invalid phase encoding direction: {pe}"
        )
    pe_sign = "+" if len(pe) == 1 else "-"
    pe = pe[0]
    config = [
        dwi_file.name.split(".")[0],
        pe_sign,
        readout_time
    ]
    config = pd.DataFrame(config).T
    config_file = workspace_dir / "dtiQA_config.csv"
    config.to_csv(config_file, sep=",", header=False, index=False)

    shutil.copy(dwi_file, workspace_dir)
    shutil.copy(bvec_file, workspace_dir)
    shutil.copy(bval_file, workspace_dir)
    shutil.copy(t1_file, workspace_dir / "t1.nii.gz")

    dwi_file = output_dir / "PREPROCESSED" / "dwmri.nii.gz"
    bvec_file = output_dir / "PREPROCESSED" / "dwmri.bvec"
    bval_file = output_dir / "PREPROCESSED" / "dwmri.bval"
    qc_file = output_dir / "PDF" / "dtiQA.pdf"

    command = [
        "xvfb-run",
        "-a",
        "--server-num=1",
        "--server-args='-screen 0 1600x1280x24 -ac'",
        "bash", "/CODE/run_dtiQA.sh",
        str(workspace_dir),
        str(output_dir),
        pe
    ]

    return command, (dwi_file, bvec_file, bval_file, qc_file)


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
@coerceparams
def prequal_stats(
        output_dir: Directory,
        bundles: list[str],
        lower_fa_threshold: int = 0.3,
        upper_fa_threshold: int = 0.75,
        dryrun: bool = False) -> tuple[File]:
    """
    Parse the Prequal's stats for all subjects and applies a
    quality control on some bundles mean FA values.

    Parameters
    ----------
    output_dir : Directory
        Working directory containing the outputs.
    bundles : str
        Bundle names as define in PreQual.
    lower_fa_threshold : float, default 0.3
        Quality control lower threshold on the fractional anisotropy (FA).
    upper_fa_threshold : float, default 0.75
        Quality control upper threshold on the fractional anisotropy (FA).
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    group_stats_file : File
        A TSV file containing summary informations on fiber bunbles and
        displacements.
    """
    group_stats_file = output_dir / "group_stats.tsv"

    if not dryrun:

        stats_files = glob.glob(
            output_dir.parent / "subjects" / "*" / "*" / "STATS" / "stats.csv"
        )

        stats = []
        for path in stats_files:
            subject, session = path.split(os.sep)[-4: -2]
            df = pd.read_csv(path, index_col=0, header=None).T
            df.insert(0, "participant_id", subject)
            df.insert(1, "session", session)
            stats.append(df)
        df = pd.concat(stats)
        df.sort_values(by=["participant_id"], inplace=True)

        df["qc"] = True
        for fa_bundle in bundles:
            df["qc"] &= not (df[fa_bundle] > upper_fa_threshold)
            df["qc"] &= not (df[fa_bundle] < lower_fa_threshold)
        df["qc"] = df["qc"].astype(int)
        df.to_csv(
            group_stats_file,
            index=False,
            sep="\t",
        )

    return (group_stats_file, )
