.. _defacing:

Defacing
========

Introduction
------------

Defacing MRI data is crucial for protecting participant privacy in
neuroimaging research. Structural brain MRI include facial features
that can be reconstructed and used to identify individuals. Defacing removes
or blurs these features while preserving brain anatomy for analysis.

Defacing is a standard step in anonymizing data, helping researchers meet legal
and ethical standards for handling sensitive health information

Description
-----------

**Steps**: The UK-Biobank study uses a customized image processing pipeline
based on FSL :footcite:p:`almagro2018deface` which includes a defacing
approach. It is applied to T1w images and can be backpropagated to other
modalities using rigid alignement. This defacing approach is released as part
of the main FSL package as ``fsl_deface``. Like other tools, such as
``mri_deface`` :footcite:p:`bischoff2007deface` and ``pydeface``
:footcite:p:`gulban2009deface`, this method uses linear registration to
create a mask of face voxels, and then sets voxels in the mask to zero.
Unlike ``mri_deface`` and ``pydeface``, this method also removes the ears.
We used ``fsl_deface`` as included in FSL with default
settings.

**Quality control**: A manual quality control was performed.

References
----------

.. footbibliography::
