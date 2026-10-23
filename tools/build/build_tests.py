##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Provide a command line interface to test examples.
"""

import io
import runpy
import sys
from pathlib import Path

from brainprep.wrappers import run_command


def main(
        working_dir: str | Path,
        examples_dir: str | Path,
        image_template: str,
        image_parameters: str | None = None,
        save_file: str | Path | None = None,
        dryrun: bool = False,
    ) -> None:
    """
    Execute examples scripts in brainprep containers.

    This function scans a directory for Python scripts. Each such script is
    executed in an isolated namespace to extract a variable named ``commands``.
    Each ``command`` is then packed to be exeuted withing a brainprep
    container.

    Parameters
    ----------
    working_dir : str | Path
        Directory where the instructions / build environment will be generated.
    examples_dir : str | Path
        Directory containing example Python scripts.
    image_template : str
        Path to the container or image file referenced in the generated config
        where `{workflow}` acts as a placeholder. The calling code replaces
        `{workflow}` with the name of the image being processed. Using a
        template allows the script to dynamically generate commands for
        different images without duplicating code.
    image_parameters: str | None
        Additional parameters passed to the Apptainer container.
        Default None.
    save_file : str | Path | None
        Path to the file where the testing commands are saved.
        Default None.
    dryrun : bool
        Dont't execute the commands.
        Default False.

    Raises
    ------
    KeyError
        If a script does not define the expected ``datadir`` or ``outdir``
        variables.
    """
    banner = r"""
    +----------------------------------+
    |        BUILDING TESTS...         |
    +----------------------------------+
    """
    print(banner)

    # Build destination dirs
    datadir = working_dir / "bidsdata"
    scriptdir = working_dir / "scripts"
    for dir_ in (datadir, scriptdir):
        dir_.mkdir(parents=True, exist_ok=True)
    print(f"- Data direcotry: {datadir}")
    print(f"- Script direcotry: {scriptdir}")

    # Scan example scripts
    working_dir = Path(working_dir)
    examples_dir = Path(examples_dir)
    commands = []
    for script_file in examples_dir.rglob("*.py"):

        print(
            "\n"
            f"ℹ️  INFO: Commands from script: {script_file.stem}"
        )

        # Get commands from script executed in isolated namespace
        workflow_name = script_file.stem.replace("plot_", "")
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        env = runpy.run_path(str(script_file))
        sys.stdout = original_stdout
        examples_commands = env.get("commands", [])
        if len(examples_commands) == 0:
            print("- No command")
            continue
        print(f"- Execution: {len(examples_commands)} step(s)")

        # Get test example data locations
        datadir_orig = Path(env["datadir"])
        outdir_orig = Path(env["outdir"])

        # Copy raw data
        print(f"- Copy data: {datadir_orig} -> {datadir}")
        commands.append(
            [
                "rsync",
                "-av",
                str(datadir_orig),
                str(datadir),
            ]
        )

        # Build test commands
        for idx, step_commands in enumerate(examples_commands, start=1):
            run_file = scriptdir / f"run_{workflow_name}_{idx}.sh"
            image_file = str(image_template).format(
                workflow=workflow_name,
            )

            # Format commands
            step_commands = [
                [*cmd, "--no-color"]
                for cmd in step_commands
            ]
            run_cmd = f"apptainer run {image_parameters or ''} {image_file}"
            step_commands_str = "\n".join([
                f"{run_cmd} {' '.join(cmd_)}  &"
                for cmd_ in step_commands
            ])
            step_commands_str = step_commands_str.replace(
                str(datadir_orig),
                str(datadir),
            )
            step_commands_str = step_commands_str.replace(
                str(outdir_orig),
                str(datadir),
            )

            # Write commands to file
            bash_str = "#!/bin/bash\n\n"
            bash_str += step_commands_str
            bash_str += "\n\nwait"
            with run_file.open("w") as of:
                of.write(bash_str)

            # Execute commands
            commands.append(
                [
                    ".",
                    str(run_file),
                ]
            )
            print(f"- Command: {commands[-1]}")

    # Execution
    commands_txt = ""
    commands = [
        list(cmd)
        for cmd in dict.fromkeys(tuple(cmd) for cmd in commands)
    ]
    for cmd in commands:
        print(
            "\n"
            f"🚀 TEST: {' '.join(cmd)}"
        )
        commands_txt += f"{' '.join(cmd)}\n"
        if not dryrun:
            try:
                run_command(cmd)
                print("   |-> ✅")
            except RuntimeError as err:
                print("   |-> ❌")
        else:
            print("   |-> 🟡")

    # Save generated testing commands
    if save_file is not None:
        save_file = Path(save_file)
        if not save_file.is_file():
            save_file.touch()
        save_file.write_text(
            save_file.read_text(encoding="utf-8") +
            commands_txt
        )
        print(
            "\n"
            f"💾 SAVE: test commands - {save_file}"
        )

    print(
        "\n"
        "💡 TIP: You can overwrite the brainprep module in the .sif image.\n "
        "This is useful if you want to test some minor fixes.\n"
        "To bind your dev brainprep repository within the .sif file, just add "
        "the '--dev' argument to the command line.\n"
        "You can now test directly your dev repository."
    )

    print(
        "\n"
        "⚠️  WARNING: For some workflows as the brain parcellation workflows "
        "you will need to specify the FreeSurfer license file. Just add the "
        "'--freesurfer-license-file argument to the command line."
    )
