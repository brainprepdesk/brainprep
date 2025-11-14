##########################################################################
# NSAp - Copyright (C) CEA, 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Fetcher to download anatomical data.
"""

import gzip
import json
import os
import shutil
import tarfile
from pathlib import Path

import pandas as pd
import requests

from ..typing import (
    Directory,
)
from ..utils import (
    Bunch,
    print_info,
)


class MultiModalDataset:
    """
    Multi-modal dataset.

    This `dataset <https://www.nitrc.org/projects/multimodal>`_
    :footcite:p:`landman2011data` contains Magnetic Resonance (MR) images of
    21 healthy volunteers: scan-rescan imaging sessions including MPRAGE,
    FLAIR, DTI, resting state fMRI, B0 and B1 field maps, ...

    Attributes
    ----------
    datadir: Directory
        Directory where data will be stored.

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from pathlib import Path
    >>> from brainprep.datasets import MultiModalDataset
    >>>
    >>> datadir = Path("/tmp/brainprep-data")
    >>> datadir.mkdir(parents=True, exist_ok=True)
    >>> dataset = MultiModalDataset(datadir)
    >>> with Config(verbose=False):
    ...     data = dataset.fetch(
    ...         subject="01",
    ...         modality="func",
    ...         session="01",
    ...     )
    >>> data
    Bunch(
      description: PosixPath('...')
      anat: PosixPath('...')
      fmap1: PosixPath('...')
      fmap2: PosixPath('...')
      func: PosixPath('...')
    )

    Raises
    ------
    ValueError
        if an invalid session, modality or subject is passed to the
        :meth:`~brainprep.datasets.MultiModalDataset.fetch` method.

    References
    ----------

    .. footbibliography::
    """
    _url = "https://www.nitrc.org/frs/downloadlink.php/22{visit}"

    def __init__(
            self,
            datadir: Directory) -> None:
        """ Init class.
        """
        self.datadir = datadir
        self.allowed_subjects = [
            f"{str(subject).zfill(2)}" for subject in range(1, 22)
        ]
        self.allowed_modalities = [
            "func",
            "dwi",
        ]
        self.allowed_sessions = [
            "01",
            "02",
        ]
        self.meta = pd.read_csv(
            Path(__file__).parent.parent / "resources" / "kirby21.tsv",
            sep="\t",
        )
        self.meta["Subject"] = self.meta["Subject"].map(
            {
                val: str(idx + 1).zfill(2)
                for idx, val in enumerate(pd.unique(self.meta["Subject"]))
            }
        )
        self.meta["Visit"] = self.meta["Visit"].astype(str).apply(
            lambda x: x.zfill(2)
        )

    def fetch(
            self,
            subject: str,
            modality: str,
            session: str) -> Bunch:
        """ Fetch data.

        Parameters
        ----------
        subject: str
            Subject identifier: ['01' - '21'].
        modality: str
            Modality to be fetched: 'func' or 'dwi'.
        session: str
            Session: '01' or '02'.

        Returns
        -------
        dataset: Bunch
            Fetched data path. A 'description' entry is also available.
        """
        dataset = Bunch()
        self.sanity_check(subject, modality, session)

        description_file = (
            self.datadir /
            "rawdata" /
            "dataset_description.json"
        )
        if not description_file.is_file():
            description_file.parent.mkdir(parents=True, exist_ok=True)
            with open(description_file, "w") as of:
                description = {
                    "Name": "Example dataset",
                    "BIDSVersion": "1.0.2",
                }
                json.dump(description, of, indent=4)
        dataset["description"] = description_file

        selection = self.meta[self.meta["Subject"] == subject]
        visit = selection.iloc[int(session) - 1]["Visit"]
        url = self._url.format(
            visit=visit,
        )
        archive_file = (
                self.datadir /
                "sourcedata" /
                f"KKI2009-{visit}.tar.bz2"
        )
        if not archive_file.is_file():
            print_info(f"downloading: {url}")
            archive_file.parent.mkdir(parents=True, exist_ok=True)
            response = requests.get(url)
            response.raise_for_status()
            with open(archive_file, "wb") as of:
                of.write(response.content)

        to_extract = [
            ("anat", "T1w.nii", "MPRAGE.nii"),
            ("anat", "T1w.json", "MPRAGE.par"),
            ("fmap", "magnitude1.nii", "B08MS.nii"),
            ("fmap", "magnitude1.json", "B08MS.par"),
            ("fmap", "magnitude2.nii", "B09MS.nii"),
            ("fmap", "magnitude2.json", "B09MS.par"),
        ]
        if modality == "dwi":
            to_extract += [
                ("dwi", "dwi.nii", "DTI.nii"),
                ("dwi", "dwi.json", "DTI.par"),
                ("dwi", "dwi.bvec", "DTI.grad"),
                ("dwi", "dwi.bval", "DTI.b"),
            ]
        else:
            to_extract += [
                ("func", "task-rest_bold.nii", "fMRI.nii"),
                ("func", "task-rest_bold.json", "fMRI.par"),
            ]

        with tarfile.open(archive_file, "r:bz2") as tar:
            fmap_counter = 1
            for dtype, dest_suffix, src_suffix in to_extract:
                destination_file = (
                    self.datadir /
                    "rawdata" /
                    f"sub-{subject}" /
                    f"ses-{session}" /
                    dtype /
                    f"sub-{subject}_ses-{session}_{dest_suffix}"
                )
                if dest_suffix.endswith(".nii"):
                    if dtype == "fmap":
                        dtype = f"{dtype}{fmap_counter}"
                        fmap_counter += 1
                    dataset[dtype] = destination_file
                    if destination_file.with_suffix(".nii.gz").is_file():
                        continue
                elif dest_suffix.endswith((".bvec", ".bval")):
                    dataset[dest_suffix.split(".")[1]] = destination_file
                if destination_file.is_file():
                    continue
                destination_file.parent.mkdir(parents=True, exist_ok=True)
                file_to_extract = f"KKI2009-{visit}-{src_suffix}"
                print_info(f"extracting: {file_to_extract}")
                fileobj = tar.extractfile(file_to_extract)
                if fileobj is not None:
                    with open(destination_file, "wb") as of:
                        of.write(fileobj.read())
                else:
                    raise ValueError(
                        f"Could not extract '{file_to_extract}' from the "
                        "archive."
                    )

        for key, src_file in dataset.items():
            if src_file.suffix != ".nii":
                continue
            dest_file = src_file.with_suffix(".nii.gz")
            dataset[key] = dest_file
            if dest_file.is_file():
                continue
            with (open(src_file, "rb") as f_in,
                  gzip.open(dest_file, "wb") as f_out):
                shutil.copyfileobj(f_in, f_out)
            os.remove(src_file)

        return dataset

    def sanity_check(
            self,
            subject: str,
            modality: str,
            session: str) -> bool:
        """ Check that the fetch parameters are correct.

        Parameters
        ----------
        subject: str
            the subject identifier. This identifier must lie in ['01' - '30'],
            ['01' - '20'], for cross sectional or longitudinal data
            respectively.
        modality: str
            the modality to be fetched: 'dwi', or 'func'.
        session: str
            Session: '01' or '02'.

        Returns
        -------
        valid: bool
            the data integrity status.
        """
        if session not in self.allowed_sessions:
            raise ValueError(f"Unexpected session: {session}.")
        if modality not in self.allowed_modalities:
            raise ValueError(f"Unexpected modality: {modality}.")
        if subject not in self.allowed_subjects:
            raise ValueError(f"Unexpected subject: {subject}.")
