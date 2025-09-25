.. _vbm:

Voxel Based Morphometry
=======================

.. image:: ../images/preproc-vbm.png
   :width: 50%
   :align: center

Introduction
------------

Voxel-wise estimation of the local amount or volume of a specific tissue
compartment from T1w MRIs.
A longitudinal option is available to refine results.

Description
-----------

**Steps**: Voxel-Based Morphometry (VBM) is performed with CAT12
:footcite:p:`gaser2024cat12vbm`. The analysis stream includes non-linear spatial
registration to the MNI template, Gray Matter (GM), White Matter (WM), and
CerebroSpinal Fluid (CSF) tissues segmentation, bias correction of
intensity non-uniformities, and segmentations modulation by scaling
with the amount of volume changes due to spatial registration. VBM is
applied to investigate the GM, and the longitudinal model allows the
detection of small changes, such as brain plasticity or treatement effects
after a few weeks or months. The sensitivity of VBM in the WM is low, and
usually, diffusion-weighted imaging is preferred for that purpose. For this
reason, only the modulated GM images is considered. Moreover, CAT12 computes
GM volumes averaged on the Neuromorphometrics atlas that includes 284 brain
cortical and sub-cortical ROIs.

**Quality control**: We performe the same in-house QC visual analysis as
for quasi-raw images. Additionally, we also monitored the Noise Contrast
Ratio (NCR) and Image Quality Rating (IQR) as two metrics of quality and
we retained only images at a threshold below 4.

Featured examples
-----------------

.. grid::

  .. grid-item-card::
    :link: ../auto_examples/plot_vbm.html
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

        .. image:: ../auto_examples/images/thumb/sphx_glr_plot_vbm_thumb.png

      .. grid-item::
        :columns: 12 8 8 8

        .. div:: sd-font-weight-bold

          VBM

        Explore how to perform this analysis with a container.

References
----------

.. footbibliography::
