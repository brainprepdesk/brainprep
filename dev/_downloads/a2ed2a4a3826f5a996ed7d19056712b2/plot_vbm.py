"""
VBM pre-processing 
==================

Simple example.

Example on how to run the VBM pre-processing using brainprep.
See :ref:`user guide <vbm>` for details.

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

datadir = str(datadir)
outdir = "/tmp/brainprep-out"
homedir = "/tmp/brainprep-home"
t1w_file = str(data["sub-01"])
cmd = [
    f"SINGULARITYENV_FS_LICENSE={license}",
    "apptainer", "run",
    "--bind", f"{datadir}:/data",
    "--bind", f"{outdir}:/out",
    "--home", homedir,
    "--cleanenv",
    "docker://neurospin/brainprep-anat:latest",
    "brainprep", "vbm",
    t1w_file.replace(datadir, "/data"),
    "/out",
]
print(" ".join(cmd))
