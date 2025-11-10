##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Functional MRI PreProcessing
"""

import itertools
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
    process="fmriprep",
    bids_file="t1_file",
    add_subjects=True,
    container="neurospin/brainprep-fmriprep")
@log_runtime(
    title="Subject Level fMRI PreProcessing")
@save_runtime
@coerceparams
def brainprep_fmriprep(
        t1_file: File,
        func_files: list[File],
        dataset_description_file: File,
        freesurfer_dir: Directory,
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Subject level functional MRI pre-processing.

    Applies fmriprep tool :footcite:p:`esteban2019fmriprep` with the following
    setting:

    1) T1-weighted volume was corrected for INU (intensity non-uniformity)
       using N4BiasFieldCorrection and skull-stripped using
       antsBrainExtraction.sh (using the OASIS template).
    2) Brain mask estimated previously was refined with a custom variation of
       the method to reconcile ANTs-derived and FreeSurfer-derived
       segmentations of the cortical gray-matter of Mindboggle.
    3) Spatial normalization to the ICBM 152 Nonlinear Asymmetrical template
       version 2009c was performed through nonlinear registration with the
       antsRegistration tool of ANTs, using brain-extracted versions of both
       T1w volume and template.
    4) Brain tissue segmentation of cerebrospinal fluid (CSF), white-matter
       (WM) and gray-matter (GM) was performed on the brain-extracted T1w
       using FSL fast.
    5) Functional data was motion corrected using FSL mcflirt.
    6) This was followed by co-registration to the corresponding T1w using
       boundary-based registration with six degrees of freedom, using
       FreeSurfer bbregister.
    7) Motion correcting transformations, BOLD-to-T1w transformation and
       T1w-to-template (MNI) warp were concatenated and applied in a single
       step using ANTs antsApplyTransforms using Lanczos interpolation.
    8) Physiological noise regressors were extracted applying CompCor.
       Principal components were estimated for the two CompCor variants:
       temporal (tCompCor) and anatomical (aCompCor).A mask to exclude signal
       with cortical origin was obtained by eroding the brain mask, ensuring
       it only contained subcortical structures. Six tCompCor components were
       then calculated including only the top 5% variable voxels within that
       subcortical mask. For aCompCor, six components were calculated within
       the intersection of the subcortical mask and the union of CSF and WM
       masks calculated in T1w space, after their projection to the native
       space of each functional run.
    9) Frame-wise displacement was calculated for each functional run using
       Nipype.

    Then, compute functional ROI-based functional connectivity from
    pre-processed volumetric fMRI data based on the Schaefer 200 ROI atlas.
    Connectivity is computed using Pearson correlation.

    Parameters
    ----------
    t1_file : File
        Path to the input T1w image file.
    func_files : list[File]
        Path to the input functional image files of one subject.
    dataset_description_file : File
        Path to the BIDS dataset description file.
    freesurfer_dir : Directory
        Path to an existing FreeSurfer subjects directory where the reconall
        command has already been performed.
    output_dir : Directory
        Directory where the prep-processing related outputs will be saved
        (i.e., the root of your dataset).
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - fmri_rest_image_files: list[File] - pre-processed rfMRI NIFTI
          volumes: 2mm MNI152NLin6Asym and MNI152NLin2009cAsym.
        - fmri_rest_surf_files: File - pre-processed rfMRI CIFTI surfaces:
          fsLR23k.
        - qc_file: File - the HTML visual report for the subject's data.
        - connectivity_files: list[File] - TSV files containing the ROI-to-ROI
          connectivity matrix for each resting-state fMRI pre-processed
          image.

    Notes
    -----
    This workflow assumes the T1w image is organized in BIDS.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_fmriprep
    >>> brainprep_fmriprep(t1_file, func_files, dataset_description_file,
    ...                    freesurfer_dir, output_dir)

    Raises
    ------
    ValueError
        If the input T1w file is not BIDS-compliant.

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

    rfmri_outputs, qc_file = interfaces.fmriprep(
        t1_file,
        func_files,
        dataset_description_file,
        freesurfer_dir,
        workspace_dir,
        output_dir,
        entities,
    )
    fmri_rest_image_files = list(itertools.chain.from_iterable(
        [item[1] for item in rfmri_outputs]
    ))
    fmri_rest_surf_files = [item[2] for item in rfmri_outputs]

    connectivity_files = []
    for fmri_data in rfmri_outputs:
        counfounds_file = fmri_data[3]
        for mask_file, fmri_rest_image_files in zip(
                fmri_data[0], fmri_data[1]):
            for fmri_rest_image_file in fmri_rest_image_files:
                entities = parse_bids_keys(fmri_rest_image_file)
                connectivity_files.append(
                    interfaces.func_vol_connectivity(
                        fmri_rest_image_file,
                        mask_file,
                        counfounds_file,
                        output_dir,
                        entities,
                        fwhm=0.,
                    )
                )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        fmri_rest_image_files=fmri_rest_image_files,
        fmri_rest_surf_files=fmri_rest_surf_files,
        qc_file=qc_file,
        connectivity_files=connectivity_files,
    )
