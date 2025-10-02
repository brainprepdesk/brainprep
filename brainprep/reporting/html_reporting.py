##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that implements a HTML reporting tool.
"""

import uuid
from html import escape
from pathlib import Path
from typing import Optional, Self

from .utils import (
    dataframe_to_html,
    inject_with_jinja,
    png_image_to_base64,
)


def generate_qc_report(title, docstring, version, date, data):
    """ Generate a QC report.

    Reports are useful to visualize steps in a processing workflow.

    Parameters
    ----------
    title: str
        The report title.
    docstring: str
        The introductory docstring for the reported object.
    version: str
        A version.
    date: str
        A timestamp.
    data: dict
        A dictionary holding the data to be added to the report.
        The keys must match exactly the ones used in the template:
            - name (str): a title.
            - content (str or list of str): an image or a list of images.
            - overlay (str): overlaid iamge, to appear on hover.
            - tables: (DataFrame or list of FataFrame): tables.

    Returns
    -------
    report: HTMLReport
        An instance of a populated HTML report.
    """
    template_path = Path(__file__).parent / "data" / "body.html"
    css_path = Path(__file__).parent / "data" / "style.css"
    with css_path.open(encoding="utf-8") as css_file:
        css = css_file.read()
    js_path = Path(__file__).parent / "data" / "script.js"
    with js_path.open(encoding="utf-8") as js_file:
        js = js_file.read()
    unique_id = str(uuid.uuid4()).replace("-", "")
    for counter, item in enumerate(data):
        item["id"] = counter
        content = item.get("content")
        overlay = item.get("overlay")
        tables = item.get("tables")
        if content is not None:
            if not isinstance(content, (tuple, list)):
                content = [content]
            item["content"] = [
                png_image_to_base64(img) for img in content
            ]
        if overlay is not None:
            if not isinstance(overlay, (tuple, list)):
                overlay = [overlay]
            item["overlay"] = [
                png_image_to_base64(img) for img in overlay
            ]
        if tables is not None:
            if not isinstance(tables, (tuple, list)):
                tables = [tables]
            item["tables"] = [
                dataframe_to_html(
                    tab,
                    precision=2,
                    header=True,
                    index=False,
                    sparsify=False,
                ) for tab in tables
            ]
    html = inject_with_jinja(
        template_file=template_path,
        css=css,
        js=js,
        uuid=unique_id,
        title=title,
        docstring=docstring,
        version=version,
        date=date,
        workflows=data,
    )
    html = html.replace(".pure-g &gt; div", ".pure-g > div")

    return HTMLReport(html=html)


class HTMLReport:
    """ Render HTML content in a web page.

    Different rendering are possible:
    - print the object to get the content of the web page.
    - from a Jupyter notebook, the plot will be displayed inline if this object
      is the output of a cell.
    - use :meth:`~brainprep.reporting.HTMLDocument.save_as_html` to save it as
      an html file.
    - use :meth:`~brainprep.reporting.HTMLDocument.get_iframe` to have it
      wrapped in an iframe

    Parameters
    ----------
    html: str
        The page content.
    width: int, defaut 800
        Width of the document.
    height: int, defaut 800
        Height of the document.
    """
    def __init__(
            self,
            html,
            width: int = 800,
            height: int = 800) -> None:
        self.html = html
        self.width = width
        self.height = height
        self._temp_file = None
        self._temp_file_removing_proc = None

    def resize(
            self,
            width: int,
            height: int) -> Self:
        """ Resize the document displayed.

        Parameters
        ----------
        width: int
            New width of the document.
        height: int
            New height of the document.

        Returns
        -------
        self
        """
        self.width = width
        self.height = height
        return self

    def get_iframe(
            self,
            width: Optional[int] = None,
            height: Optional[int] = None) -> str:
        """ Get the document wrapped in an inline frame.

        Notes
        -----
        Usueful for inserting the document content in another HTML page,
        i.e. in a Jupyter notebook.

        Parameters
        ----------
        width: int, default None
            Width of the inline frame.
        height: int, default None
            Height of the inline frame.

        Returns
        -------
        wrapped: str
            Raw HTML code for the inline frame.
        """
        if width is None:
            width = self.width
        if height is None:
            height = self.height
        escaped = escape(self.html, quote=True)
        wrapped = (
            f"<iframe srcdoc='{escaped}' "
            f"width='{width}' height='{height}' "
            "frameBorder='0'></iframe>"
        )
        return wrapped

    def _repr_html_(self):
        """ Return html representation of the plot.

        Notes
        -----
        Used by the Jupyter notebook.
        See the jupyter documentation:
        https://ipython.readthedocs.io/en/stable/config/integrating.html
        """
        return self.get_iframe()

    def _repr_mimebundle_(self, include=None, exclude=None):
        """ Return html representation of the plot.

        Notes
        -----
        Used by the Jupyter notebook.
        See the jupyter documentation:
        https://ipython.readthedocs.io/en/stable/config/integrating.html
        """
        del include, exclude
        return {"text/html": self.get_iframe()}

    def __str__(self):
        return self.html

    def save_as_html(
            self,
            file_name: str) -> None:
        """ Save the plot in an HTML file, that can later be opened
        in a browser.

        Parameters
        ----------
        file_name: str
            Path to the HTML file used for saving.
        """
        with Path(file_name).open("wb") as of:
            of.write(self.html.encode("utf-8"))
