"""
fMRI Pre-Processings
====================

Simple example.

Example on how to run the fMRI pre-processing using BrainPrep.
See :ref:`user guide <fmriprep>` for details.

Data
----

Let's first get some anatomical/functional data.
"""

from pathlib import Path
from brainprep.datasets import MultiModalDataset

datadir = Path("/tmp/brainprep-data")
datadir.mkdir(parents=True, exist_ok=True)
dataset = MultiModalDataset(datadir)
data = dataset.fetch(
    subject="01",
    modality="func",
    session="01",
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
    brainprep_fmriprep,
)
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-fmriprep")
outdir.mkdir(parents=True, exist_ok=True)
with Config(dryrun=True, verbose=True):
    report = RSTReport()
    brainprep_fmriprep(
        t1_file=data.anat,
        func_files=[data.func],
        dataset_description_file=data.description,
        freesurfer_dir="/my/freesurfer/directory",
        output_dir=outdir,
        keep_intermediate=True,
    )
    print(report)


# %%
# Container
# ---------
# 
# Let's now perform this preprocessing using the BrainPrep container.
