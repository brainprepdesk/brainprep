##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Module that contains some utility functions.
"""

import inspect
import json
import re
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import (
    Any,
    Union,
    get_args,
    get_origin,
)

from decorator import decorator

from .._version import __version__
from ..typing import (
    Directory,
    File,
)


@decorator
def bids(
        func: Callable,
        process: str | None = None,
        bids_file: File | Iterable[File] | None = None,
        container: str | None = None,
        add_subjects: bool = False,
        longitudinal: bool = False,
        *args: Any,
        **kw: Any) -> Callable:
    """
    BIDS specification.

    Decorator that computes a BIDS-compliant output directory path
    based on the input BIDS file and injects it into the function.

    Decorator that ensures BIDS-compliant metadata is written to the output
    directory.

    Parameters
    ----------
    func : Callable
        The function to be decorated.
    process : str | None
        Name of the processing pipeline (e.g., 'fmriprep', 'custom'). Default
        None.
    bids_file : File |Iterable[File] | None
        Name of the argument in the function that contains the BIDS file path.
        Default None.
    container : str | None
        The name of the container (e.g., Docker image) used to run the
        pipeline. Default None.
    add_subjects : bool
        If True, add a 'subjects' upper level directory in the output
        directory, for instance to regroup subject level data. Default False.
    longitudinal : bool
        If True, add a 'longitudinal' upper level directory in the output
        directory. Default False.
    *args : Any
        Positional arguments passed to `func`.
    **kw : Any
        Keyword arguments passed to `func`.

    Returns
    -------
    wrapper : Callable
        A wrapped function with computed 'output_dir' injected.

    Raises
    ------
    ValueError
        If the decorated function has no `bids_file` or 'output_dir'
        arguments.
    """
    inputs = inspect.getcallargs(func, *args, **kw)

    if process is None:
        return func(**inputs)

    subject_level = bids_file is not None
    output_dir = (
        Path(inputs["output_dir"]) /
        "derivatives" /
        process
    )
    if longitudinal:
        output_dir /= "longitudinal"
    if add_subjects:
        output_dir /= "subjects"
    if subject_level:
        for key in (bids_file, "output_dir"):
            if key not in inputs:
                raise ValueError(
                    f"The 'bids' decorator needs a '{key}' function argument."
                )
        if isinstance(inputs[bids_file], (list, tuple)):
            entities = parse_bids_keys(inputs[bids_file][0])
        else:
            entities = parse_bids_keys(inputs[bids_file])
        output_dir = (
            output_dir /
            f"sub-{entities['sub']}" /
            f"ses-{entities['ses']}"
        )
    metadata_file = (
        Path(inputs["output_dir"]) /
        "derivatives" /
        process /
        "dataset_description.json"
    )

    metadata_file.parent.mkdir(parents=True, exist_ok=True)
    inputs["output_dir"] = output_dir

    if not metadata_file.is_file():
        metadata = {
            "Name": f"{func.__module__}.{func.__name__}",
            "BIDSVersion": "1.8.0",
            "DatasetType": "derivative",
            "GeneratedBy": [
                {
                    "Name": "brainprep",
                    "Version": __version__,
                    "CodeURL": ("https://github.com/neurospin-deepinsight/"
                                "brainprep"),
                }
            ],
        }
        if container is not None:
            metadata["GeneratedBy"][0].update(
                {
                    "Container": {
                        "Type": "docker",
                        "Tag": f"{container}:{__version__}"
                      }
                }
            )
        with metadata_file.open("w", encoding="utf-8") as of:
            json.dump(metadata, of, indent=4)

    return func(**inputs)


@decorator
def outputdir(
        func: Callable,
        plotting: bool = False,
        *args: Any,
        **kw: Any) -> Callable:
    """
    Output directory creation.

    Decorator that create the output directory.

    Parameters
    ----------
    func : Callable
        The function to be decorated.
    plotting : bool
        If True, add a 'figures' upper level directory in the output
        directory. Default False.
    *args : Any
        Positional arguments passed to `func`.
    **kw : Any
        Keyword arguments passed to `func`.

    Returns
    -------
    wrapper : Callable
        A wrapped function with the 'output_dir' created on disk.

    Raises
    ------
    ValueError
        If the decorated function has no 'output_dir' argument.
    """
    inputs = inspect.getcallargs(func, *args, **kw)

    if "output_dir" not in inputs:
        raise ValueError(
            "The 'outputdir' decorator needs a 'output_dir' function argument."
        )

    if plotting:
        inputs["output_dir"] = (
            Path(inputs["output_dir"]) /
            "figures"
        )

    Path(inputs["output_dir"]).mkdir(parents=True, exist_ok=True)

    return func(**inputs)


@decorator
def coerceparams(
        func: Callable,
        *args: Any,
        **kw: Any) -> Callable:
    """
    Convert arguments annotated as ``File`` or ``Directory`` to
    ``pathlib.Path``, and convert arguments annotated as list types from
    comma‑separated strings into Python lists.

    Parameters
    ----------
    func : Callable
        The function to be decorated.
    *args : Any
        Positional arguments passed to ``func``.
    **kw : Any
        Keyword arguments passed to ``func``.

    Returns
    -------
    Callable
        A wrapped function in which arguments annotated as ``File`` or
        ``Directory`` are converted to ``pathlib.Path`` objects, and list‑typed
        arguments are coerced from comma‑separated strings into lists.

    Raises
    ------
    ValueError
        If the decorated function contains arguments without type annotations.
    """
    inputs = inspect.getcallargs(func, *args, **kw)
    sig = inspect.signature(func)

    for name, param in sig.parameters.items():
        if param.annotation is inspect.Parameter.empty:
            raise ValueError(
                "The decorated function must only have typed arguments."
            )
        inputs[name] = coerce_to_path(
            coerce_to_list(
                inputs[name],
                param.annotation,
            ),
            param.annotation,
        )

    return func(**inputs)


def coerce_to_list(
        value: Any,
        expected_type: type) -> Any:
    """
    Coerce a value into a list when the expected type annotation indicates
    a list or tuple.

    Parameters
    ----------
    value : Any
        The input value to be coerced.
    expected_type : type
        The expected type annotation (e.g., `File`, `List[File]`,
        `Dict[str, Directory]`, `Union[str, Directory]`).

    Returns
    -------
    typed_value : Any
        The coerced value, with `list` converted to `list`.

    Notes
    -----
    - Comma-separated strings (e.g., ``"a,b,c"``) are split into lists.
    - Single non-list values are wrapped into a list.
    - Existing lists or tuples are returned as lists.
    """
    if value is None:
        return value

    origin = get_origin(expected_type)

    if origin in {list, tuple}:
        if isinstance(value, str) and "," in value:
            return value.split(",")
        if not isinstance(value, (list, tuple)):
            return [value]
        return list(value)

    return value


def coerce_to_path(
        value: Any,
        expected_type: type) -> Any:
    """
    Recursively convert values to `pathlib.Path` based on expected type
    annotations.

    Parameters
    ----------
    value : Any
        The input value to be coerced.
    expected_type : type
        The expected type annotation (e.g., `File`, `List[File]`,
        `Dict[str, Directory]`, `Union[str, Directory]`).

    Returns
    -------
    typed_value : Any
        The coerced value, with `File` and `Directory` converted to
        `pathlib.Path`.
    """
    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if value is None:
        return value

    if expected_type in {File, Directory}:
        return Path(value).resolve()

    if origin is Union and (File in args or Directory in args):
        return Path(value).resolve()

    if origin in {list, tuple, set} and args:
        container_type = origin
        inner_type = args[0]
        return container_type(coerce_to_path(inner_value, inner_type)
                              for inner_value in value)

    if origin is dict and len(args) == 2:
        _, val_type = args
        return {key: coerce_to_path(val, val_type)
                for key, val in value.items()}

    return value


def parse_bids_keys(
        bids_path: File,
        full_path: bool = False) -> dict[str]:
    """
    Parses BIDS keys and modality from a filename or path with validation.

    Parameters
    ----------
    bids_path : File
        The BIDS file.
    full_path: bool
        Find the BIDS keys frol the full input path. Default False.

    Returns
    -------
    entities : dict[str]
        A dictionary of parsed BIDS entities including modality.
    """
    # Extract the filename from the path id necessary
    filename = str(bids_path) if full_path else bids_path.name

    # Regex pattern for BIDS entities
    entity_pattern = (
        r"(?P<entity>(sub|ses|task|acq|run|echo|rec|dir|mod|ce|part|space|res|"
        r"recording))"
        r"-(?P<value>[^_/]+)"
    )
    entities = {}
    for match in re.finditer(entity_pattern, filename):
        entity = match.group("entity")
        value = match.group("value")
        entities[entity] = value

    # Extract modality (suffix before extension)
    suffix_pattern = (
        r"_(?P<modality>[a-zA-Z0-9]+)(?=\.(nii|nii\.gz|json|tsv|edf|vhdr"
        r"|eeg|bvec|bval|csv))"
    )
    modality_match = re.search(suffix_pattern, filename)
    if modality_match:
        entities["modality"] = modality_match.group("modality")

    # Update modality
    if "mod" not in entities and "modality" in entities:
        entities["mod"] = entities["modality"]

    # Define default values for missing entities
    defaults = {
        "ses": "01",
        "run": "01",
    }

    # Fill in missing entities with defaults
    for key, default in defaults.items():
        entities.setdefault(key, default)

    return entities


def sidecar_from_file(
        image_file: File) -> File:
    """
    Infers the corresponding JSON sidecar file for a given NIfTI image file.

    This function checks that the input file has a `.nii.gz` extension and
    attempts to locate a sidecar `.json` file with the same base name. If
    either condition fails, it raises a ValueError.

    Parameters
    ----------
    image_file : File
        Path to the NIfTI image file with `.nii.gz` extension.

    Returns
    -------
    sidecar_file : File
        Path to the inferred JSON sidecar file.

    Raises
    ------
    ValueError
        If the input file does not have a `.nii.gz` extension or if the
        corresponding JSON sidecar file does not exist.

    Examples
    --------
    >>> from pathlib import Path
    >>> from brainprep.utils import sidecar_from_file
    >>>
    >>> image_file = Path("/tmp/sub-01_T1w.nii.gz")
    >>> sidecar_file = Path("/tmp/sub-01_T1w.json")
    >>> sidecar_file.touch()
    >>>
    >>> sidecar_from_file(image_file)
    PosixPath('/tmp/sub-01_T1w.json')
    """
    if not str(image_file).endswith(".nii.gz"):
        raise ValueError(
            f"Input image file must be in NIIGZ format: {image_file}"
        )
    sidecar_file = Path(str(image_file).replace(".nii.gz", ".json"))
    if not sidecar_file.is_file():
        raise ValueError(
            f"Sidecar inferred from input image file not found: {sidecar_file}"
        )
    return sidecar_file


def find_stack_level() -> int:
    """
    Find the first place in the stack that is not inside brainprep.
    Taken from the pandas codebase.
    """
    import brainprep

    pkg_dir = Path(brainprep.__file__).parent

    # https://stackoverflow.com/questions/17407119/python-inspect-stack-is-slow
    frame = inspect.currentframe()
    try:
        n = 0
        while frame:
            filename = inspect.getfile(frame)
            is_test_file = Path(filename).name.startswith("test_")
            in_nilearn_code = filename.startswith(str(pkg_dir))
            if not in_nilearn_code or is_test_file:
                break
            frame = frame.f_back
            n += 1
    finally:
        # See note in
        # https://docs.python.org/3/library/inspect.html#inspect.Traceback
        del frame
    return n
