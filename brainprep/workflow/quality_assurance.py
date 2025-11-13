##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Quality assurance.
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
    print_info,
)


@coerceparams
@bids(
    process="quality_assurance",
    bids_file="image_files",
    container="neurospin/brainprep-qa")
@log_runtime(
    title="Subject Level Quality Assurance")
@save_runtime
def brainprep_quality_assurance(
        image_files: list[File],
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Subject level quality assurance pre-processing workflow for MRI images.

    Applies MRIQC tool :footcite:p:`esteban2017mriqc` with subject level
    default settings.

    Parameters
    ----------
    image_files : list[File]
        Path to the input image files of one subject.
    output_dir : Directory
        Directory where the quality assurance related outputs will be saved
        (i.e., the root of your dataset).
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - iqm_files : list[File] — paths to the subject level Image Quality
          Metrics (IQMs).

    Notes
    -----
    This workflow assumes the input images are organized in BIDS.

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from brainprep.reporting import RSTReport
    >>> from brainprep.workflow import brainprep_quality_assurance
    >>>
    >>> with Config(dryrun=True, verbose=False):
    ...     report = RSTReport()
    ...     outputs = brainprep_quality_assurance(
    ...         image_files=[
    ...             "/tmp/dataset/rawdata/sub-01/ses-01/anat/"
    ...             "sub-01_ses-01_run-01_T1w.nii.gz",
    ...             "/tmp/dataset/rawdata/sub-01/ses-01/dwi/"
    ...             "sub-01_ses-01_run-01_dwi.nii.gz",
    ...         ],
    ...         output_dir="/tmp/dataset/derivatives",
    ...     )
    >>> outputs
    Bunch(
        iqm_files: [PosixPath('...'), PosixPath('...')]
    )

    References
    ----------

    .. footbibliography::
    """
    workspace_dir = output_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"setting workspace directory: {workspace_dir}")

    iqm_files = interfaces.subject_level_qa(
        image_files,
        workspace_dir,
        output_dir,
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        iqm_files=iqm_files,
    )


@coerceparams
@bids(
    process="quality_assurance")
@log_runtime(
    title="Group Level Quality Assurance")
@save_runtime
def brainprep_group_quality_assurance(
        modalities: list[str],
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Group lebel quality assurance pre-processing workflow for MRI images.

    Applies MRIQC tool :footcite:p:`esteban2017mriqc` with group level
    default settings.

    Parameters
    ----------
    modalities: list[str]
        The modalities in the current study.
    output_dir : Directory
        Directory where the quality assurance related outputs will be saved
        (i.e., the root of your dataset).
    keep_intermediate : bool, default False
        If True, retains intermediate results (no effect on this workflow).

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - iqm_files : list[File] — paths to the group level Image Quality
          Metrics (IQMs).

    Notes
    -----
    This workflow assumes the subject level analysis have already been.

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from brainprep.reporting import RSTReport
    >>> from brainprep.workflow import brainprep_group_quality_assurance
    >>>
    >>> with Config(dryrun=True, verbose=False):
    ...     report = RSTReport()
    ...     outputs = brainprep_group_quality_assurance(
    ...         modalities=["T1w"],
    ...         output_dir="/tmp/dataset/derivatives",
    ...     )
    >>> outputs
    Bunch(
        iqm_file: [PosixPath('...')]
    )

    References
    ----------

    .. footbibliography::
    """
    iqm_file = interfaces.group_level_qa(
        modalities,
        output_dir,
    )

    return Bunch(
        iqm_file=iqm_file,
    )
