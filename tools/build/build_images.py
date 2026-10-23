##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Provide a tool to build brainprep images.
"""

from pathlib import Path

from brainprep.wrappers import run_command


def main(
        working_dir: str | Path,
        dryrun: bool = False,
    ) -> None:
    """
    Build brainprep images.

    Parameters
    ----------
    working_dir : str | Path
        Directory where the instructions / build environment will be generated.
    dryrun : bool
        Dont't execute the commands.
        Default False.
    """
    banner = r"""
    +----------------------------------+
    |        BUILDING IMAGES...        |
    +----------------------------------+
    """
    print(banner)

    working_dir = Path(working_dir).resolve()
    cw_dir = Path(__file__).parent.resolve()
    image_dir = cw_dir.parent.parent / "containers" / "wip"

    print(
        "⚠️  WARNING: Don't use Docker default storage directory "
        "(/var/lib/docker), which may not have enough free space to build "
        "images.\n"
        "To avoid build failures, permission errors, or slow performance, "
        "you should configure Docker to use a custom data directory with "
        "sufficient space.\n"
        "How to change Docker's image storage location:\n"
        "1. Create a new directory:\n"
        "     sudo mkdir -p /path/to/new/docker-data\n"
        "     sudo chown root:root /path/to/new/docker-data\n"
        "2. Edit Docker's daemon configuration:\n"
        "     sudo nano /etc/docker/daemon.json\n"
        "   Add or update the following entry:\n"
        "     { \'data-root\': \'/path/to/new/docker-data\' }\n"
        "3. Stop Docker:\n"
        "     sudo systemctl stop docker\n"
        "4. (Optional) Move existing Docker data:\n"
        "     sudo rsync -aP /var/lib/docker/ /path/to/new/docker-data/\n"
        "5. Restart Docker:\n"
        "     sudo systemctl start docker\n"
        "6. Verify the new location:\n"
        "     docker info | grep 'Docker Root Dir'\n"
        "Docker will now store images in the new directory."
    )

    # Build images
    bake_file = image_dir / "docker-bake.hcl"
    build_file = image_dir / "build.sh"
    print(
        "\n"
        "ℹ️  INFO: Building from using bake Docker buildx command: "
        f"{bake_file}"
    )
    if not bake_file.is_file():
        raise ValueError(f"Can't find buid instructions: {build_file}")
    commands = [
        [
            "rsync",
            "-av",
            str(image_dir),
            str(working_dir),
        ],
        [
            ".",
            str(working_dir / "build.sh"),
        ]
    ]
    commands_txt = ""
    for cmd in commands:
        print(
            "\n"
            f"🚀 BUILD: {' '.join(cmd)}"
        )
        commands_txt += f"{' '.join(cmd)}\n"
        if not dryrun:
            run_command(cmd)

    # Write commands to file
    commands_file = working_dir / "commands"
    commands_file.write_text(commands_txt)
    print(
        "\n"
        f"💾 SAVE: build commands - {commands_file}"
    )

    print(
        "\n"
        "💡 TIP: You can convert the generated .sif image into a writable "
        "sandbox.\n"
        "This is useful if you want to inspect or modify the container "
        "filesystem.\n"
        "To create a sandbox directory from a .sif file, run:\n"
        "    sudo singularity build --sandbox <sandbox_dir> <image>.sif\n"
        "You can then explore or modify the sandbox directory directly."
    )
