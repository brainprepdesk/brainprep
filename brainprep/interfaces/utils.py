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

import matplotlib.pyplot as plt
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
    correlations_file.parent.mkdir(parents=True, exist_ok=True)

    if not dryrun:

        image_files = glob.glob(image_files_regex)
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
            entities = parse_bids_keys(path)
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
def pca_incrementale(
    image_files_regex: str,
    output_dir: Directory,
    batch_size: int,
    dryrun: bool = False) -> tuple[File, Directory]:
    """
    Compute Incremental PCA on a set of images matching a regex pattern.

    Parameters
    ----------
    image_files_regex : str
        A REGEX to image files, each representing an image, 
        all images must have the same size.
    output_dir : Directory
        Directory where a TSV file containing the values of the first two 
        components created by the PCA will be saved, a Directory containing 
        all the graph of all batch.   
    batch_size : int
        Number of images to process in each batch.
    dryrun : bool, optional
        If True, runs in dryrun mode without executing the actual computations.
        Default is False.
        
    Returns
    -------
    components_file : File
        Path to the TSV file containing the values of the first two components.
    graphs_dir : Directory
        Directory containing the graphs of all batches and the global graph.

    """
    pca_dir = output_dir / "graphs"
    pca_dir.mkdir(parents=True, exist_ok=True)

    if not dryrun:
        image_files = glob.glob(image_files_regex)
        batches = [ image_files[i:i + batch_size] 
                    for i in range(0, len(image_files), batch_size)]
        ipca = IncrementalPCA(n_components=2)

        for batch_files in batches:
            img = [nibabel.load(batch_file).get_fdata() 
                for batch_file in batch_files]
            img = [u.flatten() for u in img]
            ipca.partial_fit(img)
        
        all_proj=[]
        dfs=[]
        for i, batch_files in enumerate(batches):
            img = [nibabel.load(batch_file).get_fdata() for batch_file in batch_files]
            img = [u.flatten() for u in img]
            components = ipca.transform(img)

            info = [parse_bids_keys(Path(batch_file)) for batch_file in batch_files]    
            subject_ids = [f"sub-{u['sub']}_ses-{u['ses']}" for u in info] 
            all_proj.append(components)
            df_batch = pd.DataFrame({
                "participant_id": [f"sub-{u['sub']}_ses-{u['ses']}" for u in info],
                "session": [u['ses'] for u in info],
                "run": [u['run'] for u in info],
                "PC1": components[:, 0],
                "PC2": components[:, 1]
            })
            dfs.append(df_batch)
            
            # Visualisation
            fig, ax = plt.subplots(figsize=(20, 10))
            ax.scatter(components[:, 0], components[:, 1])
            # Annotation des points
            for idx, desc in enumerate(subject_ids):
                ax.annotate(desc, xy=(components[idx, 0], components[idx, 1]),
                            xytext=(4, 4), textcoords="offset pixels")
            # Ajout des labels
            plt.xlabel(f"PC1 (var={ipca.explained_variance_ratio_[0]:.2f})")
            plt.ylabel(f"PC2 (var={ipca.explained_variance_ratio_[1]:.2f})")
            plt.title(f"Batch {i + 1}")
            plt.axis("equal")
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            plt.tight_layout()
            # Sauvegarde
            plt.savefig(pca_dir / f"batch_{i+1}.png")
            plt.close(fig)
        
        df_all = pd.concat(dfs, ignore_index=True)
        df_all.to_csv(output_dir / "df_all.csv", index=False)

        # Génération du graphique global
        X_pca = np.vstack(all_proj)
        fig, ax = plt.subplots(figsize=(20, 30))
        ax.scatter(X_pca[:, 0], X_pca[:, 1])

        # Annotation des points
        for i, desc in enumerate(df_all["participant_id"]):
            ax.annotate(desc, xy=(X_pca[i, 0], X_pca[i, 1]),
                        xytext=(4, 4), textcoords="offset pixels")

        # Ajout des labels
        plt.xlabel(f"PC1 (var={ipca.explained_variance_ratio_[0]:.2f})")
        plt.ylabel(f"PC2 (var={ipca.explained_variance_ratio_[1]:.2f})")
        plt.title("Incremental PCA - Global View")
        plt.axis("equal")
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        plt.tight_layout()
        plt.savefig(pca_dir / "incremental_pca.png")
        plt.close()

    return ((output_dir / "df_all.csv"), pca_dir)