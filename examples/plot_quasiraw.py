"""
Quasi-RAW pre-processing
========================

Simple example.

Example on how to run the brain parcellation pre-processing using BrainPrep.
See :ref:`user guide <quasiraw>` for details.

Data
----

Let's first get some anatomical data.
"""

from pathlib import Path
from brainprep.datasets import AnatomicalDataset

datadir = Path("/tmp/brainprep-data")
datadir.mkdir(parents=True, exist_ok=True)
dataset = AnatomicalDataset(datadir)
data = dataset.fetch(
    subject="01",
    modality="T1w",
    dtype="cross_sectional",
)
data.update(
    dataset.fetch(
        subject="02",
        modality="T1w",
        dtype="cross_sectional",
    )
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
    brainprep_quasiraw,
    brainprep_quasiraw_qc,
)
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-quasiraw")
outdir.mkdir(parents=True, exist_ok=True)
with Config(dryrun=True, verbose=True):
    for subject in data:
        report = RSTReport()
        brainprep_quasiraw(
            anatomical_file=data[subject],
            output_dir=outdir,
            keep_intermediate=True,
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
subject = "sub-01"
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
    "docker://neurospin/brainprep-quasiraw:latest",
    "brainprep", "quasiraw",
    "/data",
    "--image-files", f"[{data[subject]}]",
    "--output-dir", "/out",
]
print(" ".join(cmd))
