##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Plotting functions.
"""

import itertools

import matplotlib.pyplot as plt
import nibabel
import numpy as np
import pandas as pd
import seaborn as sns
from nilearn import plotting

from ..reporting import log_runtime
from ..typing import (
    Directory,
    File,
)
from ..utils import (
    coerceparams,
    outputdir,
)
from ..wrappers import pywrapper


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def plot_defacing_mosaic(
        im_file: File,
        mask_file: File,
        output_dir: Directory,
        entities: dict,
        dryrun: bool = False) -> tuple[File]:
    """
    Generates a defacing mosaic image by overlaying a mask on an anatomical
    image.

    Parameters
    ----------
    im_file : File
        Path to the anatomical image.
    mask_file : File
        Path to the defacing mask.
    output_dir : Directory
        Directory where the mosaic image will be saved.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    mosaic_file : File
        Path to the saved mosaic image.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_mod-T1w_deface".format(
        **entities)
    mosaic_file = output_dir / f"{basename}mosaic.png"

    if not dryrun:
        plotting.plot_roi(
            mask_file,
            bg_img=im_file,
            display_mode="z",
            cut_coords=25,
            black_bg=True,
            alpha=0.6,
            colorbar=False,
            output_file=mosaic_file
        )
        arr = plt.imread(mosaic_file)
        cut = int(arr.shape[1] / 5)
        plt.figure()
        arr = np.concatenate(
            [arr[:, idx * cut: (idx + 1) * cut] for idx in range(5)], axis=0)
        plt.imshow(arr)
        plt.axis("off")
        plt.savefig(mosaic_file)

    return (mosaic_file, )


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def plot_histogram(
        table_file: File,
        col_name: str,
        output_dir: Directory,
        bar_coords: list[float] | None = None,
        dryrun: bool = False) -> tuple[File]:
    """
    Generates a histogram image with optional vertical bars.

    Parameters
    ----------
    table_file : File
        TSV table containing the data to be displayed.
    col_name : str
        Name of the column containing the histogram data.
    output_dir : Directory
        Directory where the image with the histogram will be saved.
    bar_coords: list[float] | None
        Coordianates of vertical lines to be displayed in red. Default None.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    histogram_file : File
        Generated image with the histogram.
    """
    histogram_file = output_dir / f"histogram_{col_name}.png"

    if not dryrun:

        data = pd.read_csv(
            table_file,
            sep="\t",
        )
        arr = data[col_name].astype(float)
        arr = arr[~np.isnan(arr)]
        arr = arr[~np.isinf(arr)]

        _, ax = plt.subplots()
        sns.histplot(
            arr,
            color="gray",
            alpha=0.6,
            ax=ax,
            kde=True,
            stat="density",
            label=col_name,
        )
        for x_coord in bar_coords or []:
            ax.axvline(x=x_coord, color="red")
        ax.spines["right"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.legend()

        plt.savefig(histogram_file)

    return (histogram_file, )


@coerceparams
@outputdir
@log_runtime(
    bunched=False)
@pywrapper
def plot_brainparc(
        wm_mask_file: File,
        gm_mask_file: File,
        csf_mask_file: File,
        brain_mask_file: File,
        output_dir: Directory,
        entities: dict,
        dryrun: bool = False) -> tuple[File]:
    """

    Parameters
    ----------
    wm_mask_file : File
        Binary mask of white matter regions.
    gm_mask_file : File
        Binary mask of gray matter regions.
    csf_mask_file : File
        Binary mask of cerebrospinal fluid regions.
    brain_mask_file : File
        Binary brain mask file.
    output_dir : Directory
        FreeSurfer working directory containing all the subjects.
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    dryrun : bool
        If True, skip actual computation and file writing. Default False.

    Returns
    -------
    brainparc_image_file : File
        Image of the GM mask and GM, WM, CSF tissues histograms.
    """
    basename = "sub-{sub}_ses-{ses}_run-{run}_brainparc".format(
        **entities)
    brainparc_image_file = output_dir / f"{basename}.png"

    if not dryrun:

        subject = f"run-{entities['run']}"
        anat_file = output_dir / subject / "mri" / "norm.mgz"

        fig, axs = plt.subplots(2)
        plotting.plot_roi(
            roi_img=gm_mask_file,
            bg_img=anat_file,
            alpha=0.3,
            figure=fig,
            axes=axs[0],
        )

        anat_arr = nibabel.load(anat_file).get_fdata()
        mask_arr = nibabel.load(brain_mask_file).get_fdata()
        bins = np.histogram_bin_edges(
            anat_arr[mask_arr],
            bins="auto",
        )
        palette = itertools.cycle(sns.color_palette("Set1"))
        for name, path in [("WM", wm_mask_file),
                           ("GM", gm_mask_file),
                           ("CSF", csf_mask_file)]:
            mask = nibabel.load(path).get_fdata().astype(int)
            sns.histplot(
                anat_arr[mask],
                bins=bins,
                color=next(palette),
                alpha=0.6,
                ax=axs[1],
                kde=True,
                stat="density",
                label=name,
            )
        axs[1].spines["right"].set_visible(False)
        axs[1].spines["top"].set_visible(False)
        axs[1].legend()

        plt.subplots_adjust(wspace=0, hspace=0, top=0.9, bottom=0.1)
        plt.savefig(brainparc_image_file)

    return (brainparc_image_file, )

@coerceparams
@log_runtime(
    bunched=False)
@pywrapper
def plot_pca(
        components: np.ndarray,
        subject_ids: list[str],
        explained_variance_ratio: np.ndarray,
        title: str,
        output_dir: str,
        figsize: tuple = (20, 10)
        ) -> None:
    """
    Plot PCA components and save the figure.

    Parameters
    ----------
    components : np.ndarray
        The PCA components to plot.
    subject_ids : list[str]
        List of subject IDs for annotation.
    explained_variance_ratio : np.ndarray
        Explained variance ratio for each component.
    title : str
        Title of the plot.
    output_path : Path
        Path to save the plot.
    figsize : Tuple[int, int], optional
        Figure size. Default is (20, 10).
    """
    fig, ax = plt.subplots(figsize=figsize)
    ax.scatter(components[:, 0], components[:, 1])

    for idx, desc in enumerate(subject_ids):
        ax.annotate(desc, xy=(components[idx, 0], components[idx, 1]),
                    xytext=(4, 4), textcoords="offset pixels")

    plt.xlabel(f"PC1 (var={explained_variance_ratio[0]:.2f})")
    plt.ylabel(f"PC2 (var={explained_variance_ratio[1]:.2f})")
    plt.title(title)
    plt.axis("equal")
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    plt.tight_layout()

    plt.savefig(output_dir)
    plt.close(fig)
