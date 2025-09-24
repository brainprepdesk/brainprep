.. _quasiraw:

Quasi RAW
=========

.. image:: ../images/preproc-quasiraw.png
   :width: 50%
   :align: center
   

Introduction
------------

Quasi-raw preprocessing of T1w MRI data refers to minimal, standardized steps
applied to raw imaging data before deeper analysis. Here, a simple affine
(no shearing) registration to the MNI template space.

Description
-----------

**Steps**: Minimally preprocessed data is generated using ANTS
:footcite:p:`avants2009ants` bias field correction, FSL FLIRT
:footcite:p:`jenkinson2001flirt` with
a 9 degrees of freedom (no shearing) affine transformation to register data to
the MNI template, and the application of a brain mask to remove non-brain
tissues in the final images.

**Quality control**: First, we compute the correlation between each image
and the mean of every other images to sort them by increasing correlation
score. Then, images are manually inspected in-house following this sorting,
and a first threshold is set to remove the first outlier images. Additionally,
we use the average correlation (using Fisher's z-transform) between registered
images as a metric of quality and we retained only images at a threshold
higher than 0.5.

References
----------

.. footbibliography::
