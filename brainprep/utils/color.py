##########################################################################
# Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Utility methods to print the results in a terminal using term colors.
"""

from rich.console import Console
from rich.text import Text

from ..config import (
    DEFAULT_OPTIONS,
    brainprep_options,
)

fg_colors = {
    "title": "yellow",
    "subtitle": "cyan",
    "command": "grey53",
    "info": "blue",
    "result": "pink3",
    "error": "red",
    "warn": "dark_orange3",
    "deprecated": "dark_orange3",
}


def print_color(category: str, text: str) -> None:
    """ Print text.

    Parameters
    ----------
    category: str
        a category to select the preconfigured color.
    text: str
        text to print.

    Raises
    ------
    ValueError
        If an invalid category is used.
    """
    console = Console()
    opts = brainprep_options.get()
    verbose = opts.get("verbose", DEFAULT_OPTIONS["verbose"])
    with_color = not opts.get("no_color", DEFAULT_OPTIONS["no_color"])

    if category != "deprecated" and not verbose:
        return

    if category not in fg_colors:
        raise ValueError(
            f"Please define an entry for '{category}' in the color table."
        )

    style = fg_colors[category] if with_color else None
    tag = Text(category, style=style)
    line = Text.assemble("[", tag, "] - ", text)
    console.print(line)


def print_title(title: str) -> None:
    """ Print title.

    Parameters
    ----------
    title: str
        text to print.
    """
    print_color("title", title)


def print_subtitle(subtitle: str) -> None:
    """ Print subtitle.

    Parameters
    ----------
    subtitle: str
        text to print.
    """
    print_color("subtitle", subtitle)


def print_command(command: str) -> None:
    """ Print command.

    Parameters
    ----------
    command: str
        text to print.
    """
    print_color("command", command)


def print_info(info: str) -> None:
    """ Print info.

    Parameters
    ----------
    info: str
        text to print.
    """
    print_color("info", info)


def print_warn(warn: str) -> None:
    """ Print warn.

    Parameters
    ----------
    warn: str
        text to print.
    """
    print_color("warn", warn)


def print_result(result: str) -> None:
    """ Print result.

    Parameters
    ----------
    result: str
        text to print.
    """
    print_color("result", result)


def print_error(error: str) -> None:
    """ Print error.

    Parameters
    ----------
    error: str
        text to print.
    """
    print_color("error", error)


def print_deprecated(deprecated: str) -> None:
    """ Print deprecated.

    Parameters
    ----------
    deprecated: str
        text to print.
    """
    print_color("deprecated", deprecated)
