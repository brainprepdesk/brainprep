.. _fmriprep:

fMRI Pre-Processings
====================

Introduction
------------

To preprocess and ensure the quality of fMRI data, we use the fMRIPrep pipeline.
fMRIPrep is a robust and widely used preprocessing pipeline for functional MRI
(fMRI) data. It is designed to be automated, reproducible, and BIDS-compliant,
and it integrates tools from  FSL :footcite:p:`jenkinson2012fsl`, ANTs
:footcite:p:`tustison2014ants`, FreeSurfer :footcite:p:`fischl2012freesurfer`,
and more.

Description
-----------

**Steps**: First, the anatomical preprocessing includes bias field correction
(``N4BiasFieldCorrection`` via ANTs), skull-stripping of T1-weighted images,
tissue segmentation into gray matter, white matter, and CSF, surface
reconstruction using FreeSurfer :footcite:p:`fischl2012freesurfer`, and
spatial normalization to standard spaces
(MNI152, and fsLR) using nonlinear registration via ANTs.
Second, the functional preprocessing includes slice timing correction (only if the
TR is high), motion correction using FSL's ``MCFLIRT``, susceptibility
distortion correction using fieldmaps or SyN-based estimation, co-registration
of functional images to anatomical space, normalization of functional images
to standard space, and confound extraction (motion parameters, CompCor
components, global signals, and more).

**Quality control**: Quality control reports (HTML) are cheked manually.

Featured examples
-----------------

.. grid::

  .. grid-item-card::
    :link: ../auto_examples/plot_fmriprep.html
    :link-type: url
    :columns: 12 12 12 12
    :class-card: sd-shadow-sm
    :margin: 2 2 auto auto

    .. grid::
      :gutter: 3
      :margin: 0
      :padding: 0

      .. grid-item::
        :columns: 12 4 4 4

        .. image:: ../auto_examples/images/thumb/sphx_glr_plot_fmriprep_thumb.png

      .. grid-item::
        :columns: 12 8 8 8

        .. div:: sd-font-weight-bold

          fMRI Pre-Processing

        Explore how to perform this analysis with a container.

References
----------

.. footbibliography::
