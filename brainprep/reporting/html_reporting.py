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
from typing import Self

from .utils import (
    dataframe_to_html,
    inject_with_jinja,
    png_image_to_base64,
)


class HTMLReport:
    """
    Render and manage HTML content for display in web pages or Jupyter
    notebooks.

    This class encapsulates HTML content and provides utilities for rendering
    it inline (e.g., in Jupyter), resizing the display area, and exporting to
    an HTML file.
    It supports iframe embedding and integrates with notebook display
    protocols.

    The different rendering are available as follows:

    - print the object to get the content of the web page.
    - from a Jupyter notebook, the plot will be displayed inline if this object
      is the output of a cell.
    - use :meth:`~brainprep.reporting.html_reporting.HTMLReport.save_as_html`
      to save it as an html file.
    - use :meth:`~brainprep.reporting.html_reporting.HTMLReport.get_iframe`
      to have it wrapped in an iframe.

    Parameters
    ----------
    html : str
        The HTML content to be rendered.
    width : int
        Width of the display area in pixels. Default 800.
    height : int
        Height of the display area in pixels. Default 800.

    Examples
    --------
    >>> html = "<h1>Hello, world!</h1>"
    >>> report = HTMLReport(html)
    >>> print(report)
    <h1>Hello, world!</h1>
    >>> report.save_as_html("/tmp/output.html")
    """

    def __init__(
            self,
            html: str,
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
        """
        Resize the document displayed.

        Parameters
        ----------
        width: int
            New width of the document.
        height: int
            New height of the document.

        Returns
        -------
        Self
        """
        self.width = width
        self.height = height
        return self

    def get_iframe(
            self,
            width: int | None,
            height: int | None) -> str:
        """
        Get the document wrapped in an inline frame.

        Parameters
        ----------
        width: int | None
            Width of the inline frame. Default None.
        height: int | None
            Height of the inline frame. Default None.

        Returns
        -------
        wrapped: str
            Raw HTML code for the inline frame.

        Notes
        -----
        Useful for inserting the document content in another HTML page,
        i.e. in a Jupyter notebook.
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

    def _repr_html_(self) -> str:
        """
         Return iframe-wrapped HTML for Jupyter notebook rendering.

        Notes
        -----
        Used by the Jupyter notebook.
        See the jupyter documentation:
        https://ipython.readthedocs.io/en/stable/config/integrating.html
        """
        return self.get_iframe()

    def _repr_mimebundle_(
            self,
            include=None,
            exclude=None) -> dict:
        """
        Return html representation of the plot.

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
        """
        Save the plot in an HTML file, that can later be opened in a browser.

        Parameters
        ----------
        file_name: str
            Path to the HTML file used for saving.
        """
        Path(file_name).write_bytes(self.html.encode("utf-8"))


def generate_qc_report(
        title: str,
        docstring: str,
        version: str,
        date: str,
        data: list[dict]) -> HTMLReport:
    """
    Generate a quality control (QC) report as an interactive HTML document.

    This function compiles visual and tabular data into a structured HTML
    report using a predefined template. It is useful for documenting and
    reviewing steps in a data processing workflow.

    Parameters
    ----------
    title : str
        The title displayed at the top of the report.
    docstring : str
        A descriptive introduction or summary of the report's purpose.
    version : str
        Version identifier for the report or associated software.
    date : str
        Timestamp indicating when the report was generated.
    data : list[dict]
        A list of dictionaries, each representing a workflow step. Each
        dictionary must contain the following keys:
        - name (str): Title of the step.
        - content (Path or list of Path): Image(s) to display.
        - overlay (Path): Image(s) to show on hover.
        - tables (DataFrame or list of DataFrame): Tabular data to include.

    Returns
    -------
    report : HTMLReport
        An instance of `HTMLReport` containing the rendered HTML content.

    Notes
    -----
    - Images are converted to base64 for inline embedding.
    - Tables are rendered as HTML using `dataframe_to_html`.

    Examples
    --------
    >>> from pathlib import Path
    >>> from pandas import DataFrame
    >>>
    >>> data = [{
    ...     "name": "Step 1",
    ...     "content": Path("/tmp/image1.png"),
    ...     "overlay": Path("/tmp/image1_overlay.png"),
    ...     "tables": DataFrame({"A": [1, 2], "B": [3, 4]})
    ... }]
    >>> report = generate_qc_report(
    ...     title="QC Summary",
    ...     docstring="Overview of preprocessing steps.",
    ...     version="1.0",
    ...     date="2025-10-03",
    ...     data=data
    ... ) # doctest: +SKIP
    >>> report.save_as_html("/tmp/qc_report.html") # doctest: +SKIP
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
