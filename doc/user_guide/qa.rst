.. _qa:

Quality Assurance
=================

Introduction
------------

QA stands for Quality Assurance, and in the context of MRI, it refers to the
process of evaluating and maintaining the quality of MRI data.
Using QA in MRI data is a powerful way to ensure your neuroimaging dataset is
clean, reliable, and ready for analysis.
QA helps standardize datasets, making it easier to replicate findings and
share data with confidence.

Description
-----------

**Steps**: MRIQC :footcite:p:`esteban2017mriqc` is used to automatically
extracts image quality metrics (IQMs)
from structural (T1w, T2w), functional (BOLD), and diffusion (EPI) MRI scans.
The objective is to detect artifacts, inconsistencies, and outliers without
manually inspecting every image. MRIQC computes dozens of metrics like
signal-to-noise ratio (SNR), contrast-to-noise ratio (CNR), entropy focus
criterion (EFC), and motion parameters. These metrics help identify scans
with poor quality due to motion, scanner issues, or acquisition errors.
It generates HTML reports with side-by-side visualizations of each scan,
making it easy to spot problems like ghosting, blurring, or head motion.
Group-level reports help compare quality across subjects and sites.

**Quality control**: We exclude data that MRIQC flags as deviating significantly
from the group.

References
----------

.. footbibliography::
