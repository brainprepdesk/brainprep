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
from collections.abc import Callable
from pathlib import Path
from typing import (
    Any,
    Self,
)

from decorator import decorator

from .._version import __version__
from ..config import (
    DEFAULT_OPTIONS,
    brainprep_options,
)
from ..typing import (
    File,
)
from ..utils import (
    Bunch,
    print_title,
)


class SingletonReport(type):
    """
    A metaclass that enforces the Singleton pattern with optional reloadable
    behavior.

    This metaclass ensures that only one instance of a class is created. If the
    `reloadable` keyword argument is passed and set to `True`, the internal
    reload counter is incremented and the instance is marked as reloadable.
    Otherwise, the instance is reset and its registry is cleared.

    Parameters
    ----------
    cls : type[SingletonReport]
        The class being instantiated with this metaclass.
    *args : Any
        Positional arguments forwarded to the class constructor.
    **kwargs : Any
        Keyword arguments forwarded to the class constructor. May include
        `reloadable` to control singleton reload behavior and `increment`
        to control if we need to increment the inner counter.

    Attributes
    ----------
    _instance : Self | None
        The singleton instance of the class.

    Returns
    -------
    Self
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

    _instance: Self | None = None

    def __call__(
            cls: type[Self],
            *args: Any,
            **kwargs: Any) -> Self:
        """
        Return the singleton instance of `SingletonReport`.

        Parameters
        ----------
        *args : Any
            Positional arguments passed to the singleton initializer.
        **kwargs : Any
            Keyword arguments passed to the singleton initializer.

        Returns
        -------
        Self
            The unique singleton instance.
        """
        is_reloadable = kwargs.get("reloadable", False)
        is_increment = kwargs.get("increment", False)
        if cls._instance is None:
            cls._instance = super().__call__(
                *args, **kwargs
            )
        inst = cls._instance
        if not is_reloadable:
            inst._count = 0
            inst._registry.clear()
        if is_increment:
            inst._count += 1
        inst._reloadable = is_reloadable
        inst._increment = is_increment
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
    reloadable : bool
        If False, the report content is automatically reset upon instantiation.
        Default False.
    increment : bool
        If False, the inner step counter is not incremented upon instantiation.
        Default False.

    Attributes
    ----------
    _registry : Bunch
        Internal storage for all registered report data.
    _str_fields : tuple[str]
        Allowed string fields.

    Notes
    -----
    Supported data types for registration include:
    - `str` for metadata fields "module" "trace" and "description".
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

    _registry: Bunch = Bunch()
    _str_fields: tuple[str] = ("module", "trace", "description")

    def __init__(
            self,
            reloadable: bool = False,
            increment: bool = False) -> None:
        self._reloadable = reloadable
        self._increment = increment
        self._count = 0

    def register(
            self,
            identifier: str,
            name: str,
            data: str | Bunch) -> None:
        """
        Add a new data entry to the report under a given identifier and name.

        Two data types are supported:
        - string for the 'module', 'trace' and 'description' data elements.
        - :class:`~brainprep.utils.bunch.Bunch` otherwise.

        Parameters
        ----------
        identifier: str
            A unique data identifier.
        name: str
            A unique data element name.
        data: str | Bunch
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
                "Duplicated name in registry."
            )
        if not (isinstance(data, Bunch) or
                (isinstance(data, str) and name in self._str_fields)
                ):
            raise ValueError(
                "Registered data must be of type Bunch or str."
            )
        self._registry[identifier][name] = data

    def __str__(self):
        return repr(self._registry)

    def save_as_rst(
            self,
            file_name: File) -> None:
        """
        Save the report content to a reStructuredText (.rst) file.

        Parameters
        ----------
        file_name: File
            Path to the RST file used for saving.
        """
        report = ""
        for identifier, record in self._registry.items():
            module = record.get("module", "")
            description = record.get("description")
            trace = record.get("trace")
            title = f"{identifier.upper()}: {module}"
            report += f"\n\n{title}\n{'=' * len(title)}\n\n"
            if description is not None:
                report += f"{textwrap.dedent(description)}\n\n"
            if trace is not None:
                report += f"Depends on: {trace}\n\n"
            for name, data in record.items():
                if name in self._str_fields:
                    continue
                report += f"{name.title()}\n{'-' * len(name)}\n\n"
                for key, val in data.items():
                    report += f"* {key}: {val}\n"
                report += "\n"
        with Path(file_name).open("w") as of:
            of.write(report)


@decorator
def log_runtime(
        func: Callable,
        title: str | None = None,
        bunched: bool = True,
        *args: Any,
        **kw: Any) -> Any:
    """
    Decorator that logs runtime metadata and input/output details of a
    function call.

    This decorator uses an `RSTReport` instance to record metadata about the
    execution of the decorated function, including its module, docstring,
    inputs, outputs, and runtime statistics such as execution time and system
    information.

    Parameters
    ----------
    func : Callable
        The function to be decorated.
    title : str | None
        A title to display. Default None.
    bunched : bool
        Return a bunch object with a default 'outputs' key. Default True.
    *args : Any
        Positional arguments passed to `func`.
    **kw : Any
        Keyword arguments passed to `func`. If a `report_file` keyword argument
        is passed, the logged runtime metada are saved in this file.

    Returns
    -------
    outputs : Any
        The output returned by the decorated function.

    Notes
    -----
    - The report is created using `RSTReport(reloadable=True)`, which allows
      tracking multiple decorated steps.
    - Inputs are captured using `inspect.getcallargs`.
    - Runtime metadata includes start and end timestamps, execution duration
      in hours, platform details, and hostname.
    - Current configuration is captured.

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
    if title is not None:
        print_title(f"{title}...")
    trace = trace_module_calls()
    report = RSTReport(
        reloadable=True,
        increment=True,
    )
    identifier = f"step{report._count}"
    report.register(identifier, "module", f"{func.__module__}.{func.__name__}")
    report.register(identifier, "description", func.__doc__)
    if trace:
        report.register(identifier, "trace", trace)
    inputs = Bunch(
        **inspect.getcallargs(func, *args, **kw)
    )
    report.register(identifier, "inputs", inputs)
    start = datetime.datetime.now()
    outputs = func(*args, **kw)
    _outputs = (
        Bunch(outputs=outputs)
        if not isinstance(outputs, Bunch)
        else outputs
    )
    end = datetime.datetime.now()
    report.register(identifier, "outputs", _outputs)
    if bunched:
        outputs = _outputs
    runtime = Bunch(
        start=str(start),
        end=str(start),
        execution_time=(end - start).total_seconds() / 3600,
        brainprep_version=__version__,
        platform=platform.platform(),
        hostname=platform.node(),
    )
    report.register(identifier, "runtime", runtime)
    config = Bunch(**DEFAULT_OPTIONS.copy())
    config.update(
        brainprep_options.get()
    )
    report.register(identifier, "config", config)
    if title is not None:
        print_title(f"{title} done.")
    return outputs


@decorator
def save_runtime(
        func: Callable,
        parent: bool = False,
        *args: Any,
        **kw: Any) -> Any:
    """
    Decorator that save logged runtime metadata in a 'output_dir/logs' folder.

    Parameters
    ----------
    func : Callable
        The function to be decorated.
    parent : bool
        If True, logs will be saved in the parent output directory instead of
        the output directory. This is useful when centralizing log files.
        Default False.
    *args : Any
        Positional arguments passed to `func`.
    **kw : Any
        Keyword arguments passed to `func`. An `output_dir` keyword argument
        is expected.

    Returns
    -------
    outputs : Any
        The output returned by the decorated function.

    Examples
    --------
    >>> @log_runtime
    ... @save_runtime
    ... def add(a, b, output_dir="/tmp"):
    ...     '''Adds two numbers.'''
    ...     return a + b
    >>> result = add(3, 5)

    Raises
    ------
    ValueError
        If the `output_dir` keyword argument is not defined.
    """
    inputs = inspect.getcallargs(func, *args, **kw)
    if "output_dir" not in inputs:
        raise ValueError(
            "This decorator needs an 'output_dir' function argument."
        )
    report = RSTReport(reloadable=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if parent:
        report_file = (
            Path(inputs.get("output_dir")).parent /
            "logs" /
            f"report_{timestamp}.rst"
        )
    else:
        report_file = (
            Path(inputs.get("output_dir")) /
            "logs" /
            f"report_{timestamp}.rst"
        )
    report_file.parent.mkdir(parents=True, exist_ok=True)
    outputs = func(*args, **kw)
    report.save_as_rst(report_file)
    return outputs


def trace_module_calls(
        root_module_names: tuple[str] = ("workflow", "interfaces")) -> str:
    """
    Return the trace of function calls from the specified module and
    its submodules.

    This function walks through the current call stack and filters out
    frames whose module name starts with the given root module names.

    Parameters
    ----------
    root_module_names : tuple[str]
        The root module name to filter by (e.g., 'interfaces').
        All submodules like 'brainprep.interfaces.submodule' will be included.
        Default ('workflow', 'interfaces').

    Returns
    -------
    trace: str
        A string representing the chain of function calls from the specified
        modules, joined by '->'.

    Notes
    -----
    This uses the module name from the frame's global context, which is more
    reliable than filenames when working with packages.
    """
    trace = []
    stack = inspect.stack()
    names = [f"brainprep.{mod}" for mod in root_module_names]
    for frame_info in reversed(stack):
        module_name = frame_info.frame.f_globals.get("__name__", "")
        if module_name.startswith(tuple(names)):
            trace.append(f"{module_name}.{frame_info.function}")
    return "->".join(trace)
