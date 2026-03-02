##########################################################################
# NSAp - Copyright (C) CEA, 2025 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Fetcher to download the OpenMS dataset from GitHub.
"""

import json
from pathlib import Path

from ..typing import (
    Directory,
)
from ..utils import (
    Bunch,
    print_info,
)
from .utils import (
    git_download,
)


class OpenMSDataset:
    """
    Open Multiple Sclerosis (OpenMS) anatomical dataset.

    This `dataset <https://github.com/muschellij2/open_ms_data>`_
    :footcite:p:`lesjak2016data` contains
    Magnetic Resonance (MR) images of Multiple Sclerosis (MS)
    patients with corresponding ground truth segmentations of white matter
    lesion changes.

    Parameters
    ----------
    datadir : Directory
        Directory where data will be stored.

    References
    ----------

    .. footbibliography::

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from pathlib import Path
    >>> from brainprep.datasets import OpenMSDataset
    >>>
    >>> datadir = Path("/tmp/brainprep-data")
    >>> datadir.mkdir(parents=True, exist_ok=True)
    >>> dataset = OpenMSDataset(datadir)
    >>> with Config(verbose=False):
    ...     data = dataset.fetch(
    ...         subject="01",
    ...         modality="T1w",
    ...         dtype="cross_sectional",
    ...     )
    >>> data
    Bunch(
      description: PosixPath('...')
      anat: PosixPath('...')
    )

    Attributes
    ----------
    _url : str
        Internal URL used to fetch data.
    """

    _url: str = (
        "https://raw.githubusercontent.com/muschellij2/open_ms_data/refs/"
        "heads/master/{dtype}/raw/patient{subject}/{basename}.nii.gz"
    )

    def __init__(
            self,
            datadir: Directory) -> None:
        self.datadir = Path(datadir)
        self.allowed_dtypes = [
            "cross_sectional",
            "longitudinal",
        ]
        self.allowed_subjects = [
            [f"{str(subject).zfill(2)}" for subject in range(1, 31)],
            [f"{str(subject).zfill(2)}" for subject in range(1, 21)],
        ]
        self.allowed_modalities = [
            "T1W",
            "T2W",
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
            dtype: str = "cross_sectional") -> Bunch:
        """ Fetch data.

        Parameters
        ----------
        subject : str
            the subject identifier. This identifier must lie in ['01' - '30'],
            ['01' - '20'], for cross sectional or longitudinal data
            respectively.
        modality : str
            the modality to be fetched: 'T1w', 'T2w' or 'FLAIR'.
        dtype : str
            the type of data to download: 'cross_sectional' or 'longitudinal'.
            Default 'cross_sectional'.

        Returns
        -------
        dataset : Bunch
            the fetched data path. Keys are either 'sub-{subject}' or
            'sub-{subject}_ses-{timepoint}' for cross sectional and
            longitudinal data, respectively. A 'description' entry is
            also available.
        """
        dataset = Bunch()
        self.sanity_check(subject, modality.upper(), dtype)

        description_file = (
            self.datadir /
            "rawdata" /
            "dataset_description.json"
        )
        if not description_file.is_file():
            description_file.parent.mkdir(parents=True, exist_ok=True)
            with open(description_file, "w") as of:
                description = {
                    "Name": "OpenMS dataset",
                    "BIDSVersion": "1.0.2",
                }
                json.dump(description, of, indent=4)
        dataset["description"] = description_file

        to_download = []
        if dtype == "longitudinal":
            for counter, timepoint in enumerate(self.timepoints):
                basename = f"{timepoint}_{modality.upper()}"
                url = self._url.format(
                    dtype=dtype,
                    subject=subject,
                    basename=basename,
                )
                destination = (
                    self.datadir /
                    "rawdata" /
                    f"sub-{subject}" /
                    f"ses-{timepoint}" /
                    "anat" /
                    f"sub-{subject}_ses-{timepoint}_{modality}.nii.gz"
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                dataset[f"anat{counter + 1}"] = destination
                to_download.append((url, destination))
        else:
            url = self._url.format(
                dtype=dtype,
                subject=subject,
                basename=modality.upper(),
            )
            destination = (
                self.datadir /
                "rawdata" /
                f"sub-{subject}" /
                "ses-01" /
                "anat" /
                f"sub-{subject}_{modality}.nii.gz"
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            dataset["anat"] = destination
            to_download.append((url, destination))

        for url, destination in to_download:
            if not destination.is_file():
                print_info(f"downloading: {url}")
                git_download(url, destination)

        return dataset

    def sanity_check(
            self,
            subject: str,
            modality: str,
            dtype: str = "cross_sectional") -> None:
        """ Check that the fetch parameters are correct.

        Parameters
        ----------
        subject : str
            the subject identifier. This identifier must lie in ['01' - '30'],
            ['01' - '20'], for cross sectional or longitudinal data
            respectively.
        modality : str
            the modality to be fetched: 'T1w', 'T2w' or 'FLAIR'.
        dtype : str
            the type of data to download: 'cross_sectional' or 'longitudinal'.
            Default 'cross_sectional'

        Raises
        ------
        ValueError
            If the fetch input parameters are not correct.
        """
        if dtype not in self.allowed_dtypes:
            raise ValueError("Unexpected data type.")
        if modality not in self.allowed_modalities:
            raise ValueError("Unexpected modality.")
        index = self.allowed_dtypes.index(dtype)
        if subject not in self.allowed_subjects[index]:
            raise ValueError("Unexpected subject.")
