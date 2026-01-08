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

import fire

from brainprep import __version__ as version

cw_dir = Path(__file__).parent.resolve()
sys.path.append(str(cw_dir))

from build_images import main as build_images_main
from build_tests import main as build_tests_main


def build(
        working_dir,
        bind_dir,
    ):
    """
    Parse available Docker files and generate associated build (creation and
    test) instructions.

    Parameters
    ----------
    working_dir : str or Path
        Directory where the instructions will be generated.
    bind_dir : str or Path
        Directory where the data are available.
    """
    cw_dir = Path(__file__).parent.resolve()
    working_dir = Path(working_dir)
    hopla_dir = working_dir / "hopla"
    home_dir = working_dir / "home"
    history_file = home_dir / "history"
    examples_dir = cw_dir.parent.parent / "examples"
    for _dir in (hopla_dir, home_dir):
        _dir.mkdir(parents=True, exist_ok=True)
    history_file.touch()

    build_images_main(
        working_dir,
    )
    placeholder = "{workflow}"
    build_tests_main(
        examples_dir,
        infra="slurm",
        image_template=(
            working_dir /
            f"v{version}" /
            placeholder /
            f"brainprep-{placeholder}-v{version}.sif"
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
        image_parameters=(
            f"--cleanenv --home {home_dir} --bind {bind_dir} "
            f"--bind {history_file}:/opt/brainprep/.pixi/envs/default/"
            "conda-meta/history"
        ),
        hopla_dir=hopla_dir,
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
