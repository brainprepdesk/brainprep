.. _tbss:

Tract-Based Spatial Statistics
==============================

Introduction
------------

Tract-Based Spatial Statistics (TBSS) provides a robust, reliable way to
study white matter microstructure across individuals using diffusion MRI.

Description
-----------

**Steps**: TBSS :footcite:p:`smith2006tbss` is designed to perform voxel-wise
statistical analysis of white matter integrity across subjects. It focuses on
a key DTI (or other models) parameteric maps (here fractional anisotropy (FA) and
mean diffusivity (MD)), which reflects how directional water
diffusion is in brain tissue.

Once DWI data have been pre-processed, the FA images are
non-linearly aligned to the ENIGMA FA template. All subjects' FA
and MD data are then projected onto the ENIGMA FA skeleton.


**Quality control**: The alignment of the FA images to the template was
manually inspected to ensure accurate results.

References
----------

.. footbibliography::
