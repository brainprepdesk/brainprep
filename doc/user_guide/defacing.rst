.. _defacing:

Defacing
========

.. image:: ../images/preproc-defacing.png
   :width: 50%
   :align: center

Introduction
------------

Defacing MRI data is crucial for protecting participant privacy in
neuroimaging research. Structural brain MRI include facial features
that can be reconstructed and used to identify individuals. Defacing removes
these features while preserving brain anatomy for analysis.

Requirements
------------

+------------+--------------+
| CPU        | RAM          |
+============+==============+
| 1          | 5 GB         |
+------------+--------------+

Description
-----------

**Processing Steps**

- **Defacing T1w image**
  We use the UK-Biobank defacing method that is provided as part of the
  standard FSL distribution under the command ``fsl_deface``
  :footcite:p:`almagro2018deface`. Similar to other established defacing
  tools, such as ``mri_deface`` :footcite:p:`bischoff2007deface`
  and ``pydeface`` :footcite:p:`gulban2009deface`, the method relies on linear
  registration to generate a mask that identifies facial voxels. Voxels within
  this mask are then set to zero to remove identifiable facial features.
  A key distinction of ``fsl_deface`` compared with ``mri_deface`` and
  ``pydeface`` is that it additionally removes the ears, providing a more
  comprehensive anonymization of head anatomy.
  This workflow is applied to T1-weighted (T1w) structural images and can be
  propagated to other modalities through rigid alignement.


**Quality Control**

- **Overlap score**  
  For each image, we compute the overlap ratio between the brain mask
  extracted using FreeSurfer's deep‑learning–based ``mri_synthstrip``
  method :footcite:p:`hoopes2022brainmask` and the corresponding defacing mask.
  Images are then sorted in ascending order of this score, allowing potential
  outliers to be easily identified.

- **Manual inspection**  
  Following the overlap-based ranking, a manual quality control step is
  performed using the generated ``defacemosaic`` figure. This figure allows
  visual inspection of the defaced image and verification that facial/ear
  structures have been successfully removed. The most obvious outliers are
  thus removed.

- **Thresholding**  
  The overlap score is thresholded at 5%, meaning that if the defacing mask
  removes a substantial portion of the brain, the preprocessing is considered
  invalid. Images with an overlap greater than 5% are flagged as low‑quality.

Outputs
-------

The ``defacing`` directory contains subject-level results, logs, and
quality-control outputs.
The structure is organized following the :ref:`brainprep ontology <ontology>`.

.. code-block:: text

    defacing/
    ├── dataset_description.json
    ├── figures
    │   └── histogram_overlap.png
    ├── log
    │   └── report_<timestamp>.rst
    ├── quality_check
    │   └── mask_overlap.tsv
    └── subjects
        └── sub-01
            └── ses-01
                ├── figures
                │   └── sub-01_ses-01_run-01_mod-T1w_defacemosaic.png
                ├── log
                │   └── report_<timestamp>.rst
                ├── sub-01_ses-01_run-01_mod-T1w_defacemask.nii.gz
                ├── sub-01_ses-01_run-01_mod-T1w_defacemask.tsv
                └── sub-01_ses-01_run-01_mod-T1w_deface.nii.gz

**Description of contents**:

- ``dataset_description.json``  
  Metadata describing the process, including versioning and processing
  information.
- ``figures/histogram_overlap.png``  
  Image overlap distribution and applied threshold.
- ``logs/report_<timestamp>.rst``  
  Contains group-level workflow steps and parameters.
- ``quality_check/mask_overlap.tsv``  
  Table containing the overlap score for each subject/session/run. The table
  includes a binary ``qc`` column indicating the quality control result.
- ``subjects/sub-<id>/ses-<id>/figures/sub-01_ses-01_run-01_mod-T1w_defacemosaic.png``  
  A visual mosaic showing defacing masks on some slices for quick quality check.
- ``subjects/sub-<id>/ses-<id>/logs/report_<timestamp>.rst``  
  Contains subject-level workflow steps and parameters.
- ``subjects/sub-<id>/ses-<id>/sub-01_ses-01_run-01_mod-T1w_defacemask.nii.gz`` 
  The binary mask identifying voxels removed during defacing (face and ears).
- ``subjects/sub-<id>/ses-<id>/sub-01_ses-01_run-01_mod-T1w_defacemask.tsv`` 
  A table containing voxel counts and physical volumes (in mm³) for the
  brain/defacing masks and their intersection.
- ``subjects/sub-<id>/ses-<id>/sub-01_ses-01_run-01_mod-T1w_deface.nii.gz``  
  The final defaced T1w image with facial/ear structures removed.

Featured examples
-----------------

.. grid::

  .. grid-item-card::
    :link: ../auto_examples/plot_defacing.html
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

        .. image:: ../auto_examples/images/thumb/sphx_glr_plot_defacing_thumb.png

      .. grid-item::
        :columns: 12 8 8 8

        .. div:: sd-font-weight-bold

          Defacing

        Explore how to perform this analysis.

References
----------

.. footbibliography::
