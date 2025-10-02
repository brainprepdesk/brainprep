##########################################################################
# NSAp - Copyright (C) CEA, 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Dataset tools.
"""

import shutil
from pathlib import Path

import requests


def git_download(
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
