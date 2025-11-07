"""
Quality Assurance
=================

Simple example.

Example on how to run the quality assurance pre-processing using BrainPrep.
See :ref:`user guide <quality_assurance>` for details.

Data
----

Let's first get some anatomical data.
"""

from pathlib import Path
from brainprep.datasets import AnatomicalDataset
from brainprep.utils import Bunch

datadir = Path("/tmp/brainprep-data")
datadir.mkdir(parents=True, exist_ok=True)
dataset = AnatomicalDataset(datadir)
data = Bunch(
    sub01=dataset.fetch(
        subject="01",
        modality="T1w",
        dtype="cross_sectional",
    ),
    sub02=dataset.fetch(
        subject="02",
        modality="T1w",
        dtype="cross_sectional",
    ),
)
print(data)


# %%
# Analysis
# --------
# 
# Let's now perform the preprocessing using BrainPrep.
# As with many tutorials, we won't execute the code directly here.
# However, feel free to set the 'dryrun' configuration to False
# to actually run each step and generate results on disk.


from brainprep.workflow import (
    brainprep_quality_assurance,
    brainprep_group_quality_assurance,
)
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-qa")
outdir.mkdir(parents=True, exist_ok=True)
with Config(dryrun=True, verbose=True):
    for subject_data in data.values():
        report = RSTReport()
        brainprep_quality_assurance(
            image_files=[subject_data.anat],
            output_dir=outdir,
            keep_intermediate=True,
        )
        print(report)
    report = RSTReport()
    brainprep_group_quality_assurance(
        modalities=["T1w"],
        output_dir=outdir,
    )
    print(report)


# %%
# Container
# ---------
# 
# Let's now perform this preprocessing using the BrainPrep container.

homedir = Path("/tmp/brainprep-home")
homedir.mkdir(parents=True, exist_ok=True)
devcodedir = Path(__file__).parent.parent
cmd = [
    "singularity",
    "run",
    "shell",
    "--bind", f"{devcodedir}:/opt/brainprep",
    "--bind", f"{datadir}:/data",
    "--bind", f"{outdir}:/out",
    "--home", f"{homedir}",
    "--env", "PYTHONPATH=/opt/brainprep",
    "--env", "PREPEND_PATH=/opt/brainprep/brainprep/scripts",
    "--containall",
    "docker://neurospin/brainprep-qa:latest",
    "brainprep", "subject-level-qa",
    "/data",
    "--image-files", f"[{data.sub01.anat}]",
    "--output-dir", "/out",
]
print(" ".join(cmd))
