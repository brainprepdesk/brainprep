"""
mriqc quality control use case
==============================

Credit: A Grigis

Example on how to run the mriqc quality control using the brainprep
Singularity container.
"""
# sphinx_gallery_thumbnail_path = '_static/carousel/mriqc.png'

import os

from brainrise.datasets import MRIToyDataset

#############################################################################
# Please tune these parameters.

DATADIR = "/tmp/brainprep-data"
OUTDIR = "/tmp/brainprep-out"
WORKDIR = "/tmp/brainprep-out/work"
HOMEDIR = "/tmp/brainprep-home"
SCRIPT = "mriqc"
SIMG = "/volatile/nsap/brainprep/mriqc/brainprep-mriqc-latest.simg"

for path in (DATADIR, OUTDIR, HOMEDIR, WORKDIR):
    if not os.path.isdir(path):
        os.mkdir(path)
dataset = MRIToyDataset(root=DATADIR)
cmd = ["singularity", "run", "--bind", f"{DATADIR}:/data",
       "--bind", f"{OUTDIR}:/out", "--home", HOMEDIR, "--cleanenv",
       SIMG,
       "brainprep", SCRIPT,
       "/data",
       "sub-unknown",
       "--outdir", "/out",
       "--workdir", "/out/work"]

#############################################################################
# You can now execute this command.

print(" ".join(cmd))

