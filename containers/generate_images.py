##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

# System import
import os
import glob
import fire
import shutil
from datetime import date


def main(working_dir):
    """ Parse available Docker files and generates associated recipes.

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
        # create destination directory
        dest_dir = os.path.join(working_dir, name)
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        # add tmp and cache dir
        tmp_dir = os.path.join(dest_dir, "tmp")
        cache_dir = os.path.join(dest_dir, "cache")
        for _path in (tmp_dir, cache_dir):
            if not os.path.isdir(_path):
                os.mkdir(_path)
        # copy the files in brainprep/containers/resources
        resources = os.path.join(os.path.dirname(path), "resources", "*")
        for resource_file in glob.glob(resources):
            shutil.copy(resource_file, dest_dir)
        # copy the appropriate Dockerfile
        shutil.copy(path, os.path.join(dest_dir, "Dockerfile"))
        # create the commands list to run
        cmds = "export WDIR={}\n".format(dest_dir)
        cmds += "cd $WDIR\n"
        cmds += "export IMG={}\n".format(name)
        cmds += "sudo docker build --no-cache --tag brainprep-$IMG .\n"
        cmds += "sudo docker images\n"
        cmds += ("sudo docker save -o brainprep-$IMG-{0}.tar "
                 "brainprep-$IMG:latest\n".format(today))
        cmds += "sudo chmod 755 brainprep-$IMG-{}.tar\n".format(today)
        cmds += ("sudo SINGULARITY_TMPDIR=$WDIR/tmp SINGULARITY_CACHEDIR="
                 "$WDIR/cache singularity build brainprep-$IMG-{}.simg "
                 "docker-archive://brainprep-$IMG-{}.tar\n"
                 .format(today, today))
        cmds += "singularity inspect brainprep-$IMG-{}.simg\n".format(today)
        cmds_file = os.path.join(dest_dir, "commands")
        with open(cmds_file, "wt") as of:
            of.write(cmds)
        print("Ready to execute: {}".format(cmds_file))


if __name__ == "__main__":

    fire.Fire(main)
