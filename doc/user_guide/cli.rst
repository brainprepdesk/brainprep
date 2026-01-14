.. _cli:

CLI
===

``brainprep`` is a command-line interface for running brain imaging
preprocessing workflows.

Usage
-----

.. code-block:: bash

    brainprep [WORKFLOW] [PARMS]

``[WORKFLOW]`` specifies which preprocessing pipeline to run, and ``[PARAMS]``
are the input arguments associated with that workflow.

Use ``brainprep --help`` to list all available workflows, or
``brainprep [WORKFLOW] --help`` to display the parameters required by a
specific workflow.
