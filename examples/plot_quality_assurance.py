"""
Quality Assurance
=================

Simple example.

Example on how to run the quality assurance pre-processing using brainprep.
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
print(data)


# %%
# Container
# ---------
# 
# Now let's perform the pre-processing on a brainprep container.


datadir = str(datadir)
outdir = "/tmp/brainprep-out"
homedir = "/tmp/brainprep-home"
license = "/out/license.txt"
cmd = [
    "apptainer", "run",
    "--bind", f"{datadir}:/data",
    "--bind", f"{outdir}:/out",
    "--home", homedir,
    "--cleanenv",
    "docker://neurospin/brainprep-mriqc:latest",
    "brainprep", "qa",
    "/data",
    "sub-unknown",
    "--outdir", "/out",
    "--workdir", "/out/work"]
print(" ".join(cmd))
