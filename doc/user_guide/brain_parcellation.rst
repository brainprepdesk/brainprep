.. _brain_parcellation:

Brain parcellation
==================

.. image:: ../images/preproc-cortex.png
   :width: 50%
   :align: center

Introduction
------------

The brain parcellation is performed with the ``recon-all`` command provided
by FreeSurfer :footcite:p:`fischl2012freesurfer`. It performs a fully automated
processing pipeline that takes
raw T1-weighted MRI scans and outputs segmented brain volumes, cortical
surface models, parcellation maps and numerous quantitative metrics
(e.g., cortical thickness, surface area, ....).

With ``brainprep``, researchers can perform both cross-sectional preprocessing
and longitudinal refinement of brain MRI data. The cross-sectional
workflows are designed to process individual timepoints independently.
``brainprep`` offers a routine to refine results across multiple timepoints
for the same subject. This workflow leverage temporal consistency to improve
segmentation accuracy, reduce variability, and enhance the reliability of
derived metrics such as cortical thickness or volume changes over time.
This is particularly valuable in studies of brain development, aging, or
disease progression


Description
-----------

**Steps**: Cortical analysis is performed with FreeSurfer **recon-all**
:footcite:p:`fischl2012freesurfer`. The analysis
stream includes intensity normalization, skull stripping, segmentation of
GM (pial) and WM, hemispheric-based tessellations, topology corrections and
inflation, and registration to the *fsaverag* template. Available morphological
measures are summarized on the Desikan :footcite:p:`desikan2006automated` and
Destrieux :footcite:p:`fischl2004automatically` parcellations. Specifically,
7 ROI-based features computed both on Desikan and Destrieux atlases are
shared including: the cortical thickness (mean and standard deviation),
GM volume, surface area, integrated mean and Gaussian curvatures and intrinsic
curvature index. Moreover, vertex-wise cortical thickness, curvature and average
convexity features :footcite:p:`fischl1999cortical` (measuring the depth/height
of a vertex above the average surface) are also accessible on the
high-resolution seven order icosahedron. To allow inter-hemispheric cortical
surface-based analysis, we further transform the right hemisphere features
into the left one, using the symmetric **fsavarage_sym** Freesurfer template
and the **xhemi** routines :footcite:p:`greve2013surface`. The final
vertex-wise cortical features comprise 163,842 nodes per hemisphere.

**Quality control**: We first performe a visual analysis on images ranked by
the correlation score. In addition we use the Euler number as a metric of
quality and we retaine images at a threshold greater than -217, as specified in
:footcite:p:`rosen2018`.

Featured examples
-----------------

.. grid::

  .. grid-item-card::
    :link: ../auto_examples/plot_brain_parcellation.html
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

        .. image:: ../auto_examples/images/thumb/sphx_glr_plot_brain_parcellation_thumb.png

      .. grid-item::
        :columns: 12 8 8 8

        .. div:: sd-font-weight-bold

          Brain Parcellation

        Explore how to perform this analysis with a container.

References
----------

.. footbibliography::
