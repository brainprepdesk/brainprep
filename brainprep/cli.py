##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" Command-line interface (CLI) utilities for BrainPrep workflows.

This module provides a dynamic, Fire-powered command-line interface that
automatically exposes all BrainPrep workflows as CLI commands. It also
injects global configuration parameters into each workflow function
signature, enabling users to override default processing options directly
from the command line.
"""


import functools
import inspect
from collections.abc import Callable

import fire

import brainprep.workflow as wf
from brainprep.config import DEFAULT_OPTIONS


def make_wrapped(
        fn: Callable,
        is_vbm: bool = False) -> Callable:
    """
    Wrap a workflow function and extend its signature with global
    configuration parameters.

    This function creates a wrapper around a BrainPrep workflow function
    so that:

    - All original parameters of ``fn`` are preserved.
    - All global configuration parameters from ``DEFAULT_OPTIONS`` are
      added as keyword-only parameters.
    - Configuration parameters passed via the CLI are extracted from
      ``kwargs`` and applied through the ``Config`` context manager.
    - The modified signature is exposed to Fire, ensuring that the CLI
      help message displays the extended parameter list.

    Parameters
    ----------
    fn : Callable
        The workflow function to wrap. Its signature is inspected and
        extended with additional keyword-only configuration parameters.
    is_vbm : bool
       Whether the wrapped function corresponds to a VBM workflow.
       If ``False`` (default), VBM-specific configuration parameters
       such as ``cat12_file``, ``spm12_dir``, ``matlab_dir``,
       ``tpm_file``, and ``darteltpm_file`` are excluded from the
       generated signature. If ``True``, all configuration parameters
       are included. Default False.

    Returns
    -------
    method : Callable
        A wrapped version of ``fn`` whose signature includes both the
        original parameters and the global configuration parameters.

    Notes
    -----
    The wrapper inspects the signature of ``fn`` using
    ``inspect.signature`` and reconstructs a new signature that includes
    both workflow-specific and global configuration parameters. Each
    configuration parameter is annotated as ``"Context Manager"`` to
    indicate that it is handled by the ``Config`` system rather than
    passed directly to the workflow.
    During execution, configuration parameters are removed from
    ``kwargs`` and passed to the ``Config`` context manager. Remaining
    arguments are forwarded to the underlying workflow function.
    """
    @functools.wraps(fn)
    def wrapped_fn(*args, **kwargs):
        from brainprep.config import Config
        config_params = {
            key: kwargs.pop(key)
            for key in DEFAULT_OPTIONS
            if key in kwargs
        }
        with Config(**config_params):
            return fn(*args, **kwargs)

    sig = inspect.signature(fn)
    kwargs_in_keys = 'kwargs' in sig.parameters.keys()
    params = list(sig.parameters.values())
    for key, val in DEFAULT_OPTIONS.items():
        if not is_vbm and key in (
                "cat12_file", "spm12_dir", "matlab_dir", "tpm_file",
                "darteltpm_file"):
            continue
        param = inspect.Parameter(
            key,
            inspect.Parameter.KEYWORD_ONLY,
            annotation="Context Manager",
            default=val,
        )
        if kwargs_in_keys:
            params.insert(-1, param)
        else:
            params.append(param)
    wrapped_fn.__signature__ = sig.replace(parameters=params)

    return wrapped_fn


def main():
    """
    Entry point for the BrainPrep command-line interface.

    This function exposes all BrainPrep workflows as Fire commands.
    Each workflow is wrapped so that global configuration parameters can
    be passed directly from the command line.

    The CLI supports all workflows defined in ``brainprep.workflow`` and
    automatically displays them in the help message.

    Notes
    -----
    This function should not be called directly from Python code.

    Examples
    --------
    Listing available commands::

        $ brainprep --help

    Command help::

        $ brainprep subject-level-qa --help
    """
    commands = {
        "subject-level-qa": wf.brainprep_quality_assurance,
        "group-level-qa": wf.brainprep_group_quality_assurance,
        "subject-level-defacing": wf.brainprep_defacing,
        "group-level-defacing": wf.brainprep_group_defacing,
        "subject-level-quasiraw": wf.brainprep_quasiraw,
        "group-level-quasiraw": wf.brainprep_group_quasiraw,
        "subject-level-sbm": wf.brainprep_sbm,
        "longitudinal-sbm": wf.brainprep_longitudinal_sbm,
        "group-level-sbm": wf.brainprep_group_sbm,
        "subject-level-vbm": wf.brainprep_vbm,
        "longitudinal-vbm": wf.brainprep_longitudinal_vbm,
        "group-level-vbm": wf.brainprep_group_vbm,
        "subject-level-fmriprep": wf.brainprep_fmriprep,
        "group-level-fmriprep": wf.brainprep_group_fmriprep,
    }
    for key, fn in commands.items():
        commands[key] = make_wrapped(fn, is_vbm=key.endswith("vbm"))
    fire.Fire(commands)
