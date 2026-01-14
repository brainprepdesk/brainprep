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

import nibabel
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.stats import pearsonr
from sklearn.decomposition import IncrementalPCA

from .plotting import plot_pca
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
        If True, copy only the content of the source directory. Default False.
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
    target_directory = output_dir
    if not content:
        target_directory /= source_dir.name
    if not dryrun:
        if not source_dir.is_dir():
            raise ValueError(
                f"Source '{source_dir}' is not a directory."
            )
        if not content:
            shutil.copytree(source_dir, output_dir)
        else:
            for item in source_dir.iterdir():
                target = output_dir / item.name
                if item.is_dir():
                    shutil.copytree(item, target, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, target)
            if not any(source_dir.iterdir()):
                source_dir.rmdir()
    return (target_directory, )


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
        If the input file is not compressed.if __name__ == "__main__":
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
        image_files_regex: Path,
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
    correlations_file.parent.mkdir(parents=True, exist_ok=True)

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
        image_files_regex: Path,
        output_dir: Directory,
        batch_size: int = 10,
        batch_plot: bool = False,
        dryrun: bool = False) -> tuple[File]:
    """
    Compute Incremental PCA with only 2 components on a set of images
    matching a regex pattern.

    Parameters
    ----------
    image_files_regex : str
        A REGEX to image files, each representing an image,
        all images must have the same size.
    output_dir : Directory
        Directory where a TSV file containing the values of the first two
        components created by the PCA ill be saved, a Directory containing
        all the graph of all batch.
    batch_size : int or None, optional
        Number of images to process in each batch. Default is 10 following
        sklearn's recommendation on IncrementalPCA.
    batch_plot : bool, optional
        If True, generates and saves PCA plots for each batch. It plots
        all images in a batch on a graph using the first two components.
        Default is False.
    dryrun : bool, optional
        If True, runs in dryrun mode without executing
        the actual computations. Default is False.

    Returns
    -------
    components_file : File
        Path to the TSV file containing the values of
        the first two components.

    Raises
    ------
    ValueError
        If no images are found matching the regex pattern.
    ValueError
        If any batch has less than 2 images for PCA computation.
    """
    pca_dir = output_dir
    pca_dir.mkdir(parents=True, exist_ok=True)
    components_file = output_dir / "df_scores.csv"

    if not dryrun:

        image_files = glob.glob(str(image_files_regex))

        if len(image_files) == 0:
            raise ValueError(
                f"No files found matching the input regex:{image_files_regex}"
            )
        batches = [image_files[i:i + batch_size]
                    for i in range(0, len(image_files), batch_size)]

        if not all(len(batch_files) > 2 for batch_files in batches):
            raise ValueError(
                "All batches must have at least 2 images for PCA computation."
            )

        ipca = IncrementalPCA(n_components=2)

        for batch_files in batches:
            data = [nibabel.load(batch_file).get_fdata()
                for batch_file in batch_files]
            data = [item.flatten() for item in data]
            ipca.partial_fit(data)
        all_proj = []
        dfs = []
        for idx, batch_files in enumerate(batches):
            data = [
                nibabel.load(batch_file).get_fdata()
                for batch_file in batch_files]
            data = [img.flatten() for img in data]
            components = ipca.transform(data)
            all_proj.append(components)

            info = [
                parse_bids_keys(Path(batch_file))
                for batch_file in batch_files]
            df_batch = pd.DataFrame({
                "participant_id": [item['sub'] for item in info],
                "session": [item['ses'] for item in info],
                "run": [item['run'] for item in info],
                "pc1": components[:, 0],
                "pc2": components[:, 1]
            })
            dfs.append(df_batch)
            if batch_plot:
                sub_ses_name = [f"sub-{item['sub']}_ses-{item['ses']}"
                    for item in info]
                plot_pca(
                    components=components,
                    subject_ids=sub_ses_name,
                    explained_variance_ratio=ipca.explained_variance_ratio_,
                    title=f"Batch {idx + 1}",
                    output_dir=pca_dir / f"batch_{idx+1}.png"
                )

        df_all = pd.concat(dfs, ignore_index=True)
        df_all.to_csv(output_dir / "df_scores.csv", index=False)
        stacked_batch_components = np.vstack(all_proj)

        plot_pca(
            components=stacked_batch_components,
            subject_ids=df_all["participant_id"].tolist(),
            explained_variance_ratio=ipca.explained_variance_ratio_,
            title="Incremental PCA",
            output_dir=pca_dir / "incremental_pca.png",
            figsize=(20, 30)
        )
    return (components_file, )
