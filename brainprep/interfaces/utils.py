##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Utils functions.
"""

import getpass
import gzip
import shutil
import socket
from collections import OrderedDict

import nibabel
import numpy as np
import pandas as pd

from ..decorators import (
    CoerceparamsHook,
    CommandLineWrapperHook,
    LogRuntimeHook,
    OutputdirHook,
    PythonWrapperHook,
    SignatureHook,
    step,
)
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    make_run_id,
)


@step(
    hooks=[
        CoerceparamsHook(),
        OutputdirHook(),
        LogRuntimeHook(
            bunched=False
        ),
        PythonWrapperHook(),
        SignatureHook(),
    ]
)
def maskdiff(
        mask1_file: File,
        mask2_file: File,
        output_dir: Directory,
        entities: dict,
        inv_mask1: bool = False,
        inv_mask2: bool = False,
        dryrun: bool = False) -> tuple[File]:
    """
    Compute summary statistics comparing two binary masks.

    This function loads two binary mask images, verifies that they share
    the same spatial dimensions and affine transformation, computes their
    voxel-wise intersection, and writes a summary table containing voxel
    counts and physical volumes (in mm³) for each mask and their intersection.

    Parameters
    ----------
    mask1_file : File
        Path to the first binary mask image.
    mask2_file : File
        Path to the second binary mask image.
    output_dir : Directory
        Directory where the defacing mask will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    inv_mask1 : bool
        If True, the first mask is inverted before comparison. This is
        useful when the mask represents an exclusion region rather than an
        inclusion region. Default False.
    inv_mask2 : bool
        If True, the second mask is inverted before comparison. This is
        useful when the mask represents an exclusion region rather than an
        inclusion region. Default False.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    summary_file : File
        Path to the generated summary TSV file.

    Raises
    ------
    ValueError
        If both masks have not identical shapes and affines.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_defacemask".format(
        **entities)
    summary_file = output_dir / f"{basename}.tsv"

    if not dryrun:

        mask1_im = nibabel.load(mask1_file)
        mask2_im = nibabel.load(mask2_file)
        mask1 = mask1_im.get_fdata().astype(bool)
        mask2 = mask2_im.get_fdata().astype(bool)

        if inv_mask1:
            mask1 = ~mask1
        if inv_mask2:
            mask1 = ~mask2

        if mask1.shape != mask2.shape:
            raise ValueError(
                f"Mask shapes differ: {mask1.shape} vs {mask2.shape}. "
                "Resampling is required."
            )
        if not np.allclose(mask1_im.affine, mask2_im.affine):
            raise ValueError(
                "Mask affines differ. Resampling is required before "
                "intersection."
            )

        intersection = np.logical_and(mask1, mask2)
        voxel_volume = np.abs(np.linalg.det(mask1_im.affine[:3, :3]))

        summary_df = pd.DataFrame({
            "mask": ["mask1", "mask2", "intersection"],
            "voxels": [
                mask1.sum(),
                mask2.sum(),
                intersection.sum(),
            ],
            "volume_mm3": [
                mask1.sum() * voxel_volume,
                mask2.sum() * voxel_volume,
                intersection.sum() * voxel_volume,
            ]
        })
        summary_df.to_csv(summary_file, sep="\t", index=False)

    return (summary_file, )


@step(
    hooks=[
        CoerceparamsHook(),
        OutputdirHook(),
        LogRuntimeHook(
            bunched=False
        ),
        PythonWrapperHook(),
        SignatureHook(),
    ]
)
def copyfiles(
        source_image_files: list[File],
        destination_image_files: list[File],
        output_dir: Directory,
        dryrun: bool = False) -> None:
    """
    Copy input image files.

    Parameters
    ----------
    source_image_files : list[File]
        Path to the image to be copied.
    destination_image_files : list[File]
        Path to the locations where images will be copied.
    output_dir : Directory
        Directory where the images are copied.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.
    """
    if not dryrun:
        for src_path, dest_path in zip(source_image_files,
                                       destination_image_files,
                                       strict=True):
            shutil.copy(src_path, dest_path)


@step(
    hooks=[
        CoerceparamsHook(),
        OutputdirHook(),
        LogRuntimeHook(
            bunched=False
        ),
        PythonWrapperHook(),
        SignatureHook(),
    ]
)
def movedir(
        source_dir: Directory,
        output_dir: Directory,
        content: bool = False,
        dryrun: bool = False) -> tuple[Directory]:
    """
    Move input directory.

    Parameters
    ----------
    source_dir : Directory
        Path to the directory to be moved.
    output_dir : Directory
        Directory where the folder is moved.
    content : bool
        If True, move the content of the source directory. Default False.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    target_directory : Directory
        Path to the moved directory.

    Raises
    ------
    ValueError
        If `source_dir` is not a directory.
    """
    if not dryrun:
        if not source_dir.is_dir():
            raise ValueError(
                f"Source '{source_dir}' is not a directory."
            )
        if not content:
            shutil.move(source_dir, output_dir / source_dir.name)
        else:
            for item in source_dir.iterdir():
                target = output_dir / item.name
                shutil.move(item, output_dir / item.name)
            if not any(source_dir.iterdir()):
                source_dir.rmdir()
    return (output_dir if content else output_dir / source_dir.name, )


@step(
    hooks=[
        CoerceparamsHook(),
        LogRuntimeHook(
            bunched=False
        ),
        PythonWrapperHook(),
        SignatureHook(),
    ]
)
def ungzfile(
        input_file: File,
        output_file: File,
        output_dir: Directory,
        dryrun: bool = False) -> tuple[File]:
    """
    Ungzip input file.

    Parameters
    ----------
    input_file : File
        Path to the file to ungzip.
    output_file : File
        Path to the ungzip file.
    output_dir : Directory
        Directory where the unzip file is created.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    output_file : File
        Path to the ungzip file.

    Raises
    ------
    ValueError
        If the input file is not compressed.
    """
    if input_file.suffix != ".gz":
        raise ValueError(
            f"The input file is not compressed: {input_file}"
        )

    if not dryrun:
        with gzip.open(input_file, "rb") as gzfobj:
            output_file.write_bytes(gzfobj.read())

    return (output_file, )


@step(
    hooks=[
        CoerceparamsHook(),
        OutputdirHook(),
        LogRuntimeHook(
            bunched=False
        ),
        SignatureHook(),
    ]
)
def write_uuid_mapping(
        input_file: File,
        output_dir: Directory,
        entities: dict,
        name: str = "uuid_mapping.tsv",
        full_path: bool = False) -> File:
    """
    Create a TSV file that records a deterministic  UUID-based mapping.

    Each row contains:
    - filename: relative path within the BIDS dataset.
    - run_default: 5-digit deterministic run ID derived from the filename.
    - uuid: full UUIDv5 for traceability.

    Parameters
    ----------
    input_file : File
        Path to the file to map.
    output_dir : Directory
        Directory where the TSV file is created.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    name : str
        Name of the TSV file to write. Default is "uuid_mapping.tsv".
    full_path: bool
        If True, extract entities from the full input path rather than
        only the filename. Default is False.

    Returns
    -------
    output_file : File
        Path to the written TSV file.
    """
    outut_file = output_dir / f"run-{entities['run']}" / name
    filename = str(input_file) if full_path else input_file.name
    code, short_code = make_run_id(filename)

    if short_code == entities["run"]:
        outut_file.parent.mkdir(parents=True, exist_ok=True)
        df = pd.DataFrame.from_dict({
            "filename": [filename],
            "run": [short_code],
            "uuid": [code],
        })
        df.to_csv(outut_file, sep="\t", index=False)
    else:
        outut_file = None

    return (outut_file, )


@step(
    hooks=[
        CoerceparamsHook(),
        LogRuntimeHook(
            bunched=False
        ),
        CommandLineWrapperHook(),
        SignatureHook(),
    ]
)
def anonfile(
        input_file: File,
        mapping: dict[str, str]) -> tuple[list[str], File]:
    """
    Anonymize a text file using sed.

    The function constructs a list of sed substitution expressions based on
    the user-provided mapping and additional system-derived identifiers
    (hostname, IP address, username). The resulting command performs
    in-place anonymization of the input file.

    Parameters
    ----------
    input_file : File
        Path to the file to anonymize.
    mapping : dict[str, str]
        Patterns to replace (keys) and their replacements (values).

    Returns
    -------
    command : list[str]
        The sed command-line used for anonization.
    output_file : File
        Path to the anonymized file.
    """
    mapping = OrderedDict(mapping)
    hostname = socket.gethostname()
    mapping.update(
        OrderedDict({
            hostname: "HOSTNAME",
            socket.gethostbyname(hostname): "X.X.X.X",
            getpass.getuser(): "USER",
        })
    )

    patterns = []
    for old, new in mapping.items():
        old_esc = old.replace("/", r"\/")
        new_esc = new.replace("/", r"\/")
        patterns.extend(["-e", f"'s/{old_esc}/{new_esc}/g'"])
    command = [
        "sed",
        *patterns,
        "-i", str(input_file)
    ]

    return command, (input_file, )
