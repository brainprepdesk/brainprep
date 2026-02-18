##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Tools.
"""


import glob
import gzip
import shutil
from pathlib import Path
import re

import nibabel
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.decomposition import IncrementalPCA

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
from ..wrappers import pywrapper
from .plotting import plot_pca


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def mask_diff(
        im1_file: File,
        im2_file: File,
        output_dir: Directory,
        entities: dict,
        threshold: float = 0.6,
        dryrun: bool = False) -> tuple[File]:
    """
    Computes a defacing mask by thresholding the intensity difference between
    two input images.

    Parameters
    ----------
    im1_file : File
        Path to the first image.
    im2_file : File
        Path to the second image.
    output_dir : Directory
        Directory where the defacing mask will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    threshold : float
        Threshold for intensity difference to define the mask. Default 0.6.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    mask_file : File
        Path to the saved mask image.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_defacemask".format(
        **entities)
    mask_file = output_dir / f"{basename}.nii.gz"

    if not dryrun:
        im1 = nibabel.load(im1_file)
        im2 = nibabel.load(im2_file)
        mask = np.abs(im1.get_fdata() - im2.get_fdata())
        indices = np.where(mask > threshold)
        mask[...] = 0
        mask[indices] = 1
        im_mask = nibabel.Nifti1Image(mask, im1.affine)
        nibabel.save(im_mask, mask_file)

    return (mask_file, )


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
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


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
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
            output_dir /= source_dir.name
        else:
            for item in source_dir.iterdir():
                target = output_dir / item.name
                shutil.move(item, output_dir / item.name)
            if not any(source_dir.iterdir()):
                source_dir.rmdir()
    return (output_dir, )


@outputdir
@log_runtime(
    bunched=False)
@pywrapper
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


@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def mean_correlation(
        image_files_regex: str,
        atlas_file: File,
        output_dir: Directory,
        correlation_threshold: float = 0.5,
        dryrun: bool = False) -> tuple[File]:
    """
    Compute the mean Pearson correlation between a reference image and a list
    of other images.

    Parameters
    ----------
    image_files_regex : str
        A REGEX to image files, each representing an image of the same shape
        and geometry as `atlas_file`.
    atlas_file : File
        An file representing the reference image.
    output_dir : Directory
        Directory where a TSV file containing the mean correlation values is
        created.
    correlation_threshold : float
        Quality control threshold on the correlation score. Default 0.5.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    correlations_file : File
        A TSV file containing the Pearson correlation coefficient between the
        atlas image and each image pointed by the input REGEX.

    Raises
    ------
    ValueError
        If the atlas and an image have incompatible shape or geometry.
    """
    correlations_file = output_dir / "mean_correlations.tsv"

    if not dryrun:

        image_files = glob.glob(str(image_files_regex))
        atlas_im = nibabel.load(atlas_file)
        atlas_arr = atlas_im.get_fdata()

        scores = pd.DataFrame(
            columns=(
                "participant_id",
                "session",
                "run",
                "mean_correlation",
            )
        )
        for path in image_files:
            entities = parse_bids_keys(Path(path))
            im = nibabel.load(path)
            arr = atlas_im.get_fdata()
            if atlas_arr.shape != arr.shape:
                raise ValueError(
                    f"Atlas and image have incompatible shape: {path}"
                )
            if not np.allclose(atlas_im.affine, im.affine):
                raise ValueError(
                    f"Atlas and image have incompatible orientation: {path}"
                )
            corr, _ = pearsonr(
                atlas_arr.flatten(),
                arr.flatten(),
            )
            scores.loc[len(scores)] = [
                entities["sub"],
                entities["ses"],
                entities["run"],
                corr,
            ]

        scores["qc"] = (
            scores["mean_correlation"] > correlation_threshold
        ).astype(int)
        scores.to_csv(
            correlations_file,
            index=False,
            sep="\t",
        )

    return (correlations_file, )


@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def incremental_pca(
        image_files_regex: str,
        output_dir: Directory,
        batch_size: int = 10,
        dryrun: bool = False) -> tuple[File]:
    """
    Perform an Incremental PCA with 2 components on a collection of images
    matched by a regex pattern, processing them in batches.

    The function loads all images matching the provided regex, splits them
    into batches, and incrementally fits a PCA model using scikit-learn's
    ``IncrementalPCA``. Each image is flattened into a 1D vector before
    processing. After fitting, the function transforms all batches to obtain
    the first two principal components for each image. These components are
    saved in a TSV file as two columns named ``pc1`` and ``pc2``. BIDS
    entities (``participant_id``, ``session``, ``run``) are extracted from
    filenames using ``parse_bids_keys`` and included in the output table.

    Parameters
    ----------
    image_files_regex : str
        A REGEX to image files, each representing an image,
        all images must have the same size.
    output_dir : Directory
        Directory where a TSV file containing the values of the first two
        components created by the PCA ill be saved, a Directory containing
        all the graph of all batch.
    batch_size : int
        Number of images to use in each batch. If None, a single batch is used.
        Default is 10.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    pca_file : File
        Path to the generated ``pca.tsv`` file containing the PCA results.

    Raises
    ------
    ValueError
        If no image matches the regex pattern.
        If the dataset contains fewer than 2 images, which prevents PCA
        computation.
    """
    pca_file = output_dir / "pca.tsv"

    if not dryrun:

        image_files = glob.glob(str(image_files_regex))
        n_images = len(image_files)
        if n_images == 0:
            raise ValueError(
                f"No image matches the regex pattern: {image_files_regex}"
            )
        if n_images < 2:
            raise ValueError(
                f"The dataset contains fewer than 2 images: {n_images}"
            )
        batches = [
            image_files[idx:idx + batch_size]
            for idx in range(0, len(image_files), batch_size)
        ]

        pca = IncrementalPCA(n_components=2)
        for batch_files in batches:
            data = [
                nibabel.load(_file).get_fdata().flatten()
                for _file in batch_files
            ]
            pca.partial_fit(data)

        df = []
        for batch_files in batches:
            data = [
                nibabel.load(_file).get_fdata().flatten()
                for _file in batch_files
            ]
            components = pca.transform(data)
            info = [
                parse_bids_keys(Path(_file))
                for _file in batch_files
            ]
            partial_df = pd.DataFrame({
                "participant_id": [item["sub"] for item in info],
                "session": [item["ses"] for item in info],
                "run": [item["run"] for item in info],
                "pc1": components[:, 0],
                "pc2": components[:, 1],
                "explained_variance_ratio_pc1": [
                    pca.explained_variance_ratio_[0],
                ] * len(info),
                "explained_variance_ratio_pc2": [
                    pca.explained_variance_ratio_[1],
                ] * len(info),
            })
            df.append(partial_df)
        df = pd.concat(df, ignore_index=True)
        df.to_csv(pca_file, index=False, sep="\t")

    return (pca_file, )

@outputdir
@log_runtime(
    bunched = False)
@coerceparams
def filter_metrics(
    metrics_files: list[str],
    modalities: list[str],
    output_dir: Directory) -> tuple(list[File]):
    """
    Filter the MRIQC metrics based on the modality and default criteria.
    
    Parameters
    ----------
    metrics_files : list[str]
        List of paths to the MRIQC metrics files.
    modalities : list[str]
        List of modalities in the current study.
    output_dir : Directory
        Directory where the filtered metrics will be saved.

    Returns
    -------
    iqm_files : list[File] — paths to the group level 
        Image Quality Metrics (IQMs) filtered.

    Raises
    ------
    ValueError
        If modality does not match the provided modalities (BIDS).
        If filename format does not match "group_{modality}.tsv").
    """
    metrics_by_modalities = {
        'T1w': ['cjv', 'cnr', 'efc','fber','wm2max', 'inu_med','qi_1', 'qi_2'
        'icvs_wm','fwhm_avg', 'rpvs_wm', 'snr_wm', 'snrd_wm','wm2max',
        'bids_name'],
        'bold': ['aor', 'aqi', 'dummy_trs', 'dvars_vstd', 'efc', 'fber',
        'fd_mean', 'fwhm_avg', 'gcor', 'gsr_x', 'gsr_y', 'snr', 'tsnr',
        'bids_name'],
        'dwi':['bdiffs_max', 'bdiffs_median', 'efc_shell01', 'efc_shell02',
        'fber_shell01', 'fber_shell02', 'fd_mean', 'ndc', 'sigma_pca', 
        'sigma_piesno', 'snr_cc_shell0', 'snr_cc_shell1_best',
        'snr_cc_shell1_worst', 'spikes_global', 'bids_name']
    }
    forbidden_prefixes = ('spacing', 'summary', 'tpm', 'size')
    
    print(f"Filtering metrics for modalities: {metrics_files}")

    iqm_files = [
        output_dir / f"filtered_group_{mod}.tsv"
        for mod in modalities
    ]
    for file in metrics_files:
        metric_df = pd.read_csv(str(file), sep='\t')
        match = re.search(r"group_(\w+).tsv", Path(file).name)

        if match:
            if match.group(1) not in modalities:
                raise ValueError(
                    f"Modality {match.group(1)} not in {modalities}")
            
            cols_to_keep = [
                col for col in metric_df.columns
                if not col.startswith(forbidden_prefixes)
                and col in metrics_by_modalities[match.group(1)]
                ]

            filtered_df = metric_df[cols_to_keep].copy()
            output_file = output_dir / f"filtered_{Path(file).name}"
            filtered_df.to_csv(output_file, sep='\t', index=False)
        else:
            raise ValueError(f"Invalid filename format: {Path(file).name}")

    return (iqm_files, )