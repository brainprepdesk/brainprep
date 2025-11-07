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
   - Example path: `longitudinal/sub-001/`.

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
    │   ├── sub-001/
    │   └── sub-002/
    ├── logs/
    │   └── report.rst
    └── dataset_description.json
