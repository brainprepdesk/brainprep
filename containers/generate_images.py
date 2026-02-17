#! /usr/bin/env python3
##########################################################################
# NSAp - Copyright (C) CEA, 2022
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import glob
import os
import shutil
from datetime import date

import fire


def main(working_dir):
    """ Parse available Docker files and generates associated images.

    Parameters
    ----------
    working_dir: str
        the directory where the images will be generated.
    """
    image_dir = os.path.dirname(os.path.abspath(__file__))
    today = date.today()
    today = today.strftime("%d%m%Y")
    for path in glob.glob(os.path.join(image_dir, "Dockerfile.*")):
        basename = os.path.basename(path)
        name = basename.split(".", 1)[1]
        if name in ("dmriprep", ):
            continue
        dest_dir = os.path.join(working_dir, name)
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        tmp_dir = os.path.join(dest_dir, "tmp")
        cache_dir = os.path.join(dest_dir, "cache")
        for _path in (tmp_dir, cache_dir):
            if not os.path.isdir(_path):
                os.mkdir(_path)
        shutil.copy(path, os.path.join(dest_dir, "Dockerfile"))
        cmds = f"export WDIR={dest_dir}\n"
        cmds += "cd $WDIR\n"
        cmds += f"export IMG={name}\n"
        cmds += "sudo docker build --no-cache --tag brainprep-$IMG .\n"
        cmds += "sudo docker images\n"
        cmds += (f"sudo docker save -o brainprep-$IMG-{today}.tar "
                 f"brainprep-$IMG:{today}\n")
        cmds += f"sudo chmod 755 brainprep-$IMG-{today}.tar\n"
        cmds += ("sudo SINGULARITY_TMPDIR=$WDIR/tmp SINGULARITY_CACHEDIR="
                 f"$WDIR/cache singularity build brainprep-$IMG-{today}.simg "
                 f"docker-archive://brainprep-$IMG-{today}.tar\n"
                 )
        cmds += f"singularity inspect brainprep-$IMG-{today}.simg\n"
        cmds_file = os.path.join(dest_dir, "commands")
        with open(cmds_file, "w") as of:
            of.write(cmds)
        print(f"Ready to execute: {cmds_file}")

    for path in glob.glob(os.path.join(image_dir, "Singularity.*")):
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        name = basename.split(".", 1)[1]
        docker_path = os.path.join(dirname, f"Dockerfile.{name}")
        if not os.path.isfile(docker_path):
            raise ValueError(f"Please define the '{docker_path}' docker file associated "
                             "to the singularity recipe.")
        dest_dir = os.path.join(working_dir, name)
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        home_dir = os.path.join(dest_dir, "home")
        tmp_dir = os.path.join(dest_dir, "tmp")
        cache_dir = os.path.join(dest_dir, "cache")
        for _path in (tmp_dir, cache_dir, home_dir):
            if not os.path.isdir(_path):
                os.mkdir(_path)
        shutil.copy(path, os.path.join(dest_dir, "Singularity"))
        shutil.copy(docker_path, os.path.join(dest_dir, "Dockerfile"))
        cmds = f"export WDIR={dest_dir}\n"
        cmds += "cd $WDIR\n"
        cmds += f"export IMG={name}\n"
        cmds += ("sudo SINGULARITY_TMPDIR=$WDIR/tmp "
                 "SINGULARITY_CACHEDIR=$WDIR/cache "
                 "SINGULARITY_HOME=$WDIR/home "
                 f"singularity build brainprep-$IMG-{today}.simg Singularity\n"
                 )
        cmds += f"singularity sif list brainprep-$IMG-{today}.simg\n"
        cmds += (f"singularity sif dump 4 brainprep-$IMG-{today}.simg "
                 "> data.squash\n")
        cmds += "unsquashfs -dest data data.squash\n"
        cmds += "docker build --tag brainprep-$IMG .\n"
        cmds += "sudo docker images\n"
        cmds += (f"sudo docker save -o brainprep-$IMG-{today}.tar "
                 f"brainprep-$IMG:{today}\n")
        cmds += f"sudo chmod 755 brainprep-$IMG-{today}.tar\n"
        cmds_file = os.path.join(dest_dir, "commands")
        with open(cmds_file, "w") as of:
            of.write(cmds)
        print(f"Ready to execute: {cmds_file}")


if __name__ == "__main__":

    fire.Fire(main)
