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

import os
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


@bids(
    process="quality_assurance",
    bids_file="image_files",
    container="neurospin/brainprep-qa")
@log_runtime(
    title="Subject Level Quality Assurance")
@save_runtime
@coerceparams
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
    >>> from brainprep.workflow import brainprep_quality_assurance
    >>> brainprep_quality_assurance([t1_file, dwi_file], output_dir)

    References
    ----------

    .. footbibliography::
    """
    workspace_dir, iqm_files = interfaces.subject_level_qa(
        image_files,
        output_dir,
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        iqm_files=iqm_files,
    )


@bids(
    process="quality_assurance")
@log_runtime(
    title="Group Level Quality Assurance")
@save_runtime
@coerceparams
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
    >>> from brainprep.workflow import brainprep_group_quality_assurance
    >>> brainprep_group_quality_assurance(output_dir)

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
