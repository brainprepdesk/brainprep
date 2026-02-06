##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


"""
CAT12 functions.
"""

import glob
from pathlib import Path

import pandas as pd
from scipy.io import loadmat

from ..config import (
    DEFAULT_OPTIONS,
    brainprep_options,
)
from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    coerce_to_path,
    outputdir,
    parse_bids_keys,
)
from ..wrappers import (
    cmdwrapper,
    pywrapper,
)
from .utils import (
    ungzfile,
)


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@cmdwrapper
def cat12vbm_wf(
        t1_files: list[File],
        batch_file: File,
        output_dir: Directory,
        entities: list[dict]) -> tuple[list[str], tuple[File | list[File]]]:
    """
    Compute VBM prep-processing using CAT12.

    Parameters
    ----------
    t1_files : list[File]
        Path to the T1 files.
    batch_file : File
        Path to the ready for execution CAT12 batch file
    output_dir : Directory
        Directory where the prep-processing related outputs will be saved.
    entities : list[dict]
        Dictionaries of parsed BIDS entities including modality for each input
        image file.

    Returns
    -------
    command : list[str]
       Pre-processing command-line.
    outputs : tuple[File | list[File]]
        - gm_files : list[File] - Path to the modulated, normalized gray
          matter segmentations of the input T1-weighted MRI images.
        - qc_files : list[File] - Visual reports.
    """
    opts = brainprep_options.get()
    cat12_file = opts.get("cat12_file", DEFAULT_OPTIONS["cat12_file"])
    spm12_dir = opts.get("spm12_dir", DEFAULT_OPTIONS["spm12_dir"])
    matlab_dir = opts.get("matlab_dir", DEFAULT_OPTIONS["matlab_dir"])

    output_dirs = [
        output_dir / f"ses-{info['ses']}"
        for info in entities
    ]
    gm_files = [
        trg_dir / "mri" / f"mwp1{im_file.name.replace('.gz', '')}"
        for im_file, trg_dir in zip(t1_files, output_dirs, strict=True)
    ]
    qc_files = [
        trg_dir / "report" / f"catreport_{im_file.name.replace('.gz', '')}"
        for im_file, trg_dir in zip(t1_files, output_dirs, strict=True)
    ]

    command = [
        str(cat12_file),
        "-s", str(spm12_dir),
        "-m", str(matlab_dir),
        "-b", str(batch_file)
    ]

    return command, (gm_files, qc_files)


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def write_catbatch(
        t1_files: list[File],
        output_dir: Directory,
        entities: list[dict],
        model_long: int = 1,
        dryrun: bool = False) -> tuple[File]:
    """
    Generate CAT12 batch file.

    Parameters
    ----------
    t1_files: list[File]
        Path to the T1 files.
    output_dir : Directory
        Working directory containing the outputs.
    entities : list[dict]
        Dictionaries of parsed BIDS entities including modality for each input
        image file.
    model_long : int
        Longitudinal model choice:1  short time (weeks), 2 long time (years)
        between images sessions. Default 1.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    batch_file : File
        Path to the ready for execution CAT12 batch file.

    Notes
    -----
    - Input T1w image files are unzip in workspace folder.
    """
    opts = brainprep_options.get()
    tpm_file = opts.get("tpm_file", DEFAULT_OPTIONS["tpm_file"])
    darteltpm_file = opts.get(
        "darteltpm_file", DEFAULT_OPTIONS["darteltpm_file"]
    )

    assert len(t1_files) == len(entities)
    longitudinal = len(t1_files) != 1
    if longitudinal:
        batch_file = (
            output_dir /
            "cat12vbm_matlabbatch.m"
        )
        template_batch = (
            Path(__file__).parent.parent /
            "resources" /
            "cat12vbm_matlabbatch_longitudinal.m"
        )
    else:
        unique_id = '_'.join(
            ['-'.join([key,value]) for key,value in entities[0].items()
             if key not in ['sub','ses','mod','modality']]
        )
        batch_file = (
            output_dir /
            f"ses-{entities[0]['ses']}" /
            f"cat12vbm_matlabbatch_{unique_id}.m"
        )
        template_batch = (
            Path(__file__).parent.parent /
            "resources" /
            "cat12vbm_matlabbatch.m"
        )
    output_dirs = [
        output_dir / f"ses-{info['ses']}"
        for info in entities
    ]
    unzip_t1_files = [
        trg_dir / im_file.name.replace(".gz", "")
        for im_file, trg_dir in zip(t1_files, output_dirs, strict=True)
    ]

    for src_file, trg_file in zip(t1_files, unzip_t1_files, strict=True):
        ungzfile(
            src_file,
            trg_file,
            trg_file.parent,
        )

    content = template_batch.read_text()
    content = content.format(
        model_long=model_long,
        anat_file=(
            " \n".join([
                f"'{path}'" for path in unzip_t1_files
            ])
        ),
        tpm_file=str(tpm_file),
        darteltpm_file=str(darteltpm_file),
    )
    batch_file.write_text(content)

    return (batch_file, )


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def cat12vbm_morphometry(
        output_dir: Directory,
        dryrun: bool = False) -> list[File]:
    """
    Parse the CAT12 VBM XML ROI stats for all subjects.

    Parameters
    ----------
    output_dir : Directory
        Working directory containing the outputs.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    morphometry_files : list[File]
        TSV files containing ROI-based GM, WM and CSF features for different
        atlases.
    """
    atlases = {
        "Schaefer2018_100Parcels_17Networks_order": ["Vgm", "Vwm"],
        "Schaefer2018_200Parcels_17Networks_order": ["Vgm", "Vwm"],
        "Schaefer2018_400Parcels_17Networks_order": ["Vgm", "Vwm"],
        "Schaefer2018_600Parcels_17Networks_order": ["Vgm", "Vwm"],
        "aal3": ["Vgm"],
        "cobra": ["Vgm", "Vwm"],
        "hammers": ["Vgm", "Vwm", "Vcsf"],
        "ibsr": ["Vgm", "Vwm", "Vcsf"],
        "julichbrain": ["Vgm", "Vwm"],
        "lpba40": ["Vgm", "Vwm"],
        "mori": ["Vgm", "Vwm"],
        "neuromorphometrics": ["Vgm", "Vwm", "Vcsf"],
        "suit": ["Vgm", "Vwm"],
        "thalamic_nuclei": ["Vgm"],
        "thalamus": ["Vgm"],
    }
    morphometry_files = [
        output_dir / f"{atlas}_cat12_vbm_roi.tsv"
        for atlas in atlases
    ]

    if not dryrun:

        mat_files = coerce_to_path(
            glob.glob(
                str(output_dir.parent / "subjects" / "sub-*" / "ses-*" / "label" /
                    "catROI_*T1w.mat")
            ),
            expected_type=list[File]
        )
        entities = [
            parse_bids_keys(path)
            for path in mat_files
        ]
        for atlas, output_file in zip(
                atlases, morphometry_files, strict=True):
            data = []
            for info, path in zip(entities, mat_files, strict=True):
                _data = loadmat(path, simplify_cells=True)
                ids = _data["S"][atlas]["ids"]
                names = _data["S"][atlas]["names"]
                features = []
                for brain_tissue in atlases[atlas]:
                    values = _data["S"][atlas]["data"][brain_tissue]
                    df = pd.DataFrame({
                        "ID": [int(val) for val in ids],
                        "Name": names,
                        brain_tissue: [float(val) for val in values]
                    }).T
                    df.columns = [f"{brain_tissue}_{col}" for col in df.loc["Name"]]
                    df = df[2:]
                    df = df.reset_index(drop=True)
                    features.append(df)
                df = pd.concat(features, axis=1)
                df.insert(0, "participant_id", info["sub"])
                df.insert(1, "session", info["ses"])
                df.insert(2, "run", info["run"])
                data.append(df)
            df = pd.concat(data)
            df.sort_values(by=["participant_id"], inplace=True)
            df.to_csv(
                output_file,
                index=False,
                sep="\t",
            )

    return (morphometry_files, )


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def cat12vbm_stats(
        output_dir: Directory,
        ncr_threshold: float = 4.5,
        iqr_threshold: float = 4.5,
        dryrun: bool = False) -> tuple[File]:
    """
    Parse the CAT12 VBM report stats for all subjects and applies a
    quality control.

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
        Working directory containing the outputs.
    ncr_threshold : float
         Quality control threshold on the NCR scores. Default 4.5.
    iqr_threshold : float
         Quality control threshold on the IQR scores. Default 4.5.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    group_stats_file : File
        A TSV file containing quality metrics.
    """
    group_stats_file = output_dir / "group_stats.tsv"

    if not dryrun:

        report_files = coerce_to_path(
            glob.glob(
                str(output_dir.parent / "subjects" / "sub-*" / "ses-*" / "report" /
                "cat_*T1w.xml")
            ),
            expected_type=list[File]
        )
        entities = [
            parse_bids_keys(path)
            for path in report_files
        ]

        stats = []
        for info, path in zip(entities, report_files, strict=True):
            df = pd.read_xml(
                path,
                iterparse={"qualityratings": ["ICR", "NCR", "IQR"]},
            )
            df.insert(0, "participant_id", info["sub"])
            df.insert(1, "session", info["ses"])
            df.insert(2, "run", info["run"])
            stats.append(df)
        df = pd.concat(stats)
        df.sort_values(by=["participant_id"], inplace=True)

        df["qc"] = (
            (df["NCR"] < ncr_threshold) &
            (df["IQR"] < iqr_threshold)
        ).astype(int)

        df.to_csv(
            group_stats_file,
            index=False,
            sep="\t",
        )

    return (group_stats_file, )
