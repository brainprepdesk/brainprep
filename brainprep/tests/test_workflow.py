##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
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

    def setUp(self):
        self.examples_dir = Path(__file__).parent.parent.parent / "examples"

    def _test_interface_commands(self, env):
        outdir = Path(env["outdir"])
        for commands_file in outdir.rglob("commands_*.rst"):
            for cmd in commands_file.read_text().splitlines():
                print("*", cmd.split(" "))
                print(cmd)
                subprocess.check_call(cmd.split(" "))

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
        self._test_interface_commands(env)

    def test_quasiraw(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_quasiraw.py"
        )
        env = runpy.run_path(str(script_path))
        self._test_interface_commands(env)

    def test_sbm(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_sbm.py"
        )
        env = runpy.run_path(str(script_path))
        self._test_interface_commands(env)

    def test_vbm(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_vbm.py"
        )
        env = runpy.run_path(str(script_path))
        self._test_interface_commands(env)

    def test_fmriprep(self):
        script_path = (
            self.examples_dir /
            "workflows" /
            "plot_fmriprep.py"
        )
        env = runpy.run_path(str(script_path))
        self._test_interface_commands(env)


if __name__ == "__main__":
    unittest.main()
