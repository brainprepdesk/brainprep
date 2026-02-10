.. _fmriprep:

fMRI Pre-Processings
====================

.. image:: ../images/preproc-fmriprep.png
   :width: 50%
   :align: center

Introduction
------------

To preprocess and ensure the quality of fMRI data, we use the fMRIPrep pipeline.
fMRIPrep is a robust and widely used preprocessing pipeline for functional MRI
(fMRI) data. It is designed to be automated, reproducible, and BIDS-compliant,
and it integrates tools such as FSL :footcite:p:`jenkinson2012fsl`, ANTs
:footcite:p:`tustison2014ants`, FreeSurfer :footcite:p:`fischl2012freesurfer`,
and more.

Requirements
------------

+------------+--------------+
| CPU        | RAM          |
+============+==============+
| 1          | 10GB , 5 GB  |
+------------+--------------+

Description
-----------

**Processing Steps**

- **Anatomical Data Preprocessing**
  The T1w image was corrected for intensity non-uniformity (INU) with
  N4BiasFieldCorrection (Tustison et al. 2010), distributed with ANTs 2.6.2
  (Avants et al. 2008, RRID:SCR_004757), and used as T1w-reference throughout
  the workflow. The T1w-reference was then skull-stripped with a Nipype
  implementation of the antsBrainExtraction.sh workflow (from ANTs), using
  OASIS30ANTs as target template. Brain tissue segmentation of cerebrospinal
  fluid (CSF), white-matter (WM) and gray-matter (GM) was performed on the
  brain-extracted T1w using fast (FSL (version unknown), RRID:SCR_002823,
  Zhang, Brady, and Smith 2001). Volume-based spatial normalization to one
  standard space (MNI152NLin2009cAsym) was performed through nonlinear
  registration with antsRegistration (ANTs 2.6.2), using brain-extracted
  versions of both T1w reference and the T1w template. The following template
  was were selected for spatial normalization and accessed with TemplateFlow
  (25.0.4, Ciric et al. 2022): ICBM 152 Nonlinear Asymmetrical template
  version 2009c (TemplateFlow ID: MNI152NLin2009cAsym).

- **Functional Data Preprocessing**
  First, a reference volume was generated, using a custom methodology of
  fMRIPrep, for use in head motion correction. Head-motion parameters with
  respect to the BOLD reference (transformation matrices, and six
  corresponding rotation and translation parameters) are estimated before
  any spatiotemporal filtering using mcflirt (FSL , Jenkinson et al. 2002).
  The BOLD reference was then co-registered to the T1w reference using
  mri_coreg (FreeSurfer) followed by flirt (FSL , Jenkinson and Smith 2001)
  with the boundary-based registration (Greve and Fischl 2009) cost-function.
  Co-registration was configured with six degrees of freedom. Several
  confounding time-series were calculated based on the preprocessed BOLD:
  framewise displacement (FD), DVARS and three region-wise global signals.
  FD was computed using two formulations following Power (absolute sum of
  relative motions, Power et al. (2014)) and Jenkinson (relative root mean
  square displacement between affines, Jenkinson et al. (2002)). FD and DVARS
  are calculated for each functional run, both using their implementations
  in Nipype (following the definitions by Power et al. 2014). The three
  global signals are extracted within the CSF, the WM, and the whole-brain
  masks. Additionally, a set of physiological regressors were extracted to
  allow for component-based noise correction (CompCor, Behzadi et al. 2007).
  Principal components are estimated after high-pass filtering the
  preprocessed BOLD time-series (using a discrete cosine filter with 128s
  cut-off) for the two CompCor variants: temporal (tCompCor) and anatomical
  (aCompCor). tCompCor components are then calculated from the top 2% variable
  voxels within the brain mask. For aCompCor, three probabilistic masks
  (CSF, WM and combined CSF+WM) are generated in anatomical space. The
  implementation differs from that of Behzadi et al. in that instead of
  eroding the masks by 2 pixels on BOLD space, a mask of pixels that likely
  contain a volume fraction of GM is subtracted from the aCompCor masks. This
  mask is obtained by thresholding the corresponding partial volume map at
  0.05, and it ensures components are not extracted from voxels containing a
  minimal fraction of GM. Finally, these masks are resampled into BOLD space
  and binarized by thresholding at 0.99 (as in the original implementation).
  Components are also calculated separately within the WM and CSF masks. For
  each CompCor decomposition, the k components with the largest singular
  values are retained, such that the retained components’ time series are
  sufficient to explain 50 percent of variance across the nuisance mask
  (CSF, WM, combined, or temporal). The remaining components are dropped
  from consideration. The head-motion estimates calculated in the correction
  step were also placed within the corresponding confounds file. The
  confound time series derived from head motion estimates and global signals
  were expanded with the inclusion of temporal derivatives and quadratic
  terms for each (Satterthwaite et al. 2013). Frames that exceeded a threshold
  of 0.5 mm FD or 1.5 standardized DVARS were annotated as motion outliers.
  Additional nuisance timeseries are calculated by means of principal
  components analysis of the signal found within a thin band (crown) of
  voxels around the edge of the brain, as proposed by (Patriat, Reynolds,
  and Birn 2017). All resamplings can be performed with a single interpolation
  step by composing all the pertinent transformations (i.e. head-motion
  transform matrices, susceptibility distortion correction when available,
  and co-registrations to anatomical and output spaces). Gridded (volumetric)
  resamplings were performed using nitransforms, configured with cubic
  B-spline interpolation.

**Quality Control**:

Quality control reports (HTML) are cheked manually.

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
