Developer Tools
===============

This document describes the layout and purpose of the developer-oriented
tools included in this repository. These tools are not part of the
installed Python package and are intended exclusively for contributors
working on the project.


Overview
--------

The repository contains two dedicated directories for internal tooling:

- ``build/``: scripts and utilities used for building, packaging, or
  distributing the project.
- ``scaling/``: scripts and utilities used for running or adapting the
  project on high-performance computing (HPC) infrastructures.

These directories help keep the main Python package clean and ensure that
developer utilities remain organized and discoverable.


``build/`` Directory
--------------------

The ``build/`` directory contains scripts and helper utilities used for
building or packaging the project. These scripts are not installed with
the Python package and are intended for maintainers.

It includes:

- ``build/build_cli.py``: the main build configuration script.  
  Running ``build_cli.py build <params>`` generates a directory tree and
  aggregates creation and test instructions into a ``commands`` file.

These tools are typically invoked manually by developers or by
continuous integration (CI) workflows during release preparation,
packaging, or automated testing.


``scaling/`` Directory
----------------------

The ``scaling/`` directory contains tools related to scalability and
execution on HPC environments. These scripts are useful for adapting or
running BrainPrep workflows on clusters, job schedulers, or distributed
compute infrastructures.

Typical contents include:

- coming soon.

These tools are not part of the public API and are intended for internal
use by contributors who work on scaling, benchmarking, or optimizing the
project for large datasets or distributed environments.
