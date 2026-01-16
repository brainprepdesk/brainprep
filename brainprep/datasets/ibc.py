##########################################################################
# NSAp - Copyright (C) CEA, 2025 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Fetcher to download IBC dataset from OpenNeuro.
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
    openneuro_download,
)


class IBCDataset:
    """
    Individual Brain Charting (IBC) multi-modal dataset.

    This `dataset <https://openneuro.org/datasets/ds002685>`_
    :footcite:p:`pinho2018ibc` contains Magnetic Resonance (MR) images of
    13 healthy volunteers. The first session is considered and includes T1W,
    T2W, FLAIR, DWI, and task fMRI.

    Parameters
    ----------
    datadir : Directory
        Directory where data will be stored.

    Attributes
    ----------
    _url : str
        Internal URL used to fetch data.

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from pathlib import Path
    >>> from brainprep.datasets import IBCDataset
    >>>
    >>> datadir = Path("/tmp/brainprep-data")
    >>> datadir.mkdir(parents=True, exist_ok=True)
    >>> dataset = IBCDataset(datadir)
    >>> with Config(verbose=False):
    ...     data = dataset.fetch(
    ...         subject="01",
    ...         modality="anat",
    ...     )
    >>> data
    Bunch(
      description: PosixPath('...')
      anat: PosixPath('...')
    )

    References
    ----------

    .. footbibliography::
    """

    _url: str = (
        "https://s3.amazonaws.com/openneuro.org/ds002685/"
        "{key}"
    )

    def __init__(
            self,
            datadir: Directory) -> None:
        self.datadir = Path(datadir)
        self.allowed_subjects = [
            f"{str(subject).zfill(2)}" for subject in range(1, 16)
            if subject not in (3, 10)
        ]
        self.allowed_modalities = [
            "anat",
            "func",
            "dwi",
        ]

    def fetch(
            self,
            subject: str,
            modality: str) -> Bunch:
        """ Fetch data.

        Parameters
        ----------
        subject : str
            Subject identifier: ['01' - '13'].
        modality : str
            Modality to be fetched: 'anat', 'func' or 'dwi'.

        Returns
        -------
        dataset: Bunch
            Fetched data path. A 'description' entry is also available.
        """
        dataset = Bunch()
        self.sanity_check(subject, modality)

        description_file = (
            self.datadir /
            "rawdata" /
            "dataset_description.json"
        )
        if not description_file.is_file():
            description_file.parent.mkdir(parents=True, exist_ok=True)
            with open(description_file, "w") as of:
                description = {
                    "Name": "IBC dataset",
                    "BIDSVersion": "1.0.2",
                }
                json.dump(description, of, indent=4)
        dataset["description"] = description_file

        sidecar_t1w = {
            "Modality": "MR",
            "MagneticFieldStrength": 3,
            "Manufacturer": "Siemens",
            "ManufacturersModelName": "MAGNETOM Prisma-fit",
            "MRAcquisitionType": "3D",
            "SeriesDescription": "MPRAGE_SAGITTAL",
            "ProtocolName": "MPRAGE",
            "AcquisitionNumber": 1,
            "SliceThickness": 1,
            "EchoTime": 0.00298,
            "RepetitionTime": 2.3,
            "InversionTime": 0.9,
            "FlipAngle": 9,
            "PartialFourier": 0.875,
            "BaseResolution": 256,
            "FrequencyEncodingSteps": 256,
            "PhaseEncodingStepsOutOfPlane": 176,
            "ReconMatrixPE": 240,
        }
        mapping = [
            ("anat",
             f"sub-{subject}_ses-00_T1w.nii.gz",
             None),
            ("anat",
             sidecar_t1w,
             f"sub-{subject}_ses-00_T1w.json"),
        ]
        if modality == "dwi":
            mapping += [
                ("dwi",
                 f"sub-{subject}_ses-00_dwi.nii.gz",
                 None),
                ("dwi",
                 f"sub-{subject}_ses-00_dwi.bvec",
                 None),
                ("dwi",
                 f"sub-{subject}_ses-00_dwi.bval",
                 None),
                ("dwi",
                 "dwi.json",
                 f"sub-{subject}_ses-00_dwi.json"),
            ]
        elif modality == "func":
            task = "ArchiStandard"
            mapping += [
                ("func",
                 f"sub-{subject}_ses-00_task-{task}_dir-pa_bold.nii.gz",
                 None),
                ("func",
                 f"task-{task}_dir-pa_bold.json",
                 f"sub-{subject}_ses-00_task-{task}_dir-pa_bold.json"),
                ("func",
                 f"sub-{subject}_ses-00_task-{task}_dir-pa_sbref.nii.gz",
                 None),
                ("func",
                 f"task-{task}_dir-pa_sbref.json",
                 f"sub-{subject}_ses-00_task-{task}_dir-pa_sbref.json"),
                ("func",
                 f"sub-{subject}_ses-00_task-{task}_dir-pa_events.tsv",
                 None),
                ("fmap",
                 f"sub-{subject}_ses-00_task-{task}_dir-ap_sbref.nii.gz",
                 None),
                ("fmap",
                 f"task-{task}_dir-ap_sbref.json",
                 f"sub-{subject}_ses-00_task-{task}_dir-ap_sbref.json"),
            ]

        to_download = []
        for dtype, srcname, dstname in mapping:
            if dstname is None:
                url = self._url.format(
                    key=(
                        f"sub-{subject}/"
                        "ses-00/"
                        f"{dtype if dtype != 'fmap' else 'func'}/"
                        f"{srcname}"
                    )
                )
            elif isinstance(srcname, dict):
                pass
            else:
                url = self._url.format(
                    key=f"{srcname}"
                )
            destination = (
                self.datadir /
                "rawdata" /
                f"sub-{subject}" /
                "ses-00" /
                dtype /
                (dstname or srcname)
            )
            destination.parent.mkdir(parents=True, exist_ok=True)
            is_niigz = destination.suffixes == [".nii", ".gz"]
            is_func_bold = (dtype == "func" and "bold" in srcname)
            is_not_func = (dtype != "func")
            if is_niigz and (is_func_bold or is_not_func):
                dataset[dtype] = destination
            elif destination.suffix.endswith(".bvec"):
                dataset["bvec"] = destination
            elif destination.suffix.endswith(".bval"):
                dataset["bval"] = destination
            if isinstance(srcname, dict):
                with open(destination, "w") as of:
                    json.dump(srcname, of, indent=4)
            else:
                to_download.append((url, destination))

        for url, destination in to_download:
            if not destination.is_file():
                print_info(f"downloading: {url}")
                openneuro_download(url, destination)

        return dataset

    def sanity_check(
            self,
            subject: str,
            modality: str) -> None:
        """ Check that the fetch parameters are correct.

        Parameters
        ----------
        subject : str
            the subject identifier.
        modality : str
            the modality to be fetched.

        Raises
        ------
        ValueError
            If the fetch input parameters are not correct.
        """
        if modality not in self.allowed_modalities:
            raise ValueError("Unexpected modality.")
        if subject not in self.allowed_subjects:
            raise ValueError("Unexpected subject.")
