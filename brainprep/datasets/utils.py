##########################################################################
# NSAp - Copyright (C) CEA, 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Dataset creation tools.
"""

from pathlib import Path

import requests


def git_download(
        url: str,
        destination: Path) -> None:
    """
    Download data from GitHub URL and saves it locally.

    Parameters
    ----------
    url: str
        Direct URL to the raw data file on GitHub.
    destination: Path
        Path to the saved data file.

    Raises
    ------
    ValueError
        If the URL does not point to 'raw.githubusercontent.com'.
    """
    # Ensure it's a raw GitHub URL
    if "raw.githubusercontent.com" not in url:
        raise ValueError(
            f"URL '{url}' does not point to 'raw.githubusercontent.com'."
        )

    # Download the data
    response = requests.get(url)
    response.raise_for_status()

    # Save the data
    with destination.open("wb") as of:
        of.write(response.content)
    del response
