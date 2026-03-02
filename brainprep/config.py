##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Configuration used by BrainPrep.
"""

import contextvars
from pathlib import Path

DEFAULT_OPTIONS = {
    "verbose": True,
    "dryrun": False,
    "no_color": False,
    "cat12_file": Path(
        "/opt/cat12/standalone/cat_standalone.sh"
    ),
    "spm12_dir": Path(
        "/opt/cat12"
    ),
    "matlab_dir": Path(
        "/opt/MCR-2017b/v93"
    ),
    "tpm_file": Path(
        "/opt/cat12/spm12_mcr/home/gaser/gaser/spm/spm12/tpm/TPM.nii"
    ),
    "darteltpm_file": Path(
        "/opt/cat12/spm12_mcr/home/gaser/gaser/spm/spm12/toolbox/"
        "cat12/templates_MNI152NLin2009cAsym/Template_1_Dartel.nii"
    ),
}

brainprep_options = contextvars.ContextVar(
    "brainprep_options",
    default=DEFAULT_OPTIONS,
)


class Config:
    """
    Context manager for modifying global execution options.

    This context manager allows temporary overrides of global options such as
    `verbose` and `dryrun`, which are commonly used across the `brainprep`
    package to control execution behavior. These options are primarily
    consumed by the :mod:`~brainprep.interfaces` and
    :func:`~brainprep.reporting` modules when executing commands from
    decorated functions.

    Additional options may be passed to workflows. These include
    resource-specific flags and configuration pre-configured to work with
    the associated container resource.

    Parameters
    ----------
    **options : dict
        Keyword arguments intercepted by the wrapper function:
        - verbose : bool, default True - print information or not.
        - dryrun : bool, default False - execute commands or not
        - with_color : bool, default True - print with colors or not.
        - cat12_file : File - path to the CAT12 standalone executable.
        - spm12_dir : Directory - path to the SPM12 standalone executable.
        - matlab_dir : Directory - path to the Matlab Compiler Runtime (MCR).
        - tpm_file : File - path to the SPM TPM file.
        - darteltpm_file : File - path to the CAT12 template file.

    Examples
    --------
    >>> from brainprep.config import Config
    >>> from brainprep.interfaces import movedir
    >>>
    >>> with Config(dryrun=True, verbose=False):
    ...     target_directory = movedir(
    ...         source_dir="/tmp/source_dir",
    ...         output_dir="/tmp/destination_dir",
    ...     )
    >>> target_directory
    PosixPath('/tmp/destination_dir/source_dir')

    Notes
    -----
    - The context variable `brainprep_options` holds the current
      configuration.
    - Options are scoped to the `with` block and automatically restored
      afterward.
    """

    def __init__(self, **options: dict):
        self.token = None
        self.options = options

    def __enter__(self):
        self.token = brainprep_options.set(self.options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        brainprep_options.reset(self.token)
