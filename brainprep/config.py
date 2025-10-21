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


DEFAULT_OPTIONS = {
    "verbose": True,
    "dryrun": False
}

brainprep_options = contextvars.ContextVar(
    "brainprep_options",
    default=DEFAULT_OPTIONS,
)


class Config:
    """
    Context manager for modifying options passed to the
    :mod:`~brainprep.interfaces` and :func:`~brainprep.reporting` modules
    when executing commands from decorated functions.

    Parameters
    ----------
    **options : dict
        Keyword arguments intercepted by the wrapper function:
        - verbose : bool, default True - print informations or not.
        - dryrun : bool, default False - execute commands or not

    Example
    -------
    >>> with Config(dryrun=True):
    ...     brainprep_deface('t1w.nii.gz', '/tmp')

    Notes
    -----
    - The context variable `brainprep_options` holds the current
      configuration.
    - Options are scoped to the `with` block and automatically restored
      afterward.
    """
    def __init__(self, **options):
        self.token = None
        self.options = options

    def __enter__(self):
        self.token = brainprep_options.set(self.options)

    def __exit__(self, exc_type, exc_val, exc_tb):
        brainprep_options.reset(self.token)
