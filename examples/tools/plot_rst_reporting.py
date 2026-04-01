"""
RST reporting
=============

Simple example.

Example on how to accumulate runtime information in an RST report.
See :ref:`user guide <reporting>` for details.

Functions
---------

Let's create some functions to monitor.
"""

from brainprep.decorators import (
    LogRuntimeHook,
    step,
)
from brainprep.utils import Bunch


@step(
    hooks=[LogRuntimeHook()]
)
def workflow(val1, val2=None):
    """
    This is the main workflow.

    Parameters
    ----------
    val1: int
        a value.
    val2: int, default None
        an optional value.

    Returns
    -------
    val: int
        a value.
    """
    if val2 is not None:
        return Bunch(val=val1 * square(val2).val2)
    else:
        return Bunch(val=val1)


@step(
    hooks=[LogRuntimeHook()]
)
def square(val):
    """
    Return the square of the input.

    Parameters
    ----------
    val: int
        a value.

    Returns
    -------
    val2: int
        the value squared.
    """
    return Bunch(val2=val ** 2)


# %%
# Reporting
# ---------
# 
# Now let's generate the RST report.

from pathlib import Path

from brainprep.reporting import RSTReport

working_dir = Path("/tmp/brainprep-reporting")
working_dir.mkdir(parents=True, exist_ok=True)

report = RSTReport()
print(workflow(val1=1))
print(report)
report = RSTReport()
print(workflow(val1=1, val2=2))
print(report)
report.save_as_rst(working_dir / "report.rst")
