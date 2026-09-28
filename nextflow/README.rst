Nextflow Execution Guide
========================

This guide provides step-by-step instructions for running ``brainprep`` using
`NextFlow <https://www.nextflow.io/>`_.

Prerequisites
-------------

- Install `NextFlow <https://www.nextflow.io/>`_
- Set up a `Pixi environment <https://pixi.prefix.dev/>`_ (recommended)

Setting Up the Environment
--------------------------

Install Pixi
~~~~~~~~~~~~

If you haven't already installed Pixi, follow the instructions on
the `Pixi documentation <https://pixi.prefix.dev/>`_.

Create a Pixi Environment
~~~~~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the directory where you want to create your Pixi environment.
2. Copy the **pixi.toml** file from the provided folder into your desired
   directory.
3. Run the following command to set up your environment and start a new shell
   session:

.. code-block:: bash

    pixi shell

Running NextFlow
----------------

With your Pixi environment activated, you can now run NextFlow commands.

Basic Commands
~~~~~~~~~~~~~~

To run ``brainprep``, go to the directory containing the **brainprep.nf**
NextFlow script file and use the following command to list the available
workflows and help:

.. code-block:: bash

    nextflow run brainprep.nf

Running the Quasiraw Workflow
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To run the quasiraw workflow, adapt the following command:

.. code-block:: bash

    nextflow run brainprep.nf \
        --workflow subject_level_quasiraw \
        --data <CSV_DATA_FILE> \
        --rtype flow \
        --outdir <OUTDIR> \
        --dryrun \
        -profile standard

Using Apptainer Profile
~~~~~~~~~~~~~~~~~~~~~~~

If using an Apptainer profile, you can export the following environment
variables:

.. code-block:: bash

    export APPTAINER_CACHEDIR=<CACHE_DIR>
    export APPTAINER_TMPDIR=<TMP_DIR>
