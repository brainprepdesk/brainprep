##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
TractSeg functions.
"""

from ..decorators import (
    CoerceparamsHook,
    CommandLineWrapperHook,
    LogRuntimeHook,
    OutputdirHook,
    SignatureHook,
    step,
)
from ..typing import (
    Directory,
    File,
)


@step(
    hooks=[
        CoerceparamsHook(),
        OutputdirHook(),
        LogRuntimeHook(
            bunched=False
        ),
        CommandLineWrapperHook(),
        SignatureHook(),
    ]
)
def tractseg_parcellation(
        fod_file: File,
        mrtrix_warp_file: File,
        scalar_map_files: list[File],
        scalar_map_names: list[str],
        workspace_dir: Directory,
        output_dir: Directory,
        entities: dict) -> tuple[list[list[str]], tuple[File]]:
    """
    White matter (WM) parcellation.

    White-matter bundle segmentation was performed using TractSeg, a
    deep-learning-based framework that directly predicts tract-specific
    segmentations, orientations, and tractograms from diffusion-derived
    fiber-orientation peaks. This approach enables fast and anatomically
    consistent delineation of major white-matter pathways without requiring
    whole-brain tractography or atlas registration.

    Parameters
    ----------
    fod_file : File
        Path to the fiber orientation distributions (FOD) file of one subject.
    mrtrix_warp_file : File
        T1 to MNI MrTrix warp file.
    scalar_map_files : list[File]
        Scalar maps (i.e., FA, MD, ...) used to derive tractometry data.
    scalar_map_names : list[str]
        Names associated to scalar maps.
    workspace_dir: Directory
        Working directory with the workspace of the current processing.
    output_dir : Directory
        Directory where the reoriented image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.

    Returns
    -------
    command : list[list[str]]
        Parcellation computation command-lines.
    outputs : tuple[File]
        - tractometry_files : list[File] - Generated tractometry data
        for each input scalar map.
    """
    subject, session = entities["sub"], entities["ses"]
    basename = f"sub-{subject}_ses-{session}_desc-tractseg"

    output_dir1_ = output_dir / "tractometry"
    output_dir1_.mkdir(parents=True, exist_ok=True)
    output_dir2_ = output_dir / "bundles"
    output_dir2_.mkdir(parents=True, exist_ok=True)

    commands = [
        [
            "mrtransform",
            str(fod_file),
            "-warp",
            str(mrtrix_warp_file),
            str(workspace_dir / "FOD_WM_MNI.mif"),
            "-reorient_fod", "yes",
            "-force",
        ],
        [
            "sh2peaks",
            str(workspace_dir / "FOD_WM_MNI.mif"),
            str(workspace_dir / "peaks_MNI.mif"),
            "-num", "3",
            "-force",
        ],
        [
            "mrconvert",
            str(workspace_dir / "peaks_MNI.mif"),
            str(workspace_dir / "peaks_MNI.nii.gz"),
            "-force",
        ],
        *[
            [
                "TractSeg",
                "-i", str(workspace_dir / "peaks_MNI.nii.gz"),
                "-o", str(workspace_dir / "tractseg"),
                "--output_type", dtype
            ]
            for dtype in ("tract_segmentation", "endings_segmentation", "TOM")
        ],
        [
            "TractSeg",
            "-i", str(workspace_dir / "peaks_MNI.nii.gz"),
            "-o", str(workspace_dir / "tractseg"),
            "--output_type", "tract_segmentation",
            "--uncertainty",
        ],
        [
            "Tracking",
            "-i", str(workspace_dir / "peaks_MNI.nii.gz"),
            "-o", str(workspace_dir / "tractseg"),
            "--nr_fibers", "5000",
        ],
        *[
            [
                "Tractometry",
                "-i", str(workspace_dir / "tractseg" / "TOM_trackings"),
                "-o", str(output_dir1_ / f"{basename}_{name}.csv"),
                "-e", str(workspace_dir / "tractseg" /
                          "endings_segmentations"),
                "-s", str(in_file),
            ]
            for in_file, name in zip(
                scalar_map_files, scalar_map_names, strict=True
            )
        ],
        [
            "find",
            str(workspace_dir / "tractseg" / "bundle_segmentations"),
            "-maxdepth", "1",
            "-type", "f",
            "-name", "*.nii.gz",
            "-exec",
            "sh",
            "-c",
            f'cp "$1" "{output_dir2_}/{basename}_$(basename "$1")"',
            "_",
            "{}",
            ";",
        ],
        [
            "find",
            str(workspace_dir / "tractseg" / "bundle_uncertainties"),
            "-maxdepth", "1",
            "-type", "f",
            "-name", "*.nii.gz",
            "-exec",
            "sh",
            "-c",
            (f'cp "$1" "{output_dir2_}/{basename}_rec-uncertainty_"'
             f'"$(basename "$1")"'),
            "_",
            "{}",
            ";",
        ],
    ]

    return commands, [
        [
            output_dir1_ / f"{basename}_{name}.csv"
            for name in scalar_map_names
        ],
    ]
