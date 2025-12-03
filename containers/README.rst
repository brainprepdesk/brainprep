Docker Container
================

In order to run ``brainprep`` in a Docker container, Docker must be
`installed <https://docs.docker.com/engine/installation>`_.

Recipies
--------

Docker recipies are automatically generated using
`neurodocker <https://github.com/ReproNim/neurodocker>`_. First, install
``neurodocker``:

.. code-block:: bash

    pip install neurodocker

Then, generate the new recipies (one per workflow type):

.. code-block:: bash

    neurodocker generate docker \
        --base-image nipreps/mriqc:24.0.2 \
        --pkg-manager apt \
        --label description="brainprep quality assesssment" version="2.0" \
        --yes \
        --entrypoint python3 \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.qa

    neurodocker generate docker \
        --base-image ubuntu:24.04 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --fsl version=6.0.7.18 \
          install_path=/opt/fsl-6.0.7.18 \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.defacing

    neurodocker generate docker \
        --base-image ubuntu:24.04 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --fsl version=6.0.7.18 \
          install_path=/opt/fsl-6.0.7.18 \
        --freesurfer version=7.4.1 \
          install_path=/opt/freesurfer-7.4.1 \
          exclude_paths="average/mult-comp-cor lib/cuda lib/qt subjects/V1_average subjects/bert subjects/cvs_avg35 subjects/cvs_avg35_inMNI152 subjects/fsaverage3 subjects/fsaverage4 subjects/fsaverage5 subjects/fsaverage6 subjects/fsaverage_sym trctrain" \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.quasiraw

    neurodocker generate docker \
        --base-image ubuntu:24.04 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --matlabmcr version=2023b \
        --cat12 version=12.9_R2023b \
          install_path=/opt/cat12-12.9_R2023b \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.vbm

    neurodocker generate docker \
        --base-image ubuntu:24.04 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --freesurfer version=7.4.1 \
          install_path=/opt/freesurfer-7.4.1 \
          exclude_paths="diffusion docs fsfast average/mult-comp-cor lib/cuda lib/qt subjects/V1_average subjects/bert subjects/cvs_avg35 subjects/cvs_avg35_inMNI152 subjects/fsaverage3 subjects/fsaverage4 subjects/fsaverage5 subjects/fsaverage6 subjects/fsaverage_sym trctrain" \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.brainparc

    neurodocker generate docker \
        --base-image ubuntu:24.04 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --fsl version=6.0.7.18 \
          install_path=/opt/fsl-6.0.7.18 \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.tbss

    neurodocker generate docker \
        --base-image nipreps/fmriprep:25.2.3 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.fmriprep

    neurodocker generate docker \
        --base-image pennlinc/qsiprep:1.0.2 \
        --pkg-manager apt \
        --yes \
        --entrypoint python3 \
        --run-bash "pip install git+https://github.com/neurospin-deepinsight/brainprep.git@dev" \
        > Dockerfile.dmriprep

.. note::

    Generated recipes are manually fine‑tuned afterward.

  
Creation
--------

The **generate_images.py** configuration script generates a tree structure
and aggregates the creation instructions in a **commands** file.
