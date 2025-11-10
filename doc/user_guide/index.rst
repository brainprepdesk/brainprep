.. _user_guide:

==========
User guide
==========

This user guide is especially directed towards grad students
with a background in computer science.
However, less or more advanced readers can also find interesting
pieces of information throughout the guide.

Table of contents
=================

.. toctree::
   :numbered:
   :maxdepth: 1

   quality_assurance.rst
   defacing.rst
   quasiraw.rst
   vbm.rst
   brain_parcellation.rst
   dmriprep.rst
   tbss.rst
   fmriprep.rst
   reporting.rst
   glossary.rst

Data Organization Ontology
==========================

The following ontology is used to structure and organize data on disk for
neuroimaging analyses. The system supports three hierarchical levels of
analysis: **subject-level**, **group-level**, and **longitudinal**.
Each level corresponds to a specific directory structure and naming convention
to ensure consistency, traceability, and compatibility with processing
pipelines.

Analysis Levels
---------------

1. **Subject-Level Analysis**
   - Data is organized per individual subject.
   - Root directory: `subjects/`.
   - Each subject has a dedicated subdirectory named using a unique
     identifier (e.g., `sub-001`, `sub-002`).
   - Within each subject directory, session-specific data is stored in
     subdirectories following the BIDS convention (e.g., `ses-01`, `ses-02`).
   - Example path: `subjects/sub-001/ses-01/`.

2. **Group-Level Analysis**
   - Data is aggregated across subjects for group-level processing.
   - Root directory: `qc/`, `morphometry/`, `statistic/`.
   - Each group-level analysis type has its own named directory:
     - `qc/` for quality control metrics.
     - `morphometry/` for structural measurements.
     - `statistic/` for statistical outputs.
   - These directories contain results derived from multiple subjects and
     sessions, often in tabular or summary formats.

3. **Longitudinal Analysis**
   - Data is structured to support longitudinal studies across multiple
     timepoints.
   - Root directory: `longitudinal/`.
   - Contains subject-wise data aggregated across sessions and timepoints.
   - May include harmonized metrics, trajectory models, or longitudinal
     statistical outputs.
   - Example path: `longitudinal/subject/sub-001/ses-01/`.

Metadata and Logs
-----------------

A `dataset_description.json` file is placed at the root of the dataset. This
file documents:
- The tool or pipeline used for processing.
- The version of the tool.
- The container technology used (Docker image), if applicable.

A `logs/` directory is maintained at the root level to store logs from all
processing steps. One key log file is `report.rst`, which provides a
comprehensive report of:
- All processing steps executed.
- Input and output file locations for each step.
- Runtime information for each step.

Directory Overview
------------------

The overall structure can be visualized as:

::

    data_root/
    ├── subjects/
    │   ├── sub-001/
    │   │   ├── ses-01/
    │   │   └── ses-02/
    │   └── sub-002/
    │       └── ses-01/
    ├── qc/
    ├── morphometry/
    ├── statistic/
    ├── longitudinal/
    │   ├── subjects
    │   │   ├── sub-001/
    │   │   └── sub-002/
    │   └── qc
    ├── logs/
    │   └── report.rst
    └── dataset_description.json


Wrappers for Interface Construction
===================================

Overview
--------

In the workflow system, interfaces are built using **wrappers** that encapsulate
tools and expose them in a standardized way. These wrappers serve as the
building blocks of workflows, enabling seamless integration and execution of
diverse tools.

There are two primary types of wrappers:

1. **Command-Line Wrappers**
2. **Python Wrappers**

Wrapper Implementation
----------------------

All wrappers are implemented as **Python decorators**, which provide a clean
and expressive way to define interfaces.
**Benefits of Using Decorators:**

- Simplifies interface definition
- Promotes modular and reusable code
- Enables automatic metadata extraction
- Supports consistent execution patterns

Command-Line Wrappers
---------------------

Command-line wrappers encapsulate tools that are available on the system and
can be executed via the shell. These wrappers provide a structured interface
to interact with external binaries, scripts, or utilities.

**Features:**

- Execute system-level tools using subprocesses.
- Capture standard output and error streams.
- Support for input/output file management.
- Parameter mapping to command-line arguments.

**Return Value:**

A command-line wrapper returns:

- A **command** or **list of commands** to be executed.
- A **tuple of generated output paths**.

Python Wrappers
---------------

Python wrappers encapsulate tools implemented directly in Python. These
wrappers allow for tighter integration with the workflow engine and enable
more complex logic and data manipulation.

**Features:**

- Direct invocation of Python functions or classes.
- Access to in-memory data structures.
- Easier debugging and testing.
- Richer error handling and logging.

**Return Value:**

A Python wrapper returns:

- A **tuple of generated output paths**.

Usage in Workflows
------------------

Both types of wrappers are used to define **interfaces**—modular units of
computation that can be chained together in workflows. By abstracting
tool-specific details, wrappers promote reusability, portability, and clarity
in workflow design.

.. note::

   Wrappers should be designed with clear input/output specifications and
   robust error handling to ensure reliability across diverse execution
   environments.

