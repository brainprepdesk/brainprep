##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" Provide a command line interface.
"""

import sys
from pathlib import Path

cw_dir = Path(__file__).parent.resolve()
sys.path.append(str(cw_dir))

import fire
from build_images import main as build_images_main
from build_tests import main as build_tests_main

from brainprep import __version__ as version


def build(
        working_dir: str | Path,
        bind_dir: str | Path,
        partition: str,
        freesurfer_license_file: str | Path,
        dev: bool = False,
    ) -> None:
    """
    Parse available Docker files and generate the associated build instructions
    (creation and test steps).

    Two infrastructures are supported: ``ccc`` and ``slurm``.
    To select one, use either ``<name>`` or ``<project>:<name>`` as the value
    of the ``partition`` parameter.

    Parameters
    ----------
    working_dir : str | Path
        Directory where the generated instructions will be written.
    bind_dir : str | Path
        Directory containing the data to be bound into the Docker environment.
    partition : str
        Name of the partition to use. Can be provided as ``<name>`` or
        ``<project>:<name>`` depending on the infrastructure.
    freesurfer_license_file : str | Path
        Path to the FreeSurfer license file required for container execution.
    dev : bool
        If True, overwrite the ``brainprep`` module inside the container image.
        Default is False.
    """
    cw_dir = Path(__file__).parent.resolve()
    working_dir = Path(working_dir)
    hopla_dir = working_dir / f"v{version}" / "hopla"
    home_dir = working_dir / f"v{version}" / "home"
    examples_dir = cw_dir.parent.parent / "examples"
    for dir_ in (hopla_dir, home_dir):
        dir_.mkdir(parents=True, exist_ok=True)

    if ":" in partition:
        infra = "ccc"
        project_id, partition = partition.split(":")
        image_extension = "sif"
    else:
        infra = "slurm"
        project_id = None
        image_extension = "tar"

    if infra == "slurm":
        build_images_main(
            working_dir,
        )
    placeholder = "{workflow}"
    if infra == "slurm":
        image_parameters = f"--cleanenv --home {home_dir} --bind {bind_dir} "
        if dev:
            image_parameters += (
                f"--bind {cw_dir.parent.parent / 'brainprep'}:"
                "/opt/brainprep/.pixi/envs/default/lib/python3.12/site-packages/"
                "brainprep "
            )
    elif infra == "ccc" and dev:
        image_parameters = (
            f"-v {cw_dir.parent.parent / 'brainprep'}:"
            "/opt/brainprep/.pixi/envs/default/lib/python3.12/site-packages/"
            "brainprep "
        )
    else:
        image_parameters = ""

    build_tests_main(
        examples_dir,
        infra=infra,
        image_template=(
            working_dir /
            f"v{version}" /
            placeholder /
            f"brainprep-{placeholder}-v{version}.{image_extension}"
        ),
        save_template=(
            working_dir /
            f"v{version}" /
            placeholder /
            "commands"
        ),
        root_template=(
            working_dir /
            f"v{version}" /
            placeholder
        ),
        image_parameters=image_parameters,
        hopla_dir=hopla_dir,
        partition=partition,
        freesurfer_license_file=freesurfer_license_file,
        project_id=project_id,
    )


def main():
    """
    BrainPrep build command-line interface.

    This function exposes the commands to build (create and test) BrainPrep
    Docker/Singularity images.

    Notes
    -----
    This function relies on ``fire.Fire`` to automatically generate a
    command-line interface from a dictionary mapping workflow names to
    their corresponding functions. Any additional keyword arguments
    provided on the command line are forwarded to the selected workflow.

    Examples
    --------
    Build test instructions from the example scripts in the ``examples``
    repository directory using the ``slurm`` infrastructure and a given
    container image:

        python3 containers/build/build_cli.py build-tests \
            --examples-dir examples \
            --infra slurm \
            --image-template /tmp/brainprep-{workflow}-v2.0.0.sif \
            --hopla-dir /tmp/hopla

    Build image creation instructions in a given folder:

        python3 containers/build/build_cli.py build-images \
            --working-dir /tmp/build

    Build image creation and test instructions in a given folder:

        python3 containers/build/build_cli.py build \
            --working-dir /tmp/build \
            --bind-dir /my/data/dir
    """
    fire.Fire({
        "build-tests": build_tests_main,
        "build-images": build_images_main,
        "build": build,
    })


if __name__ == "__main__":
    main()
