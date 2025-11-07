"""
VBM pre-processing 
==================

Simple example.

Example on how to run the VBM pre-processing using BrainPrep.
See :ref:`user guide <vbm>` for details.

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
        dtype="longitudinal",
    ),
    sub02=dataset.fetch(
        subject="02",
        modality="T1w",
        dtype="longitudinal",
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
    brainprep_group_vbm,
    brainprep_longitudinal_vbm,
    brainprep_vbm,
)
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-vbm")
outdir.mkdir(parents=True, exist_ok=True)
with Config(dryrun=True, verbose=True):
    for subject_data in data.values():
        report = RSTReport()
        outputs = brainprep_vbm(
            t1_file=subject_data.anat1,
            output_dir=outdir,
        )
        # print(report)
    outputs = brainprep_longitudinal_vbm(
        t1_files=[data.sub01.anat1, data.sub01.anat2],
        model=1,
        output_dir=outdir,
    )
    outputs = brainprep_group_vbm(
        output_dir=outdir,
    )
    outputs = brainprep_group_vbm(
        output_dir=outdir,
        longitudinal=True,
    )


# %%
# Container
# ---------
# 
# Let's now perform this preprocessing using the BrainPrep container.
