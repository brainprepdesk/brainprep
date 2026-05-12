##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2026
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


import subprocess
import unittest
import runpy
from pathlib import Path


class TestGalleryExamples(unittest.TestCase):

    def setUp(self, test_interfaces=True):
        self.test_interfaces = test_interfaces
        self.examples_dir = Path(__file__).parent.parent.parent / "examples"

    def _test_interface_commands(self, env):
        if not self.test_interfaces:
            return
        outdir = Path(env["outdir"])
        commands = []
        for commands_file in outdir.rglob("commands_*.rst"):
            commands.extend(
                commands_file.read_text().splitlines()
            )
        print(f"Parsed: {outdir}")
        print(f"Interface commands: {len(commands)}")
        procs = [
            (
                cmd, subprocess.Popen(
                    cmd.split(" "),
                    stdout=subprocess.PIPE,
                )
            )
            for cmd in commands
        ]
        failures = []
        for cmd, proc in procs:
            out = proc.communicate()
            if proc.returncode != 0:
                failures.append(
                    f"Command failed: {cmd}\n"
                )
        if failures:
            self.fail("\n".join(failures))

    def test_html_reporting(self):
        script_path = (
            self.examples_dir /
            "tools" /
            "plot_html_reporting.py"
        )
        runpy.run_path(str(script_path))

    def test_rst_reporting(self):
        script_path = (
            self.examples_dir /
            "tools" /
            "plot_rst_reporting.py"
        )
        runpy.run_path(str(script_path))

    def test_quality_assurance(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_quality_assurance.py"
        )
        env = runpy.run_path(str(script_path))
        self._test_interface_commands(env)

    def test_defacing(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_defacing.py"
        )
        env = runpy.run_path(str(script_path))
        # self._test_interface_commands(env)

    def test_quasiraw(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_quasiraw.py"
        )
        env = runpy.run_path(str(script_path))
        # self._test_interface_commands(env)

    def test_sbm(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_sbm.py"
        )
        env = runpy.run_path(str(script_path))
        # self._test_interface_commands(env)

    def test_vbm(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_vbm.py"
        )
        env = runpy.run_path(str(script_path))
        # self._test_interface_commands(env)

    def test_fmriprep(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_fmriprep.py"
        )
        env = runpy.run_path(str(script_path))
        # self._test_interface_commands(env)


if __name__ == "__main__":
    unittest.main()
