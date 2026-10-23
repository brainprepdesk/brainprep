##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Provide a command line interface.
"""

import sys
from pathlib import Path

import fire

from brainprep import __version__

cw_dir = Path(__file__).parent.resolve()
sys.path.append(str(cw_dir))

from build_images import main as build_images_main
from build_tests import main as build_tests_main


def build(
        working_dir: str | Path,
        bind_dir: str | Path | None = None,
        freesurfer_license_file: str | Path | None = None,
        dev: bool = False,
        dryrun: bool = False,
    ) -> None:
    """
    Build brainprep images, and generate/execute associated test commands.

    Parameters
    ----------
    working_dir : str | Path
        Directory where the build and tests are done.
    bind_dir : str | Path | None
        Directory containing the data to be bound into the Apptainer
        environment.
        Default None.
    freesurfer_license_file : str | Path | None
        Path to the FreeSurfer license file required for some containers
        execution.
        Default None.
    dev : bool
        If True, overwrite the ``brainprep`` module inside the container image.
        Default False.
    dryrun : bool
        Dont't execute the commands.
        Default False.
    """
    version = __version__.replace(".dev", "")
    working_dir = Path(working_dir) / f"v{version}"
    home_dir = working_dir / "home"
    brainprep_dir = Path(__file__).resolve().parent.parent.parent
    examples_dir = brainprep_dir / "examples"
    home_dir.mkdir(parents=True, exist_ok=True)
    print(f"- Home direcotry: {home_dir}")

    build_images_main(
        working_dir,
        dryrun=dryrun,
    )

    placeholder = "{workflow}"
    image_parameters = f"--cleanenv --home {home_dir} "
    if bind_dir is not None:
        image_parameters += f"--bind {bind_dir} "
    if freesurfer_license_file is not None:
        image_parameters += (
            f" --bind {freesurfer_license_file}:/opt/freesurfer/license.txt"
        )
    if dev:
        image_parameters += (
            f" --bind {brainprep_dir / 'brainprep'}:"
            "/opt/brainprep/.pixi/envs/default/lib/python3.12/site-packages/"
            "brainprep"
        )

    build_tests_main(
        working_dir,
        examples_dir,
        image_template=(
            working_dir /
            "images" /
            f"brainprep-{placeholder}-v{version}.sif"
        ),
        image_parameters=image_parameters,
        save_file=working_dir / "commands",
        dryrun=dryrun,
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
    repository:

        python3 tools/build/build_cli.py build-tests \
            --examples-dir examples \
            --image-template /tmp/brainprep-{workflow}-v2.0.0.sif

    Build image creation instructions:

        python3 tools/build/build_cli.py build-images \
            --working-dir /tmp/build
            --dryrun

    Build image creation and test instructions:

        python3 tools/build/build_cli.py build \
            --working-dir /tmp/build \
            --dev \
            --dryrun
    """
    fire.Fire({
        "build-tests": build_tests_main,
        "build-images": build_images_main,
        "build": build,
    })


if __name__ == "__main__":
    main()
