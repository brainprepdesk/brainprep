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
# Let's now perform preprocessing using the BrainPrep.
# As with many tutorials, we won't execute the code directly here.
# However, feel free to set the 'dryrun' configuration to False
# to actually run each step and generate results on disk.


from brainprep.workflow import (
    brainprep_quality_assurance,
    brainprep_group_quality_assurance,
)
from brainprep.wrappers import WrapperConfig
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-qa")
outdir.mkdir(parents=True, exist_ok=True)
with WrapperConfig(dryrun=True):
    for subject in data:
        report = RSTReport()
        brainprep_quality_assurance(
            image_files=[data[subject]],
            output_dir=outdir,
            keep_intermediate=True,
        )
        print(report)
    report = RSTReport()
    brainprep_group_quality_assurance(
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
subject = "sub-01"
cmd = [
    "apptainer",
    "run",
    "--bind", f"{datadir}:/data",
    "--bind", f"{outdir}:/out",
    "--home", f"{homedir}",
    "--cleanenv",
    "docker://neurospin/brainprep-mriqc:latest",
    "brainprep", "subject-level-qa",
    "/data",
    "--image-files", f"[{data[subject]}]",
    "--output-dir", "/out",
]
print(" ".join(cmd))
