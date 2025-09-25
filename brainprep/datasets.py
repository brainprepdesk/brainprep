##########################################################################
# NSAp - Copyright (C) CEA, 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Fetch some data.
"""

from typing import Optional

import os
from pathlib import Path
import shutil
import requests
from .utils import (
    Bunch,
)


class AnatomicalDataset:
    """ Anatomical dataset.

    This `dataset <https://github.com/muschellij2/open_ms_data>`_ contains
    Magnetic Resonance (MR) images of Multiple Sclerosis (MS)
    patients with corresponding ground truth segmentations of white matter
    lesion changes.

    The cross-sectional data is from the "3D MR image database of Multiple
    Sclerosis patients with white matter lesion segmentations".

    The longitudinal data is from the "Longitudinal MR image database of
    Multiple Sclerosis patients with white matter lesion change segmentation".

    Attributes
    ----------
    datadir: Path
        directory where data will be stored.

    Examples
    --------
    >>> from pathlib import Path
    >>> from brainprep.datasets import AnatomicalDataset
    >>> datadir = Path("/tmp/brainprep-data")
    >>> datadir.mkdir(parents=True, exist_ok=True)
    >>> dataset = AnatomicalDataset(datadir)
    >>> data = dataset.fetch(
    ...     subject="01",
    ...     modality="T1w",
    ...     dtype="cross_sectional",
    ... )
    >>> print(data)
    Bunch(
      sub-01: PosixPath('/tmp/brainprep-data/sub-01_T1w.nii.gz')
    )

    Raises
    ------
    ValueError
        if an invalid data type, modality or subject is passed to the
        :meth:`~brainprep.datasets.AnatomicalDataset.fetch` method.
    """
    _url = (
        "https://raw.github.com/muschellij2/open_ms_data/master/"
        "{dtype}/raw/patient{subject}/{basename}.nii.gz"
    )

    def __init__(
            self,
            datadir: Path) -> None:
        """ Init class.
        """
        self.datadir = datadir
        self.allowed_dtypes = [
            "cross_sectional",
            "longitudinal",
        ]
        self.allowed_subjects = [
            [f"{str(subject).zfill(2)}" for subject in range(1, 31)],
            [f"{str(subject).zfill(2)}" for subject in range(1, 21)],
        ]
        self.allowed_modalities = [
            "T1w",
            "T2w",
            "FLAIR",
        ]
        self.timepoints = [
            "study1",
            "study2",
        ]

    def fetch(
            self,
            subject: str,
            modality: str,
            dtype: Optional[str] = "cross_sectional") -> Bunch:
        """ Fetch data.

        Parameters
        ----------
        subject: str
            the subject identifier. This indentifier must lie in ['01' - '30'],
            ['01' - '20'], for cross sectional or longitudinal data
            respectively.
        modality: str
            the modality to be fetched: 'T1w', 'T2w' or 'FLAIR'.
        dtype: str, default 'cross_sectional'
            the type of data to download: 'cross_sectional' or 'longitudinal'.

        Returns
        -------
        dataset: Bunch
            the fetched data path. Keys are either 'sub-{subject}' or
            'sub-{subject}_ses-{timepoint}' for cross sectional and
            longitudinal data, respectively.
        """
        self.sanity_check(subject, modality, dtype)

        dataset = Bunch()
        to_download = []
        if dtype == "longitudinal":
            for timepoint in self.timepoints:
                basename = f"{timepoint}_{modality}"
                url = self._url.format(
                    dtype=dtype,
                    subject=subject,
                    basename=basename,
                )
                destination = (
                    self.datadir /
                    f"sub-{subject}_ses-{timepoint}_{modality}.nii.gz"
                )
                dataset[f"sub-{subject}_ses-{timepoint}"] = destination
                to_download.append((url, destination))
        else:
            url = self._url.format(
                dtype=dtype,
                subject=subject,
                basename=modality,
            )
            destination = (
                self.datadir /
                f"sub-{subject}_{modality}.nii.gz"
            )
            dataset[f"sub-{subject}"] = destination
            to_download.append((url, destination))

        for url, destination in to_download:
            if not os.path.isfile(destination):
                self.git_download(url, destination)

        return dataset

    @classmethod
    def git_download(
            cls,
            url: str,
            destination: Path) -> None:
        """ Download data from GitHub.

        Parameters
        ----------
        url: str
            the link to the data.
        destination: Path
            the location of the downloaded data.
        """
        response = requests.get(url, stream=True)
        with destination.open("wb") as of:
            response.raw.decode_content = False
            shutil.copyfileobj(response.raw, of)
        del response

    def sanity_check(
            self,
            subject: str,
            modality: str,
            dtype: Optional[str] = "cross_sectional") -> bool:
        """ Check that the fetch parameters are correct.

        Parameters
        ----------
        subject: str
            the subject identifier. This indentifier must lie in ['01' - '30'],
            ['01' - '20'], for cross sectional or longitudinal data
            respectively.
        modality: str
            the modality to be fetched: 'T1w', 'T2w' or 'FLAIR'.
        dtype: str, default 'cross_sectional'
            the type of data to download: 'cross_sectional' or 'longitudinal'.

        Returns
        -------
        valid: bool
            the data integrity status.
        """
        if dtype not in self.allowed_dtypes:
            raise ValueError("Unexpected data type.")
        if modality not in self.allowed_modalities:
            raise ValueError("Unexpected modality.")
        index = self.allowed_dtypes.index(dtype)
        if subject not in self.allowed_subjects[index]:
            raise ValueError("Unexpected subject.")
