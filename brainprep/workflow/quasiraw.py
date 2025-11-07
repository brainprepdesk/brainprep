# -*- coding: utf-8 -*-
##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2022
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Quasi-RAW pre-processing.
"""

import os
from pathlib import Path
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
    process="quasiraw",
    bids_file="anatomical_file",
    add_subjects=True,
    container="neurospin/brainprep-quasiraw")
@log_runtime(
    title="Subject Level Quasi-RAW")
@save_runtime
@coerceparams
def brainprep_quasiraw(
        anatomical_file: File,
        output_dir: Directory,
        keep_intermediate: bool = False) -> Bunch:
    """
    Quasi-RAW pre-processing.

    Applies the Quasi-RAW pre-processing described in
    :footcite:p:`dufumier2022openbhb`. This includes:

    1) Reorient the anatomical image to standard MNI152 template space.
    2) Compute a brain mask using a skull-stripping tool.
    3) Apply the brain mask to the anatomical image.
    4) Resample the anatomical image to 1mm isotropic voxel size.
    5) Resample the brain mask image to 1mm isotropic voxel size.
    6) Perform N4 bias field correction.
    7) Linearly (9 dof) register the image to the MNI152 1mm template space.
    8) Apply the registration to the antomical image.
    9) Apply the registration to the brain mask image.
    10) Apply the brain mask to the registered anatomical image.

    Parameters
    ----------
    anatomical_file: File
        Path to the input image file.
    output_dir: Directory
        Directory where the outputs will be saved (i.e., the root of your
        dataset).
    keep_intermediate : bool, default False
        If True, retains intermediate results (i.e., the workspace); useful
        for debugging.

    Returns
    -------
    Bunch
        A dictionary-like object containing:
        - aligned_anatomical_file : File - path to the aligned anatomical
          image - a Nifti file with the suffix "_T1w".
        - aligned_mask_file : File - path to the aligned mask image - a
          Nifti file with the suffix "_mod-T1w_brainmask".
        - transform_file : File - path to the 9 dof affine transformation - a
          text file with the suffix "_mod-T1w_affine".

    Notes
    -----
    This workflow assumes the anatomical image is organized in BIDS.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_quasiraw
    >>> brainprep_quasiraw(t1_file, brain_mask_file, output_dir)

    Raises
    ------
    ValueError
        If the input anatomical file is not BIDS-compliant.

    References
    ----------

    .. footbibliography::
    """
    resource_dir = Path(interfaces.__file__).parent.parent / "resources"
    template_file = resource_dir / "MNI152_T1_1mm_brain.nii.gz"
    print_info(f"setting template file: {template_file}")
    workspace_dir = output_dir / "workspace"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    print_info(f"setting workspace directory: {workspace_dir}")

    entities = parse_bids_keys(anatomical_file)
    if len(entities) == 0:
        raise ValueError(
            f"The anatomical file '{anatomical_file}' is not BIDS-compliant."
        )

    reoriented_anatomical_file = interfaces.reorient(
        anatomical_file,
        workspace_dir / "01-reorient",
        entities,
    )
    mask_file = interfaces.brainmask(
        reoriented_anatomical_file,
        workspace_dir / "02-brainmask",
        entities,
    )
    masked_anatomical_file = interfaces.applymask(
        reoriented_anatomical_file,
        mask_file,
        workspace_dir / "03-applymask",
        entities,
    )
    scaled_anatomical_file, _ = interfaces.scale(
        masked_anatomical_file,
        1,
        workspace_dir / "04-scale",
        entities,
    )
    scaled_mask_file, _ = interfaces.scale(
        mask_file,
        1,
        workspace_dir / "05-scale",
        entities,
    )
    bc_anatomical_file, _ = interfaces.biasfield(
        scaled_anatomical_file,
        scaled_mask_file,
        workspace_dir / "06-biasfield",
        entities,
    )
    _, affine_transform_file = interfaces.affine(
        bc_anatomical_file,
        template_file,
        workspace_dir / "07-affine",
        entities,
    )
    aligned_anatomical_file = interfaces.applyaffine(
        bc_anatomical_file,
        template_file,
        affine_transform_file,
        workspace_dir / "08-applyaffine",
        entities,
        interpolation="spline",
    )
    aligned_mask_file = interfaces.applyaffine(
        mask_file,
        template_file,
        affine_transform_file,
        workspace_dir / "09-applyaffine",
        entities,
        interpolation="nearestneighbour",
    )
    aligned_anatomical_file = interfaces.applymask(
        aligned_anatomical_file,
        aligned_mask_file,
        workspace_dir / "10-applymask",
        entities,
    )

    mod = entities["mod"]
    basename = "sub-{sub}_ses-{ses}_run-{run}".format(**entities)
    output_anatomical_file = output_dir / f"{basename}_{mod}.nii.gz"
    output_mask_file = output_dir / f"{basename}_mod-{mod}_brainmask.nii.gz"
    output_transform_file = output_dir / f"{basename}_mod-{mod}_affine.txt"
    interfaces.copyfiles(
        [aligned_anatomical_file, aligned_mask_file, affine_transform_file],
        [output_anatomical_file, output_mask_file, output_transform_file],
        output_dir,
    )

    if not keep_intermediate:
        print_info(f"cleaning workspace directory: {workspace_dir}")
        shutil.rmtree(workspace_dir)

    return Bunch(
        aligned_anatomical_file=output_anatomical_file,
        aligned_mask_file=output_mask_file,
        transform_file=output_transform_file,
    )


def brainprep_group_quasiraw(img_regex, outdir, brainmask_regex=None,
                             extra_img_regex=None, corr_thr=0.5):
    """
    Quasi-RAW pre-processing quality control.

    Parameters
    ----------
    img_regex: str
        regex to the quasi raw image files for all subjects.
    outdir: str
        the destination folder.
    brainmask_regex: str, default None
        regex to the brain mask files for all subjects. If one file is
        provided, we assume subjects are in the same referential.
    extra_img_regex: list of str, default None
        list of regex to extra image to diplay in quality control.
    corr_thr: float, default 0.5
        control the quality control threshold on the correlation score.
    """
    print_title("Parse data...")
    if not os.path.isdir(outdir):
        raise ValueError("Please specify a valid output directory.")
    img_files = sorted(glob.glob(img_regex))
    if brainmask_regex is None:
        brainmask_files = []
    else:
        brainmask_files = sorted(glob.glob(brainmask_regex))
    if extra_img_regex is None:
        extra_img_files = []
    else:
        extra_img_regex = listify(extra_img_regex)
        extra_img_files = [sorted(glob.glob(item)) for item in extra_img_regex]
    print("  images:", len(img_files))
    print("  brain masks:", len(brainmask_files))
    print("  extra images:", [len(item) for item in extra_img_files])
    if len(brainmask_files) > 1:
        check_files([img_files, brainmask_files])
    if len(extra_img_files) > 0:
        check_files([img_files] + extra_img_files)

    print_title("Load images...")
    imgs_arr, df = load_images(img_files)
    imgs_arr = imgs_arr.squeeze()
    imgs_size = list(imgs_arr.shape)[1:]
    if len(brainmask_files) == 1:
        mask_img = nibabel.load(brainmask_files[0])
        mask_glob = (mask_img.get_fdata() > 0)
    elif len(brainmask_files) > 1:
        if len(brainmask_files) != len(imgs_arr):
            raise ValueError("The list of images and masks must have the same "
                             "length.")
        masks_arr = [nibabel.load(path).get_fdata() > 0
                     for path in brainmask_files]
        mask_glob = masks_arr[0]
        for arr in masks_arr[1:]:
            mask_glob = np.logical_and(mask_glob, arr)
    else:
        mask_glob = np.ones(imgs_size).astype(bool)
    imgs_arr = imgs_arr[:, mask_glob]
    print(df)
    print("  flat masked images:", imgs_arr.shape)

    print_title("Compute PCA analysis...")
    pca_path = plot_pca(imgs_arr, df, outdir)
    print_result(pca_path)

    print_title("Compute correlation comparision...")
    df_corr, corr_path = compute_mean_correlation(imgs_arr, df, outdir)
    print_result(corr_path)

    print_title("Save quality control scores...")
    df_qc = df_corr
    df_qc["qc"] = (df_qc["corr_mean"] > corr_thr).astype(int)
    qc_path = os.path.join(outdir, "qc.tsv")
    df_qc.sort_values(by=["corr_mean"], inplace=True)
    df_qc.to_csv(qc_path, index=False, sep="\t")
    print(df_qc)
    print_result(qc_path)

    print_title("Save scores histograms...")
    data = {"corr": {"data": df_qc["corr_mean"].values, "bar": corr_thr}}
    snap = plot_hists(data, outdir)
    print_result(snap)

    print_title("Save brain images ordered by mean correlation...")
    sorted_indices = [
        df.index[(df.participant_id == row.participant_id) &
                 (df.session == row.session) &
                 (df.run == row.run)].item()
        for _, row in df_qc.iterrows()]
    img_files_cat = (
        [np.asarray(img_files)[sorted_indices]] +
        [np.asarray(item)[sorted_indices] for item in extra_img_files])
    img_files_cat = [item for item in zip(*img_files_cat)]
    cut_coords = [(1, 1, 1)] * (len(extra_img_files) + 1)
    snaps, snapdir = plot_images(img_files_cat, cut_coords, outdir)
    df_report = df_qc.copy()
    df_report["snap_path"] = snaps
    df_report["snap_path"] = df_report["snap_path"].apply(
        create_clickable)
    print_result(snapdir)

    print_title("Save quality check ordered by mean correlation...")
    report_path = os.path.join(outdir, "qc.html")
    html_report = df_report.to_html(index=False, table_id="table-brainprep")
    html_report = unescape(html_report)
    with open(report_path, "wt") as of:
        of.write(html_report)
    print_result(report_path)
