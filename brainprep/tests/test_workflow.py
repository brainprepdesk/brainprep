##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################


import unittest
import runpy
from pathlib import Path


class TestGalleryExamples(unittest.TestCase):

    def setUp(self):
        self.examples_dir = Path(__file__).parent.parent.parent / "examples"

    def test_html_reporting(self):
        script_path = self.examples_dir / "plot_html_reporting.py"
        runpy.run_path(str(script_path))

    def test_rst_reporting(self):
        script_path = self.examples_dir / "plot_rst_reporting.py"
        runpy.run_path(str(script_path))

    def test_quality_assurance(self):
        script_path = self.examples_dir / "plot_quality_assurance.py"
        runpy.run_path(str(script_path))

    def test_defacing(self):
        script_path = self.examples_dir / "plot_defacing.py"
        runpy.run_path(str(script_path))

    def test_quasiraw(self):
        script_path = self.examples_dir / "plot_quasiraw.py"
        runpy.run_path(str(script_path))

    def test_brain_parcellation(self):
        script_path = self.examples_dir / "plot_brain_parcellation.py"
        runpy.run_path(str(script_path))

    def test_vbm(self):
        script_path = self.examples_dir / "plot_vbm.py"
        runpy.run_path(str(script_path))

    def test_fmriprep(self):
        script_path = self.examples_dir / "plot_fmriprep.py"
        runpy.run_path(str(script_path))


if __name__ == "__main__":
    unittest.main()
