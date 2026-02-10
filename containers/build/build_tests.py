##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
Provide a command line interface to test examples on different
infrastructure.
"""

import copy
import io
import json
import runpy
import shutil
import sys
import tomllib
from datetime import datetime
from pathlib import Path


def main(
        examples_dir,
        infra,
        image_template,
        hopla_dir,
        partition,
        freesurfer_license_file,
        image_parameters=None,
        root_template=None,
        save_template=None,
    ):
    """
    Execute examples scripts using ``hoplacli``.

    This function scans a directory for Python scripts. Each such script is
    executed in an isolated namespace to extract a variable named ``commands``.
    For each step in ``commands``, a configuration file is generated from a
    TOML template, along with the corresponding `hoplacli` command that is
    finally executed.

    Parameters
    ----------
    examples_dir : str or Path
        Directory containing example Python scripts.
    infra : str
        Infrastructure identifier. Must match one of the available
        ``*_default_config.toml`` templates in the local ``resources`` folder.
    image_template : str
        Path to the container or image file referenced in the generated config
        where `{workflow}` acts as a placeholder. The calling code replaces
        `{workflow}` with the name of the image being processed. Using a
        template allows the script to dynamically generate commands for
        different images without duplicating code.
    hopla_dir: str or Path
        Path to the hopla working directory.
    partition : str
        Name of the partition to use: <name> or <project>:<name>.
    freesurfer_license_file : str or Path
        Path to the FreesurFer license file.
    image_parameters: str
        Additional parameters passed to the container execution command.
        Default None.
    root_template : str
        Path to the working directory where `{workflow}` acts as a placeholder.
        The calling code replaces `{workflow}` with the name of the image
        being processed. Defaults are directly defined in the
        examples: ``datadir`` and ``outdir``. Default None.
    save_template: str
        Path to the file where the testing commands are saved where
        `{workflow}` acts as a placeholder. The calling code replaces
        `{workflow}` with the name of the image being processed. Default None.

    Raises
    ------
    ValueError
        If the provided ``infra`` does not match any available configuration
        template in the ``resources`` directory or if the ``save_template``
        varaible is used in a partial build.
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

    # Get configuration templates
    cw_dir = Path(__file__).parent.resolve()
    config_dir = cw_dir / "resources"
    template_paths = config_dir.glob("*_default_config.toml")
    config_files = {
        path.name.split("_")[0]: path
        for path in template_paths
    }
    if infra not in config_files:
        raise ValueError(f"Unsupported infrastructure: {infra}.")
    config_template = config_files[infra].read_text()
    workflow_resource_file = config_dir / "workflows_config.toml"
    with workflow_resource_file.open("rb") as of:
         workflow_resource = tomllib.load(of)
    image_parameters = image_parameters or ""

    # Scan example scripts
    examples_dir = Path(examples_dir)
    script_paths = examples_dir.glob("*.py")
    hoplacli_commands = []
    start = 0
    for script_file in script_paths:

        # Get commands from script executed in isolated namespace
        name = script_file.name.replace("".join(script_file.suffixes), "")
        workflow_name = name.replace("plot_", "")

        print(
            "\n"
            f"ℹ️  INFO: Commands from script: {name}"
        )
        original_stdout = sys.stdout
        sys.stdout = io.StringIO()
        env = runpy.run_path(str(script_file))
        sys.stdout = original_stdout
        commands = env.get("commands", [])
        if len(commands) == 0:
            print("- No command")
            continue

        # Prepapre commands to execute code with hoplacli
        print(f"- Execution: {len(commands)} steps")
        confs = workflow_resource[workflow_name]
        if root_template is not None:
            datadir_orig = Path(env["datadir"])
            outdir_orig = Path(env["outdir"])
            datadir = Path(
                str(root_template).format(
                    workflow="data",
                )
            )
            outdir = Path(
                str(root_template).format(
                    workflow=workflow_name,
                )
            )
            print(f"- Copy data: {datadir_orig} -> {datadir}")
            shutil.copytree(datadir_orig, datadir, dirs_exist_ok=True)
        else:
            datadir = Path(env["datadir"])
            outdir = Path(env["outdir"])
        for idx, step_commands in enumerate(commands, start=1):
            config_path = outdir / f"config_step{idx}.toml"

            # Format commands
            step_commands_str = json.dumps(step_commands, indent=2)
            if root_template is not None:
                step_commands_str = step_commands_str.replace(
                    str(datadir_orig),
                    str(datadir),
                )
                step_commands_str = step_commands_str.replace(
                    str(outdir_orig),
                    str(datadir),
                )

            # Fill template
            image_file = str(image_template).format(
                workflow=name.replace("plot_", ""),
            )
            if confs["default"].get("use_freesurfer", False):
                image_parameters += (
                    f"--bind {freesurfer_license_file}:"
                    "/opt/freesurfer/license.txt "
                )
            config_str = config_template.format(
                name=f"{script_file.stem}-step{idx}",
                operator="deamon",
                date=str(datetime.now().date()),
                commands=step_commands_str,
                parameters=image_parameters,
                partition=partition,
                n_cpus=confs["default"]["n_cpus"],
                memory=confs["default"]["memory"],
                image_file=image_file,
                hopla_dir=hopla_dir,
            )

            # Write config file
            with config_path.open("w") as f:
                f.write(config_str)

            # Execute hoplacli command
            hopla_cmd = [
                "hoplacli",
                "--config", str(config_path),
                "--njobs", "10",
            ]
            hoplacli_commands.append(hopla_cmd)
            print(f"- Command: {''.join(hopla_cmd)}")

        # Save generated testing commands
        if save_template is not None:
            save_file = Path(
                str(save_template).format(
                    workflow=name.replace("plot_", ""),
                )
            )
            if not save_file.is_file():
                raise ValueError(
                    "Only use the ``save_template`` varaible in a complete "
                    "build."
                )
            with save_file.open("a") as of:
                of.write(
                    "\n".join(
                        " ".join(cmd) for cmd in hoplacli_commands[start:]
                    )
                )
            start = len(hoplacli_commands)
            print(f"- Generated build instructions: {save_file}")

    print(
        "\n"
        "💡 TIP: You can overwrite the brainprep module in the .sif image.\n "
        "This is useful if you want to test some minor fixes.\n"
        "To bind your dev brainprep repository within the .sif file, run:\n"
        f"    singularity run --bind {cw_dir.parent.parent / 'brainprep'}:"
        "/opt/brainprep/.pixi/envs/default/lib/python3.12/site-packages/"
        "brainprep ...\n"
        "You can now test direectly your dev repository."
    )

    print(
        "\n"
        "⚠️  WARNING: For the brain parcellation workflows you will need "
        "to specify the FreeSurfer license file using the following bind:\n"
        f"    singularity run --bind [LICENSE]:/opt/freesurfer/.license "
        "brainprep ..."
    )


def merge(defaults: dict, overrides: dict) -> dict:
    """
    Recursively merge two dictionaries, applying overrides to defaults.

    Parameters
    ----------
    defaults : dict
        The base dictionary containing default parameter values.
    overrides : dict
        A dictionary containing values that should override the defaults.
        Nested dictionaries are merged recursively.

    Returns
    -------
    dict
        A new dictionary containing the merged result, where values from
        `overrides` take precedence over those in `defaults`.

    Notes
    -----
    - This function does not modify the input dictionaries.
    - When both dictionaries contain a nested dictionary under the same key,
      the merge is performed recursively.
    - When a key exists only in `overrides`, it is added to the result.

    Examples
    --------
    >>> defaults = {"a": 1, "b": {"x": 10, "y": 20}}
    >>> overrides = {"b": {"y": 99}}
    >>> merge(defaults, overrides)
    {'a': 1, 'b': {'x': 10, 'y': 99}}
    """
    result = copy.deepcopy(defaults)
    for key, value in overrides.items():
        if (isinstance(value, dict) and key in result and
                isinstance(result[key], dict)):
            result[key] = merge(result[key], value)
        else:
            result[key] = value
    return result
