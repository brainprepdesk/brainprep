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

import json
import os
import re
import sys
import gzip
import inspect
import subprocess
import numpy as np
import pandas as pd
import nibabel

from decorator import decorator
from pathlib import Path

from .color import print_command, print_error
from .._version import __version__


@decorator
def bids(func, process=None, bids_file=None, container=None, *args, **kw):
    """
    BIDS specification.

    Decorator that computes a BIDS-compliant output directory path
    based on the input BIDS file and injects it into the function.

    Decorator that ensures BIDS-compliant metadata is written to the output
    directory.

    Parameters
    ----------
    func : callable
        The function to be decorated.
    process : str
        Name of the processing pipeline (e.g., 'fmriprep', 'custom').
    bids_file : Union[File,Iterable[File]]
        Name of the argument in the function that contains the BIDS file path.
    container : str
        The name of the container (e.g., Docker image) used to run the
        pipeline.
    *args : tuple
        Positional arguments passed to `func`.
    **kw : dict
        Keyword arguments passed to `func`.

    Returns
    -------
    wrapper : function
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
    if subject_level:
        for key in (bids_file, "output_dir"):
            if key not in inputs:
                raise ValueError(
                    f"This decorator needs a '{key}' function argument."
                )
        if isinstance(inputs[bids_file], (list, tuple)):
            entities = parse_bids_keys(inputs[bids_file][0])
        else:
            entities = parse_bids_keys(inputs[bids_file])
        output_dir = (
            Path(inputs["output_dir"]) /
            "derivatives" /
            process /
            f"sub-{entities['sub']}" /
            f"ses-{entities['ses']}"
        )
        metadata_file = output_dir.parent.parent / "dataset_description.json"
    else:
        output_dir = (
            Path(inputs["output_dir"]) /
            "derivatives" /
            process
        )
        metadata_file = output_dir / "dataset_description.json"

    output_dir.mkdir(parents=True, exist_ok=True)
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


def execute_command(command):
    """ Execute a command.

    Parameters
    ----------
    command: list of str
        the command to be executed.
    """
    print_command(" ".join(command))
    proc = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, error = proc.communicate()
    if proc.returncode != 0:
        raise ValueError(
            "\nCommand {0} failed:\n\n- output:\n{1}\n\n- error: "
            "{2}\n\n".format(" ".join(command),
                             output.decode("utf8"),
                             error.decode("utf8")))


def check_command(command):
    """ Check if a command is installed.

    .. note:: This function is based on which linux command.

    Parameters
    ----------
    command: str
        the name of the command to locate.
    """
    if sys.platform != "linux":
        raise ValueError("This code works only on a linux machine.")
    process = subprocess.Popen(
        ["which", command], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode("utf8")
    stderr = stderr.decode("utf8")
    exitcode = process.returncode
    if exitcode != 0:
        print_error("Command {0}: {1}".format(command, stderr))
        raise ValueError("Impossible to locate command '{0}'.".format(command))


def check_version(package_name, check_pkg_version):
    """ Check installed version of a package.

    .. note:: This function is based on dpkg linux command.

    Parameters
    ----------
    package_name: str
        the name of the package we want to check the version.
    """
    process = subprocess.Popen(
        ["dpkg", "-s", package_name],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    stdout = stdout.decode("utf8")
    stderr = stderr.decode("utf8")
    exitcode = process.returncode
    if check_pkg_version:
        # local computer installation
        if exitcode != 0:
            version = None
            print_error("Version {0}: {1}".format(package_name, stderr))
            raise ValueError(
                "Impossible to check package '{0}' version."
                .format(package_name))
        else:
            versions = re.findall("Version: .*$", stdout, re.MULTILINE)
            version = "|".join(versions)
    else:
        # specific installation
        version = "custom install (no check)."
    print("{0} - {1}".format(package_name, version))


def write_matlabbatch(template, nii_files, tpm_file, darteltpm_file,
                      session, batch_file, outdir, model_long=1):
    """ Complete matlab batch from template and unzip T1w file in the outdir.
        Create the outdir.

    Parameters
    ----------
    template: str
        path to template batch to be completed.
    nii_files: list
        the Nifti images to be processed.
    tpm_file: str
        path to the SPM TPM file.
    darteltpm_file: str
        path to the CAT12 tempalte file.
    batch_file: str
        Filepath to the matlabbatch
    outdir: str
        the destination folder for cat12vbm outputs.
    session: str
        the session names, usefull for longitudinal preprocessings.
        Warning session and nii files must be in the same order.
    model_long: int
        longitudinal model choice, default 1.
        1 short time (weeks), 2 long time (years) between images sessions.
    """
    nii_files_str = ""
    if session:
        outdir = [os.path.join(outdir, ses) for ses in session]
    if not isinstance(outdir, list):
        outdir = [outdir]
    for idx, path in enumerate(nii_files):
        nii_files_str += "'{0}' \n".format(
            ungzip_file(path, outdir=outdir[idx]))
    with open(template, "r") as of:
        stream = of.read()
        stream = stream.format(model_long=model_long, anat_file=nii_files_str,
                               tpm_file=tpm_file,
                               darteltpm_file=darteltpm_file)
    with open(batch_file, "w") as of:
        of.write(stream)


def ungzip_file(zfile, prefix="u", outdir=None):
    """ Copy and ungzip the input file.

    Parameters
    ----------
    zfile: str
        input file to ungzip.
    prefix: str, default 'u'
        the prefix of the result file.
    outdir: str, default None)
        the output directory where ungzip file is saved. If not set use the
        input image directory.

    Returns
    -------
    unzfile: str
        the ungzip file.
    """
    # Checks
    if not os.path.isfile(zfile):
        raise ValueError("'{0}' is not a valid filename.".format(zfile))
    if outdir is not None:
        if not os.path.isdir(outdir):
            raise ValueError("'{0}' is not a valid directory.".format(outdir))
    else:
        outdir = os.path.dirname(zfile)

    # Get the file descriptors
    base, extension = os.path.splitext(zfile)
    basename = os.path.basename(base)

    # Ungzip only known extension
    if extension in [".gz"]:
        basename = prefix + basename
        unzfile = os.path.join(outdir, basename)
        with gzip.open(zfile, "rb") as gzfobj:
            data = gzfobj.read()
        with open(unzfile, "wb") as openfile:
            openfile.write(data)

    # Default, unknown compression extension: the input file is returned
    else:
        unzfile = zfile

    return unzfile


def parse_bids_keys(bids_path):
    """
    Parses BIDS keys and modality from a filename or path with validation.

    Parameters
    ----------
    bids_path : str
        The BIDS filename or full path.

    Returns
    -------
    entities : dict
        A dictionary of parsed BIDS entities including modality.
    """
    # Extract the filename from the path
    filename = os.path.basename(bids_path)

    # Regex pattern for BIDS entities
    entity_pattern = (
        r"(?P<entity>(sub|ses|task|acq|run|echo|rec|dir|mod|ce|part|"
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

    # Define default values for missing entities
    defaults = {
        "ses": "01",
        "run": "1",
    }

    # Fill in missing entities with defaults
    for key, default in defaults.items():
        entities.setdefault(key, default)

    return entities


def load_images(img_files, check_same_referential=True):
    """ Load a list of images in a BIDS organisation: check that all images
    are in the same referential.

    Parameters
    ----------
    img_files: list of str (n_subjects, )
        path to images.

    Returns
    -------
    imgs_arr: array (n_subjects, 1, image_axis0, image_axis1, ...)
        the generated array.
    df: pandas DataFrame
        description of the array with columns 'participant_id',
        'session', 'run', 'ni_path'.
    """
    ref_affine = None
    ref_shape = None
    data = []
    info = {}
    for path in img_files:
        keys = parse_bids_keys(path)
        participant_id = keys["participant_id"]
        session = keys.get("session", "V1")
        run = keys.get("run", "1")
        img = nibabel.load(path)
        if ref_affine is None:
            ref_affine = img.affine
            ref_shape = img.shape
        else:
            assert np.allclose(ref_affine, img.affine), "Different affine."
            assert ref_shape == img.shape, "Different shape."
        data.append(np.expand_dims(img.get_fdata(), axis=0))
        info.setdefault("participant_id", []).append(participant_id)
        info.setdefault("session", []).append(session)
        info.setdefault("run", []).append(run)
        info.setdefault("ni_path", []).append(path)
    df = pd.DataFrame.from_dict(info)
    imgs_arr = np.asarray(data)
    return imgs_arr, df


def create_clickable(path_or_url):
    """ Foramt a path or a URL as a HTML href.

    Parameters
    ----------
    path_or_url: str
        a path or a URL.

    Returns
    -------
    url: str
        a href formated URL.
    """
    url = "<a href='{}' target='_blank'>&plus;</a>".format(path_or_url)
    return url


def listify(obj):
    """ Function to transform a coma separated string to a list of string.

    Parameters
    ----------
    obj: list or string
        the input data.

    Returns
    -------
    list: list
        the list of input data or input data.
    """
    if not isinstance(obj, list):
        return obj.split(",")
    else:
        return obj
