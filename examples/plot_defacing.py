"""
Defacing
========

Simple example.

Example on how to run the defacing pre-processing using BrainPrep.
See :ref:`user guide <defacing>` for details.

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
print(data)


# %%
# Analysis
# --------
# 
# Let's now perform preprocessing using the BrainPrep.
# As with many tutorials, we won't execute the code directly here.
# However, feel free to set the 'dryrun' configuration to False
# to actually run each step and generate results on disk.


from brainprep.workflow import brainprep_defacing
from brainprep.config import Config
from brainprep.reporting import RSTReport

outdir = Path("/tmp/brainprep-defacing")
outdir.mkdir(parents=True, exist_ok=True)
report = RSTReport()
with Config(dryrun=True, verbose=True):
    brainprep_defacing(
        t1_file=data.anat,
        output_dir=outdir,
        keep_intermediate=True,
    )
print(report)


# %%
# Container
# ---------
# 
# Let's now perform preprocessing using the BrainPrep container.
#
# Coming soon!

