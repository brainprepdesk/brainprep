##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Brain imaging defacing.
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
    process="defacing",
    bids_file="t1_file",
    add_subjects=True,
    container="neurospin/brainprep-deface")
@log_runtime(
    title="Subject Level Defacing")
@save_runtime
def brainprep_defacing(
        t1_file: File,
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Defacing pre-processing workflow for anatomical T1-weighted images.

    Applies FSL's `fsl_deface` tool :footcite:p:`almagro2018deface` with
    default settings to remove facial features (face and ears) from the input
    image. This includes:

    1) Reorient the T1w image to standard MNI152 template space.
    2) Deface the T1w image.
    3) Generate a mosaic image of the defaced T1w image.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w anatomical image file.
    output_dir : Directory
        Directory where the defaced image and related outputs will be saved
        (i.e., the root of your dataset).
    keep_intermediate : bool
        If True, retains intermediate results (e.g., reoriented image); useful
        for debugging. Default False.

    Returns
    -------
    Bunch
        A dictionary-like object containing:

        - deface_t1_file : File — path to the defaced image.
        - mask_file : File — path to the defacing mask.
        - snap_files : list[File] — paths to defacing snapshots.

    Raises
    ------
    ValueError
        If the T1w file do not follow BIDS convension.

    Notes
    -----
    This workflow assumes the input image is a valid T1-weighted anatomical
    scan.

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from brainprep.reporting import RSTReport
    >>> from brainprep.workflow import brainprep_defacing
    >>>
    >>> with Config(dryrun=True, verbose=False):
    ...     report = RSTReport()
    ...     outputs = brainprep_defacing(
    ...         t1_file=(
    ...             "/tmp/dataset/rawdata/sub-01/ses-01/anat/"
    ...             "sub-01_ses-01_run-01_T1w.nii.gz"
    ...         ),
    ...         output_dir="/tmp/dataset/derivatives",
    ...     )
    >>> outputs
    Bunch(
      deface_t1_file: PosixPath('...')
      mask_file: PosixPath('...')
      vol_files: [PosixPath('...'), PosixPath('...')]
      mosaic_file: PosixPath('...')
    )


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

    reoriented_t1_file = interfaces.reorient(
        t1_file,
        workspace_dir,
        entities,
    )
    deface_t1_file, mask_file, vol_files = interfaces.deface(
        reoriented_t1_file,
        output_dir,
        entities,
    )
    mosaic_file = interfaces.plot_defacing_mosaic(
        mask_file,
        t1_file,
        output_dir,
        entities,
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        deface_t1_file=deface_t1_file,
        mask_file=mask_file,
        vol_files=vol_files,
        mosaic_file=mosaic_file,
    )
