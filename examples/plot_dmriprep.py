"""
fMRI Pre-Processings
====================

Simple example.

Example on how to run the dMRI pre-processing using BrainPrep.
See :ref:`user guide <dmriprep>` for details.

Data
----

Let's first get some anatomical/diffusion data.
"""

from pathlib import Path
from brainprep.datasets import MultiModalDataset

datadir = Path("/tmp/brainprep-data")
datadir.mkdir(parents=True, exist_ok=True)
dataset = MultiModalDataset(datadir)
data = dataset.fetch(
    subject="01",
    modality="dwi",
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
    brainprep_dmriprep,
    brainprep_group_dmriprep,
)
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-dmriprep")
outdir.mkdir(parents=True, exist_ok=True)
with Config(dryrun=True, verbose=True):
    report = RSTReport()
    brainprep_dmriprep(
        t1_file=data.anat,
        dwi_file=data.dwi,
        bvec_file=data.bvec,
        bval_file=data.bval,
        output_dir=outdir,
        keep_intermediate=True,
    )
    print(report)
    brainprep_group_dmriprep(
        output_dir=outdir,
    )


# %%
# Container
# ---------
# 
# Let's now perform this preprocessing using the BrainPrep container.
