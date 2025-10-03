##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Provides signature-preserving function decorators in decorator factories.
"""

import datetime
import inspect
import platform
import textwrap
from pathlib import Path
from typing import Union

from decorator import decorator

from .._version import __version__
from ..utils import Bunch


class SingletonReport(type):
    """
    A metaclass that enforces the Singleton pattern with optional reloadable
    behavior.

    This metaclass ensures that only one instance of a class is created. If the
    `reloadable` keyword argument is passed and set to `True`, the internal
    reload counter is incremented and the instance is marked as reloadable.
    Otherwise, the instance is reset and its registry is cleared.

    Attributes
    ----------
    _instance : object or None
        The singleton instance of the class.
    _count : int
        Counter tracking how many times a reloadable instance has been
        requested.

    Parameters
    ----------
    reloadable : bool, optional
        If True, marks the instance as reloadable and increments the reload
        counter.
        If False or omitted, resets the reload counter and clears the registry.

    Returns
    -------
    object
        The singleton instance of the class.

    Examples
    --------
    >>> class Report(metaclass=SingletonReport):
    ...     def __init__(self):
    ...         self._registry = {}

    >>> r1 = Report()
    >>> r2 = Report()
    >>> r1 is r2
    True
    """
    _instance = None
    _count = 0

    def __call__(cls, *args, **kwargs):
        if kwargs.get("reloadable"):
            cls._count += 1
        else:
            cls._count = 0
        if cls._instance is None:
            cls._instance = super().__call__(
                *args, **kwargs
            )
        inst = cls._instance
        if kwargs.get("reloadable"):
            inst._reloadable = True
        else:
            inst._reloadable = False
        if "reloadable" not in kwargs or not kwargs["reloadable"]:
            inst._registry.clear()
        return inst


class RSTReport(metaclass=SingletonReport):
    """
    Render structured report content using reStructuredText (RST) format.

    This class collects and organizes data using `Bunch` objects and renders
    them as RST-formatted text. It supports registering multiple data entries
    under unique identifiers and exporting the report to a `.rst` file.

    The class uses a singleton pattern via `SingletonReport`, ensuring only one
    instance exists.

    Different renderings are possible:

    - print the object to get the Bunch content.
    - use :meth:`~brainprep.reporting.rst_reporting.RSTReport.save_as_rst` to
      save it as a rst file.

    To add a new data entry to the report under a given identifier and name
    use the :meth:`~brainprep.reporting.rst_reporting.RSTReport.register`
    method.

    Parameters
    ----------
    reloadable : bool, default False
        If False, the report content is automatically reset upon instantiation.

    Attributes
    ----------
    _registry : Bunch
        Internal storage for all registered report data.
    _reloadable : bool
        Indicates whether the report instance is reloadable.

    Notes
    -----
    Supported data types for registration include:
    - `str` for metadata fields "module" and "description".
    - `Bunch` for other structured data blocks.

    Examples
    --------
    >>> report = RSTReport()
    >>> report.register("step1", "module", "my_module.my_function")
    >>> report.register("step1", "description",
    ...                 "This function adds two numbers.")
    >>> report.register("step1", "inputs", Bunch(a=3, b=5))
    >>> print(report)
    Bunch(
      step1: Bunch(
        module: 'my_module.my_function'
        description: 'This function adds two numbers.'
        inputs: Bunch(
          a: 3
          b: 5
        )
      )
    )
    >>> report.save_as_rst("report.rst")
    """
    _registry = Bunch()

    def __init__(
            self,
            reloadable: bool = False) -> None:
        self._reloadable = reloadable

    def register(
            self,
            identifier: str,
            name: str,
            data: Union[str, Bunch]) -> None:
        """
        Add a new data entry to the report under a given identifier and name.

        Two data types are supported:
        - string for the 'module' and 'description' data elements.
        - :class:`~brainprep.utils.bunch.Bunch` otherwise.

        Parameters
        ----------
        identifier: str
            A unique data identifier.
        name: str
            A unique data element name.
        data: str or Bunch
            The data.

        Raises
        ------
        ValueError
            If duplicated name found or input data are invalid types.
        """
        if identifier not in self._registry:
            self._registry[identifier] = Bunch()
        if name in self._registry[identifier]:
            raise ValueError(
                "Duplicated name in registery."
            )
        if not (isinstance(data, Bunch) or
                (isinstance(data, str) and name in ("module", "description"))
                ):
            raise ValueError(
                "Registered data must be of type Bunch or str."
            )
        self._registry[identifier][name] = data

    def __str__(self):
        return repr(self._registry)

    def save_as_rst(
            self,
            file_name: str) -> None:
        """
        Save the report content to a reStructuredText (.rst) file.

        Parameters
        ----------
        file_name: str
            Path to the RST file used for saving.
        """
        report = ""
        for identifier, record in self._registry.items():
            module = record.get("module", "")
            description = record.get("description")
            title = f"{identifier.upper()}:{module}"
            report += f"{title}\n{'=' * len(title)}\n\n"
            if description is not None:
                report += f"{textwrap.dedent(description)}\n\n"
            for name, data in record.items():
                if name in ("module", "description"):
                    continue
                report += f"{name.title()}\n{'-' * len(name)}\n\n"
                for key, val in data.items():
                    report += f"* {key}: {val}\n"
                report += "\n"
        with Path(file_name).open("w") as of:
            of.write(report)


@decorator
def log_runtime(func, *args, **kw):
    """
    Decorator that logs runtime metadata and input/output details of a
    function call.

    This decorator uses an `RSTReport` instance to record metadata about the
    execution of the decorated function, including its module, docstring,
    inputs, outputs, and runtime statistics such as execution time and system
    information.

    Parameters
    ----------
    func : callable
        The function to be decorated.
    *args : tuple
        Positional arguments passed to `func`.
    **kw : dict
        Keyword arguments passed to `func`.

    Returns
    -------
    outputs : outputs
        The output returned by the decorated function.

    Notes
    -----
    - The report is created using `RSTReport(reloadable=True)`, which allows
      tracking multiple decorated steps.
    - Inputs are captured using `inspect.getcallargs`.
    - Runtime metadata includes start and end timestamps, execution duration
      in hours, platform details, and hostname.

    Examples
    --------
    >>> @log_runtime
    ... def add(a, b):
    ...     '''Adds two numbers.'''
    ...     return a + b

    >>> report = RSTReport()
    >>> result = add(3, 5)
    >>> print(report)
    Bunch(
      step1: Bunch(
        module: '__main__.add'
        description: 'Adds two numbers.'
        inputs: Bunch(
          a: 3
          b: 5
        )
        outputs: Bunch(
          outputs: 8
        )
        runtime: Bunch(
          start: '2025-10-03 15:12:55.428980'
          end: '2025-10-03 15:12:55.428980'
          execution_time: 3.611111111111111e-09
          brainprep_version: '1.0.0'
          platform: 'Linux'
          hostname: 'localhost'
        )
      )
    )
    """
    report = RSTReport(reloadable=True)
    identifier = f"step{RSTReport._count}"
    report.register(identifier, "module", f"{func.__module__}.{func.__name__}")
    report.register(identifier, "description", func.__doc__)
    inputs = Bunch(
        **inspect.getcallargs(func, *args, **kw)
    )
    report.register(identifier, "inputs", inputs)
    start = datetime.datetime.now()
    outputs = func(*args, **kw)
    if not isinstance(outputs, Bunch):
        outputs = Bunch(outputs=outputs)
    end = datetime.datetime.now()
    report.register(identifier, "outputs", outputs)
    runtime = Bunch(
        start=str(start),
        end=str(start),
        execution_time=(end - start).total_seconds() / 3600,
        brainprep_version=__version__,
        platform=platform.platform(),
        hostname=platform.node(),
    )
    report.register(identifier, "runtime", runtime)
    return outputs
