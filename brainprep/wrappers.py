##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Functions for running shell commands.
"""

import subprocess
import sys
from pathlib import Path
from typing import Any

from .typing import (
    File,
)
from .utils import (
    print_error,
    print_info,
    print_stdout,
)


def run_command(
        cmd: list[str]
    ) -> str:
    """
    Execute a command-line instruction and return its output.

    This function first verifies that the command exists on the system,
    then executes it while capturing both standard output and standard
    error. If the command exits with a non-zero return code, the captured
    output is displayed and a RuntimeError is raised.

    Parameters
    ----------
    cmd : list[str]
        The command to execute, provided as a list where the first element
        is the executable name and the remaining elements are arguments.

    Returns
    -------
    stdout : str
        The decoded standard output produced by the command.

    Raises
    ------
    RuntimeError
        If the command is not installed or if execution returns a
        non-zero exit code.
    """
    is_command_installed(cmd[0])

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    stdout_lines = []
    for line in iter(process.stdout.readline, ""):
        print_stdout(line)
        stdout_lines.append(line)
    process.stdout.close()
    stdout = "".join(stdout_lines)

    stderr = process.stderr.read()
    process.stderr.close()

    process.wait()

    if process.returncode != 0:
        print_error(stderr)
        raise RuntimeError(f"Command execution failed: {' '.join(cmd)}")

    return stdout


def is_list_str(
        command: Any) -> bool:
    """
    Check whether the input is a list containing only strings.

    Parameters
    ----------
    command : Any
        The object to validate.

    Returns
    -------
    bool
        True if `command` is a list and every element is a string,
        otherwise False.
    """
    return (isinstance(command, list) and
            all(isinstance(item, str) for item in command))


def is_list_list_str(
        command: Any
    ) -> bool:
    """
    Check whether the input is a list of lists containing only strings.

    Each element of `command` must itself be a list composed exclusively
    of string elements. This function delegates the inner-list validation
    to `is_list_str`.

    Parameters
    ----------
    command : Any
        The object to validate.

    Returns
    -------
    bool
        True if `command` is a list and every element is a list of
        strings, otherwise False.
    """
    return (isinstance(command, list) and
            all(is_list_str(item) for item in command))


def check_outputs(
        item: File | list[File] | tuple[File],
        dryrun: bool = False,
        verbose: bool = False
    ) -> None:
    """
    Recursively validates output file paths.

    Parameters
    ----------
    item : File | list[File] | tuple[File]
        A single file path or a collection of paths to validate.
    dryrun : bool
        If True, skips file existence checks. Default False.
    verbose : bool
        If True, prints each path being checked. Default False.

    Raises
    ------
    FileNotFoundError
        If `dryrun` is False and any specified path does not exist.
    ValueError
        If the input is neither a File nor a list/tuple of Files.
    """
    if isinstance(item, (list, tuple)):
        for subitem in item:
            check_outputs(subitem, dryrun, verbose)
    elif isinstance(item, (str, Path)):
        path = Path(item)
        print_info(f"checking output: {path}")
        if not dryrun and not path.exists():
            raise FileNotFoundError(
                f"Output file/directory not found: {path}"
            )
    elif item is None:
        return
    else:
        raise ValueError(
            "The outputs must be either a File or a list/tuple of Files."
        )


def is_command_installed(
        command: str
    ) -> None:
    """
    Verifies if a command is installed on a Linux system using the `which`
    utility.

    Parameters
    ----------
    command: str
        The name of the command to locate.

    Raises
    ------
    ValueError
        If the platform is not Linux or the command cannot be found.
    """
    if sys.platform != "linux":
        raise ValueError("This function is supported only on Linux systems.")

    process = subprocess.Popen(
        ["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print_info(stdout.decode("utf-8"))
        print_error(stderr.decode("utf-8"))
        raise ValueError(f"Unable to locate command: {command}")
