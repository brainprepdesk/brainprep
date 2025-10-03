##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Interface for brain imaging defacing.
"""

from typing import Optional

import matplotlib.pyplot as plt
import nibabel
import numpy as np
from nilearn import plotting

import brainprep
from ..utils import (
    Bunch,
    print_result,
    print_title,
)
from ..reporting import log_runtime


@log_runtime
def brainprep_deface(
        anatomical: str,
        outdir: str) -> None:
    """ Defacing pre-processing workflow.

    The ``mri_deface`` FSL defacing function :footcite:p:`almagro2018deface`
    is applied with default settings. It removes the face and ears.

    Parameters
    ----------
    anatomical: str
        path to the anatomical T1w image.
    outdir: str
        the destination folder.

    Notes
    -----
    Give a T1w image as input.

    Examples
    --------
    >>> from brainprep.workflow import brainprep_deface
    >>> brainprep_deface(anatomical_file, outdir)

    References
    ----------

    .. footbibliography::
    """
    #print_title("Launch FSL defacing...")
    deface_anat, mask_anat = None, None # brainprep.deface(anatomical, outdir)
    #print_result(deface_anat)
    #print_result(mask_anat)
    return Bunch(deface_anat=deface_anat, mask_anat=mask_anat)


def brainprep_deface_qc(
        anatomical: str,
        anatomical_deface: str,
        deface_root: str,
        thr_mask: Optional[float] = 0.6) -> None:
    """ Defacing QC workflow.

    Parameters
    ----------
    anatomical: str
        path to the anatomical T1w image.
    anatomical_deface: str
        path to the defaced anatomical T1w image
        (see :func:`~brainprep.workflow.deface.brainprep_deface` function to
        generate this image).
    deface_root: str
        the destination filename root (without extension).
    thr_mask: float, default 0.6
        the threshold applied to the two input anatomical images intensities
        difference in order to retrieve the defacing mask.
    """
    print_title("Generate defacing mask...")
    im_deface = nibabel.load(anatomical_deface)
    im = nibabel.load(anatomical)
    arr_deface = im_deface.get_fdata()
    arr = im.get_fdata()
    mask = np.abs(arr_deface - arr)
    indices = np.where(mask > thr_mask)
    mask[...] = 0
    mask[indices] = 1
    im_mask = nibabel.Nifti1Image(mask, im_deface.affine)
    mask_file = deface_root + ".nii.gz"
    nibabel.save(im_mask, mask_file)

    print_title("Generate defacing plots...")
    outfile = deface_root + ".png"
    plotting.plot_roi(
        im_mask, bg_img=im, display_mode="z",
        cut_coords=25, black_bg=True, output_file=outfile)
    arr = plt.imread(outfile)
    cut = int(arr.shape[1] / 5)
    fig = plt.figure()
    arr = np.concatenate(
        [arr[:, idx * cut: (idx + 1) * cut] for idx in range(5)], axis=0)
    plt.imshow(arr)
    plt.axis("off")
    plt.savefig(outfile)
