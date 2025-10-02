"""
Defacing
========

Simple example.

Example on how to run the defacing pre-processing using brainprep.
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
# Container
# ---------
# 
# Now let's perform the pre-processing on a brainprep container.

from brainprep.workflow import brainprep_deface

brainprep_deface(
    anatomical=data["sub-01"],
    outdir="/tmp/brainprep-defacinng",
)
