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
import os
import re
import uuid
from pathlib import Path
from typing import (
    Any,
    Union,
    get_args,
    get_origin,
)

import nibabel as nib
import numpy as np

from ..config import (
    DEFAULT_OPTIONS,
    brainprep_options,
)
from ..typing import (
    Directory,
    File,
)
from .color import (
    print_warn,
)


def coerce_to_list(
        value: Any,
        expected_type: type,
    ) -> Any:
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
        expected_type: type,
    ) -> Any:
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
        full_path: bool = False,
        check_run: bool = False,
    ) -> dict[str]:
    """
    Parse BIDS entities and modality from a filename or path with validation.

    This function extracts BIDS entities (e.g., subject, session, task,
    run) from a BIDS-compliant filename or full path. It also identifies the
    modality and applies default values when certain entities are missing.

    When the `ses` entity is absent, it defaults to "01". This provides ensures
    consistent downstream file handling.

    When the `run` entity is absent, a deterministic 5-digit identifier is
    generated from the filename using UUID. This produces a short, stable
    hash so that the same filename always yields the same default run value.

    Parameters
    ----------
    bids_path : File
        The BIDS file to parse.
    full_path: bool
        If True, extract entities from the full input path rather than
        only the filename.
        Default False.
    check_run: bool
        If True, checks whether the current run value appears more
        than once, assigns a UUID-style fallback if needed, and warns if even
        that fallback is not unique.
        Default False.

    Returns
    -------
    entities : dict[str]
        A dictionary containing the parsed BIDS entities and the detected
        modality. Missing entities such as `ses` and `run` are filled with
        default values.

    Notes
    -----
    If the BIDS file name does not contain the `run` key a warn message is
    displayed.
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
        r"|eeg|bvec|bval|csv|mat|xml))"
    )
    modality_match = re.search(suffix_pattern, filename)
    if modality_match:
        entities["modality"] = modality_match.group("modality")

    # Update modality
    if "mod" not in entities and "modality" in entities:
        entities["mod"] = entities["modality"]

    # Define default values for missing entities
    run_in_entities = "run" in entities
    if not run_in_entities:
        print_warn(
            f"BIDS file name does not contain run key: {filename}"
        )
    defaults = {
        "ses": "01",
        "run": make_run_id(filename)[1],
    }

    # Fill in missing entities with defaults
    for key, default in defaults.items():
        entities.setdefault(key, default)

    # Check integrity
    opts = brainprep_options.get()
    check_run = (
        check_run and
        not opts.get("skip_run_check", DEFAULT_OPTIONS["skip_run_check"])
    )
    if check_run:
        status = check_run_fn(bids_path, entities, full_path)
        if run_in_entities and not status:
            print_warn(
                "Multiple files with same run ID detected, using UUID instead."
            )
            entities["run"] = defaults["run"]
            status = check_run_fn(bids_path, entities, full_path)
        if not status:
            print_warn(
                f"The generated UUID is not unique: {bids_path}"
            )

    return entities


def check_run_fn(
        bids_path: File,
        entities: dict[str],
        full_path: bool = False,
    ) -> bool:
    """
    Scan the folder containing a BIDS file and verify that the run entity
    associated with the file appears exactly once among all matching files.

    Parameters
    ----------
    bids_path : File
        A BIDS file.
    entities : dict[str]
        Dictionary of parsed BIDS entities for the file, including the
        modality.
    full_path : bool
        If True, extract entities from the full path instead of only the
        filename.
        Default False.

    Returns
    -------
    bool
        True if the run identifier occurs exactly once among all matching
        files in the folder (or zero for virtual data), False otherwise.
    """
    filename = str(bids_path) if full_path else bids_path.name
    ext = "".join(bids_path.suffixes)
    entity_pattern = (
        r"(?P<entity>(run))"
        r"-(?P<value>[^_/]+)"
    )
    pattern = f"*sub-*{entities['modality']}*{ext}"

    all_entities = []
    for bids_path_ in bids_path.parent.glob(pattern):
        filename_ = str(bids_path_) if full_path else bids_path_.name
        entities_ = {"filename": filename_}

        # Extract run entity if present
        for match in re.finditer(entity_pattern, str(bids_path_)):
            entity = match.group("entity")
            value = match.group("value")
            entities_[entity] = value

        # If run is missing, generate one
        if "run" not in entities_:
            entities_["run"] = make_run_id(filename)[1]

        all_entities.append(entities_)

    # Count how many times the current file's run appears
    all_run_ids = [item["run"] for item in all_entities]
    count = all_run_ids.count(entities["run"])

    return count in (0, 1)


def make_run_id(
        filename: str,
    ) -> tuple[str, str]:
    """
    Generate a deterministic identifier and a 5-digit short code from a
    filename.

    This function computes a UUIDv5 using the URL namespace and the provided
    filename, converts the UUID to its integer representation, and returns both
    the full integer-based code and its first five digits. The result is stable
    and reproducible: the same filename always produces the same values.

    Parameters
    ----------
    filename : str
        The filename used as the seed for generating the identifiers.

    Returns
    -------
    code : str
        The full integer representation of the UUIDv5 derived from the
        filename.
    short_code : str
        The first five digits of the UUID-derived code, used as a compact ID.
    """
    code = str(uuid.uuid5(uuid.NAMESPACE_URL, filename).int)
    return code, code[:5]


def sidecar_from_file(
        image_file: File,
    ) -> File:
    """
    Infers the corresponding JSON sidecar file for a given NIfTI image file.

    This function checks that the input file has a ``.nii.gz`` extension and
    attempts to locate a sidecar ``.json`` file with the same base name.

    Parameters
    ----------
    image_file : File
        The NIfTI image file for which to infer the JSON sidecar.

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


def sbref_from_file(
        image_file: File,
    ) -> File | None:
    """
    Infers the corresponding SBREFr file for a given BOLD NIfTI image file.

    This function checks that the input file has a ``.nii.gz`` extension and
    attempts to locate a SBREF ``_sbref`` file with the same base name. None is
    returned if no SBREF file is found.

    Parameters
    ----------
    image_file : File
        The NIfTI image file for which to infer the SBREF file.

    Returns
    -------
    sbref_file : File | None
        Path to the inferred SBREF file.

    Raises
    ------
    ValueError
        If the input file does not have a `.nii.gz` extension.

    Examples
    --------
    >>> from pathlib import Path
    >>> from brainprep.utils import sbref_from_file
    >>>
    >>> image_file = Path("/tmp/sub-01_bold.nii.gz")
    >>> sbref_file = Path("/tmp/sub-01_sbref.nii.gz")
    >>> sbref_file.touch()
    >>>
    >>> sbref_from_file(image_file)
    PosixPath('/tmp/sub-01_sbref.nii.gz')
    """
    if not str(image_file).endswith(".nii.gz"):
        raise ValueError(
            f"Input image file must be in NIIGZ format: {image_file}"
        )
    sbref_file = Path(
        str(image_file).replace(
            "_bold.nii.gz",
            "_sbref.nii.gz",
        )
        )
    if not sbref_file.is_file():
        sbref_file = None
    return sbref_file


def bvecbval_from_file(
        image_file: File,
    ) -> tuple[File, File]:
    """
    Infers the corresponding .bvec and .bval files for a given DWI NIfTI image
    file.

    This function checks that the input file has a ``.nii.gz`` extension and
    attempts to locate gradient information ``.bvec`` and ``.bval`` files
    with the same base name. None is returned if no gradient information
    is found.

    Parameters
    ----------
    image_file : File
        The NIfTI image file for which to infer the JSON sidecar.

    Returns
    -------
    bvec_file : File
        Path to the inferred bvec file.
    bvval_file : File
        Path to the inferred bvel file.

    Raises
    ------
    ValueError
        If the input file does not have a `.nii.gz` extension.

    Examples
    --------
    >>> from pathlib import Path
    >>> from brainprep.utils import bvecbval_from_file
    >>>
    >>> image_file = Path("/tmp/sub-01_dwi.nii.gz")
    >>> bvec_file = Path("/tmp/sub-01_dwi.bvec")
    >>> bvec_file.touch()
    >>> bval_file = Path("/tmp/sub-01_dwi.bval")
    >>> bval_file.touch()
    >>>
    >>> bvecbval_from_file(image_file)
    (PosixPath('/tmp/sub-01_dwi.bvec'), PosixPath('/tmp/sub-01_dwi.bval'))
    """
    if not str(image_file).endswith(".nii.gz"):
        raise ValueError(
            f"Input image file must be in NIIGZ format: {image_file}"
        )
    bvec_file = Path(str(image_file).replace(".nii.gz", ".bvec"))
    if not bvec_file.is_file():
        bvec_file = None
    bval_file = Path(str(image_file).replace(".nii.gz", ".bval"))
    if not bval_file.is_file():
        bval_file = None
    return bvec_file, bval_file


def find_stack_level() -> int:
    """
    Return the index of the first stack frame outside the ``brainprep``
    package.

    This function walks backward through the current call stack and finds the
    first frame whose file path does not belong to the ``brainprep`` package
    directory. Test files (i.e., files whose names start with ``test_``) are
    always treated as external. This is useful for producing cleaner warnings
    and error messages by pointing to user code rather than internal library
    frames.

    Returns
    -------
    int
        The number of internal frames to skip before reaching user code.

    Notes
    -----
    Adapted from the pandas codebase.

    Examples
    --------
    >>> import warnings
    >>> from brainprep.utils import find_stack_level
    >>>
    >>> def load_data(path):
    ...     if not path.exists():
    ...         warnings.warn(
    ...             "The provided path does not exist.",
    ...             stacklevel=find_stack_level()
    ...         )
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


def find_first_occurrence(
        input_file: Path,
        target: str,
    ) -> Path:
    """
    Return the closest parent directory whose name matches `target`.

    Parameters
    ----------
    input_file : Path
        Starting path (file or directory).
    target : str
        Name of the directory to search for.

    Returns
    -------
    Path
        The first parent directory named `target`.

    Raises
    ------
    ValueError
        If no parent directory with the given name is found.
    """
    for parent in input_file.parents:
        if parent.name == target:
            return parent

    raise ValueError(
        f"Unable to find target '{target}' in parents of {input_file}"
    )


def compress_nii(
        mri_nii: File,
        atol: float = 1e-2,
        clean_nii: bool = True,
        keep: str = 'original'
    ) -> File | list[File]:
    """Compress a .nii to a .nii.gz using nibabel. Before deleting the .nii,
    the function checks that the compressed version is not too different. If it
    is, keep images follwing the 'keep' keyword.

    Arguments
    ---------
    mri_nii: str
        Image to compress. Must be a .nii.
    atol: float
        Absolute tolerance for content comparison between the .nii
        and the generated .nii.gz
    clean_nii: bool, default True
        Set to True if you want to delete the .nii after they have
        been successfully compressed to .nii.gz.
    keep_both: str, default "both"
        Set up the behavior when the .nii and the .nii.gz don't contain
        the same data.
        Set to "both" to keep both the .nii and the .nii.gz.
        Set to "orignal" to keep the .nii.
        Set to "compressed" to keep the .nii.gz.
    """
    # save a copy as nii.gz
    if isinstance(mri_nii, str):
        mri_niigz = mri_nii.replace('.nii', '.nii.gz')
    elif isinstance(mri_nii, Path):
        mri_niigz = mri_nii.with_suffix(".gz")
    else:
        raise TypeError("'mri_nii' should be either str of Path, "
                        f"not {type(mri_nii)}")
    img_nii = nib.load(mri_nii)
    nib.save(img_nii, mri_niigz)
    # check the copy is good
    img_niigz = nib.load(mri_niigz)
    equal_affine = (img_nii.affine == img_niigz.affine).all()
    similar_content = np.allclose(img_nii.get_fdata(),
                                  img_niigz.get_fdata(),
                                  atol=atol,
                                  equal_nan=True)
    # if copy good, delete nii
    if equal_affine and similar_content:
        if clean_nii:
            os.remove(mri_nii)
        return mri_niigz
    else:
        # if copy not good, print a warning and keep files according
        # to the keep argument
        if not equal_affine:
            msg = f"Different affines for {mri_nii}."
        elif not similar_content:
            adiff = np.abs(img_nii.get_fdata() - img_niigz.get_fdata()).max()
            msg = f"Images content too different for {mri_nii}: {adiff}."
        else:
            raise AssertionError("This shouldn't be triggered.")
        msg += f" Keep {keep}"
        print(msg)
        if keep == "original":
            os.remove(mri_niigz)
            return mri_nii
        elif keep == "compressed":
            os.remove(mri_nii)
            return mri_niigz
        elif keep == "both":
            return mri_nii, mri_niigz
        else:
            err_msg = (f"{keep} value not handled for 'keep' argument. "
                       "Please choose between 'original', 'compressed' "
                       "and 'both'.")
            raise ValueError(err_msg)
