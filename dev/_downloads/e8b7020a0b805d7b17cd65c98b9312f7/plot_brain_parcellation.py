"""
Brain Parcellation
==================

Simple example.

Example on how to run the brain parcellation pre-processing using BrainPrep.
See :ref:`user guide <brain_parcellation>` for details.

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
    brainprep_brainparc,
    brainprep_group_brainparc,
    brainprep_longitudinal_brainparc,
)
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-brainparc")
outdir.mkdir(parents=True, exist_ok=True)
with Config(dryrun=True, verbose=True):
    for subject_data in data.values():
        for t1_file in [subject_data.anat1, subject_data.anat2]:
            outputs = brainprep_brainparc(
                t1_file=t1_file,
                template_dir=(datadir / "fsaverage_sym"),
                output_dir=outdir,
                do_lgi=False,
                wm_file=(datadir / "deprecated"),
                keep_intermediate=True,
            )
            (outputs.subject_dir / "stats").mkdir(parents=True, exist_ok=True)
    outputs = brainprep_group_brainparc(
        output_dir=outdir,
        euler_threshold=-217,
        keep_intermediate=True,
    )
    outputs = brainprep_longitudinal_brainparc(
        t1_files=[subject_data.anat1, subject_data.anat2],
        output_dir=outdir,
        keep_intermediate=True,
    )
    for subject_dir in outputs.subject_dirs:
        (subject_dir / "stats").mkdir(parents=True, exist_ok=True)
    outputs = brainprep_group_brainparc(
        output_dir=outdir,
        euler_threshold=-217,
        longitudinal=True,
        keep_intermediate=True,
    )


# %%
# Container
# ---------
# 
# Let's now perform this preprocessing using the BrainPrep container.
