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
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

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


@log_runtime(
    bunched=False)
@cmdwrapper
@outputdir
@coerceparams
def cat12vbm(
        t1_files: list[File],
        batch_file: File,
        output_dir: Directory,
        entities: list[dict]) -> tuple[list[str], tuple[list[File]]]:
    """
    Compute VBM prep-processing using CAT12.

    Parameters
    ----------
    t1_files: list[File]
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
    gm_files : list[File]
       Path to the modulated, normalized gray matter segmentations of the
        input T1-weighted MRI images.
    qc_files : list[File]
        Visual reports.
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
        for im_file, trg_dir in zip(t1_files, output_dirs)
    ]
    qc_files = [
        trg_dir / "report" / f"catreport_{im_file.name.replace('.gz', '')}"
        for im_file, trg_dir in zip(t1_files, output_dirs)
    ]

    command = [
        str(cat12_file),
        "-s", str(spm12_dir),
        "-m", str(matlab_dir),
        "-b", str(batch_file)
    ]

    return command, (gm_files, qc_files)


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
@coerceparams
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
    model_long : int, default 1
        Longitudinal model choice:1  short time (weeks), 2 long time (years)
        between images sessions.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

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
    else:
        batch_file = (
            output_dir /
            f"ses-{entities[0]['ses']}" /
            "cat12vbm_matlabbatch.m"
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
        for im_file, trg_dir in zip(t1_files, output_dirs)
    ]

    for src_file, trg_file in zip(t1_files, unzip_t1_files):
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


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
@coerceparams
def cat12vbm_morphometry(
        output_dir: Directory,
        dryrun: bool = False) -> tuple[File]:
    """
    Parse the CAT12 VBM XML ROI stats for all subjects.

    Parameters
    ----------
    output_dir : Directory
        Working directory containing the outputs.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    morphometry_files : list[File]
        A TSV file containing ROI-based GM, WM and CSF features for different
        atlases.
    """
    iterparse = {
        "neuromorphometrics": ["Vgm", "Vcsf", "Vwm"],
        "suit": ["Vgm", "Vwm"],
        "thalamic_nuclei": ["Vgm"],
        "thalamus": ["Vgm"],
    }
    morphometry_files = [
        output_dir / f"{key}_cat12_vbm_roi.tsv"
        for key in iterparse
    ]

    if not dryrun:

        xml_files = glob.glob(
            output_dir.prent / "subjects" / "sub-*" / "ses-*" / "label" /
            "catROI_*T1w.xml"
        )
        entities = [
            parse_bids_keys(path)
            for path in xml_files
        ]

        for name, output_file in zip(iterparse, morphometry_files):
            data = []
            for info, path in zip(entities, xml_files):
                tree = ET.parse(path)
                root = tree.find(name)
                ids = root.findtext("ids").strip("[]").split(";")
                names = [
                    item.text
                    for item in root.find("names").findall("item")
                ]
                features = []
                for dtype in iterparse[name]:
                    values = (
                        root.findtext(f"data/{dtype}").strip("[]").split(";")
                    )
                    df = pd.DataFrame({
                        "ID": [int(val) for val in ids],
                        "Name": names,
                        dtype: [float(val) for val in values]
                    }).T
                    df.columns = [f"{dtype}_{col}" for col in df.loc["Name"]]
                    df = df[2:]
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


@log_runtime(
    bunched=False)
@pywrapper
@outputdir
@coerceparams
def cat12vbm_stats(
        output_dir: Directory,
        ncr_threshold: int = 4.5,
        iqr_threshold: int = 4.5,
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
    ncr_threshold : float, default 4.5
         Quality control threshold on the NCR scores.
    iqr_threshold : float, default 4.5
         Quality control threshold on the IQR scores.
    dryrun : bool, default False
        If True, skip actual computation and file writing.

    Returns
    -------
    group_stats_file : File
        A TSV file containing quality metrics.
    """
    group_stats_file = output_dir / "group_stats.tsv"

    if not dryrun:

        report_files = glob.glob(
            output_dir.parent / "subjects" / "sub-*" / "ses-*" / "report" /
            "cat_*T1w.xml"
        )
        entities = [
            parse_bids_keys(path)
            for path in report_files
        ]

        stats = []
        for info, path in zip(entities, report_files):
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
