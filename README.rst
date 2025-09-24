**Usage**

.. image:: https://img.shields.io/badge/python-3.12-blue
    :target: https://github.com/AGrigis/pysphinxdoc
    :alt: Python Version

.. image:: https://img.shields.io/badge/License-CeCILL--B-blue.svg
    :target: http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
    :alt: License

.. image:: https://img.shields.io/badge/Powered%20by-CEA%2FNeuroSpin-blue.svg
    :target: https://joliot.cea.fr/drf/joliot/Pages/Entites_de_recherche/NeuroSpin.aspx
    :alt: Powered By

**Development**

.. image:: https://coveralls.io/repos/neurospin-deepinsight/brainprep/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/neurospin-deepinsight/brainprep
    :alt: Code Coverage

.. image:: https://github.com/neurospin-deepinsight/brainprep/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/neurospin-deepinsight/brainprep/actions
    :alt: Testing

.. image:: https://github.com/neurospin-deepinsight/brainprep/actions/workflows/pep8.yml/badge.svg
    :target: https://github.com/neurospin-deepinsight/brainprep/actions
    :alt: Github Actions Linter Status

.. image:: https://github.com/neurospin-deepinsight/brainprep/actions/workflows/documentation.yml/badge.svg
    :target: https://neurospin-deepinsight.github.io/brainprep/stable
    :alt: Github Actions Doc Build Status


**Release**

.. image:: https://badge.fury.io/py/brainprep.svg
    :target: https://pypi.org/project/brainprep
    :alt: Pypi Package

.. image:: https://img.shields.io/docker/pulls/neurospin/brainprep-anat
    :target: https://hub.docker.com/r/neurospin/brainprep-anat
    :alt: Docker Anat

.. image:: https://img.shields.io/docker/pulls/neurospin/brainprep-mriqc
    :target: https://hub.docker.com/r/neurospin/brainprep-mriqc
    :alt: Docker MRI QC

.. image:: https://img.shields.io/docker/pulls/neurospin/brainprep-fmriprep
    :target: https://hub.docker.com/r/neurospin/brainprep-fmriprep
    :alt: Docker fMRI Prep

.. image:: https://img.shields.io/docker/pulls/neurospin/brainprep-dmriprep
    :target: https://hub.docker.com/r/neurospin/brainprep-dmriprep
    :alt: Docker dMRI Prep


brainprep
=========


What is ``brainprep``?
======================

``brainprep`` is a comprehensive toolbox designed to streamline the
preprocessing of brain MRI data for deep learning applications. It offers a
suite of standardized scripts tailored for anatomical, functional, and
diffusion magnetic resonance imaging (MRI), ensuring consistent and
high-quality data preparation across studies. In addition to preprocessing
pipelines, brainprep includes robust quality control (QC) routines to help
researchers assess data integrity and detect potential artifacts or anomalies.

To explore the full range of available workflows, simply run the following
command in your terminal:

.. code-block:: bash

    brainprep --help

Each workflow is encapsulated within a containerized environment, promoting
reproducibility and simplifying deployment across different systems.
By leveraging container technology, brainprep minimizes dependency issues
and ensures that preprocessing steps can be executed reliably, regardless of
the underlying hardware or operating system.

Whether you're working on large-scale neuroimaging datasets or developing
novel deep learning models for brain analysis, brainprep provides a modular,
scalable, and reproducible foundation to accelerate your research.

   
Important Links
===============

- Official source code repo: https://github.com/neurospin-deepinsight/brainprep
- HTML documentation (stable release): https://neurospin-deepinsight.github.io/brainprep/stable
- HTML documentation (dev): https://neurospin-deepinsight.github.io/brainprep/dev


Install
=======

Latest release
--------------

**1. Setup a virtual environment**

We recommend that you install ``brainprep`` in a virtual Python environment,
either managed with the standard library ``venv`` or with ``conda``.
Either way, create and activate a new python environment.

With ``venv``:

.. code-block:: bash

    python3 -m venv /<path_to_new_env>
    source /<path_to_new_env>/bin/activate

Windows users should change the last line to ``\<path_to_new_env>\Scripts\activate.bat``
in order to activate their virtual environment.

With ``conda``:

.. code-block:: bash

    conda create -n brainprep python=3.12
    conda activate brainprep

**2. Install brainprep with pip**

Execute the following command in the command prompt / terminal
in the proper python environment:

.. code-block:: bash

    python3 -m pip install -U brainprep


Check installation
------------------

Try importing brainprep in a Python / iPython session:

.. code-block:: python

    import brainprep

If no error is raised, you have installed brainprep correctly.


Dependencies
============

The required dependencies to use the software are listed
in the file `pyproject.toml <https://github.com/neurospin-deepinsight/brainprep/blob/main/pyproject.toml>`_.


Citation
========

There is no paper published yet about ``brainprep``.
We suggest that you aknowledge the brainprep team or reference to the code
repository. Thank you.

.. code-block:: text

    @misc{brainprep,
        title = {{BrainPrep source code (Version 1.0.0)}},
        author = {Grigis, Antoine and Victor, Julie and Dorval, Loic and Duchesnay, Edouard},
        url = {https://github.com/neurospin-deepinsight/brainprep},
    }
