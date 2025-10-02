##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements reporting tools.
"""

import base64
from pathlib import Path

import pandas as pd
from jinja2 import Environment, FileSystemLoader


def inject_with_jinja(
        template_file: Path,
        **kwargs) -> None:
    """ Render Jinja template given context and write it to an output file.

    Parameters
    ----------
    template_file: str
        Path to the Jinja template file.
    kwargs:
        The context to render the template.

    Returns
    -------
    render: str
        The HTML page
    """
    with template_file.open() as of:
        template_content = of.read()
    template = Environment(
        loader=FileSystemLoader(template_file.parent)
    ).from_string(template_content)
    return template.render(**kwargs)


def dataframe_to_html(
        df: pd.DataFrame,
        precision: int,
        **kwargs) -> str:
    """ Make HTML table from provided dataframe.

    Removes HTML5 non-compliant attributes (ex: `border`).

    Parameters
    ----------
    df: pandas.Dataframe
        Dataframe to be converted into HTML table.
    precision: int
        The display precision for float values in the table.
    **kwargs : keyworded arguments
        Supplies keyworded arguments for func: pandas.Dataframe.to_html()

    Returns
    -------
    html_table: str
        Code for HTML table.
    """
    with pd.option_context("display.precision", precision):
        html_table = df.to_html(**kwargs)
    html_table = html_table.replace('border="1" ', "")
    return html_table.replace('class="dataframe"', 'class="pure-table"')


def png_image_to_base64(
        image_path: Path) -> str:
    """Embed an image.

    Parameters
    ----------
    image_path: Path
        An image to display.

    Returns
    -------
    embed: str
        Binary image string.
    """
    assert image_path.suffix == ".png"
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string.decode()
