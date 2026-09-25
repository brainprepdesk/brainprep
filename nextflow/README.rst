Nextflow Execution
==================

In order to run ``brainprep`` using `NextFlow <https://www.nextflow.io/>`_,
you need to have NextFlow installed. One of the easiest ways to install
NextFlow is by using a `Pixi environment <https://pixi.prefix.dev/>`_. Below
are the steps to set up your environment and run ``brainprep``:


Install Pixi
------------

If you haven't already installed Pixi, you can do so by following the
instructions on the `Pixi documentation <https://pixi.prefix.dev/>`_.


Create a Pixi Environment
-------------------------

Navigate to the directory where you want to create your Pixi environment.
Copy the **pixi.toml** file from the provided folder into your desired
directory. This file contains the necessary configurations for your
environment. Then, run:

.. code-block:: bash

    pixi shell

This will set up your environment and start a new shell session.


Run NextFlow
------------

With your Pixi environment activated, you can now run NextFlow commands.
To run ``brainprep``, go to the directory containing the **brainprep.nf**
NextFlow script file and use the following command to list the availalbe
workflows and help:

.. code-block:: bash

    nextflow run brainprep.nf

Then run the qausiraw workflow adapt the following command:

.. code-block:: bash

    nextflow run brainprep.nf
    --workflow first_level_quasiraw
    --data <CSV_DATA_FILE>
    --rtype flow
    --outdir <OUTDIR>
    --dryrun
    -profile standard

