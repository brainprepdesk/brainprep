##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
GeoLab functions.
"""

import os

from ..config import (
    DEFAULT_OPTIONS,
    brainprep_options,
)
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
from ..utils import (
    print_warn,
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
def geolab_parcellation(
        tractogram_file: File,
        affine_file: File,
        invwarp_file: File,
        workspace_dir: Directory,
        output_dir: Directory,
        entities: dict) -> tuple[list[list[str]], tuple[File]]:
    """
    Superficial white matter (SWM) parcellation.

    Superficial white matter (SWM) parcellation was performed using GeoLab,
    a geometry-based tractography parcellation framework that segments
    hundreds of short-range bundles by combining streamline-geometry features
    with atlas-based registration.

    Parameters
    ----------
    tractogram_file : File
        Path to the tractogram file of one subject.
    affine_file : File
        Path to the MNI template to T1 affine transform.
    invwarp_file : File
        Path to the T1 to MNI template warp.
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
        - mrtrix_warp_file : File - T1 to template MrTrix warp file.
        - labels_file : File - Text file containing atlas tractogram labels.
        - qc_file : File - TSV file containing the template overlap scores.
    """
    opts = brainprep_options.get()
    mni_2iso_file = opts.get(
        "mni_2iso_file", DEFAULT_OPTIONS["mni_2iso_file"]
    )
    atlas_dir = opts.get(
        "geolab_atlas_dir", DEFAULT_OPTIONS["geolab_atlas_dir"]
    )
    subject, session = entities["sub"], entities["ses"]
    basename = f"sub-{subject}_ses-{session}_desc-geolab"
    names = [
        "comparisonWithAtlas.tsv",
        "labels.dict",
        "labels.txt",
        "labelsSBR.dict",
        "labelsSBR.txt",
        "regroupedRecognized.tck",
    ]
    output_dir_ = output_dir / "labels"
    output_dir_.mkdir(parents=True, exist_ok=True)

    mrtrix_warp_file = (
        output_dir /
        "anat" /
        "transforms" /
        "t1_to_template_mrtrix_warp_corrected.mif"
    )
    mrtrix_warp_file.parent.mkdir(parents=True, exist_ok=True)

    commands = [
        [
            "warpinit",
            str(mni_2iso_file),
            str(workspace_dir / "identity_warp[].nii"),
            "-force",
        ],
        *[
            [
                "WarpImageMultiTransform",
                "3",
                str(workspace_dir / f"identity_warp{idx}.nii"),
                str(workspace_dir / f"mrtrix_warp{idx}.nii"),
                "-R", str(mni_2iso_file),
                "-i", str(invwarp_file),
                str(invwarp_file),
            ]
            for idx in range(3)
        ],
        [
            "warpcorrect",
            str(workspace_dir / "mrtrix_warp[].nii"),
            str(mrtrix_warp_file),
            "-force",
        ],
        [
            "tcktransform",
            str(tractogram_file),
            str(mrtrix_warp_file),
            str(workspace_dir / "tractogram_MNI.tck"),
            "-force",
        ],
        [
            "tckresample",
            str(workspace_dir / "tractogram_MNI.tck"),
            str(workspace_dir / "tractogram_15pts_MNI.tck"),
            "-num_points", "15",
            "-force",
        ],
    ]

    if not atlas_dir.is_dir():
        print_warn(f"no atlas directory: {atlas_dir}")
        return commands, [mrtrix_warp_file, None, None]
    atlas_names = os.listdir(atlas_dir)

    commands.extend([
        *[
            [
                "ProjectAtlasGeoLab",
                "-i", str(workspace_dir / "tractogram_15pts_MNI.tck"),
                "-o", str(workspace_dir / atlas_name),
                "-a", str(atlas_dir / atlas_name / "bundles"),
                "-an", str(atlas_dir / atlas_name / "neighbors"),
                "-anc", str(atlas_dir / atlas_name / "centroids"),
                "-nbPoints", "15",
                "-nbThreads", "10",
                "-sp", "false",
            ]
            for atlas_name in atlas_names
        ],
        *[
            [
                "cp",
                str(workspace_dir / atlas_name / name),
                str(output_dir_ / f"{basename}_rec-{atlas_name}_{name}"),
            ]
            for atlas_name in atlas_names
            for name in names
        ],
    ])

    return commands, [
        mrtrix_warp_file,
        [
            output_dir_ / f"{basename}_rec-{atlas_name}_labels.txt"
            for atlas_name in atlas_names
        ],
        [
            (
                output_dir_ /
                f"{basename}_rec-{atlas_name}_comparisonWithAtlas.tsv"
            )
            for atlas_name in atlas_names
        ],
    ]
