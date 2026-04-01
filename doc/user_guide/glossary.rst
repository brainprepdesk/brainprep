.. glossary:

Glossary
========

.. currentmodule:: brainprep

The Glossary provides short definitions of neuroimaging concepts as well
as ``brainprep`` specific vocabulary.

If you wish to add a missing term, please create an issue or open a Pull
Request.

.. glossary::
    :sorted:

    BIDS
        `Brain Imaging Data Structure`_ is a simple and easy to adopt way
        of organizing neuroimaging and behavioral data.

    BOLD
        Blood oxygenation level dependent. This is the kind of signal measured
        by functional Magnetic Resonance Imaging.

    EPI
        Echo-Planar Imaging. This is the type of sequence used to acquire
        functional or diffusion MRI data.

    fMRI
        Functional magnetic resonance imaging is based on the fact that
        when local neural activity increases, increases in metabolism and
        blood flow lead to fluctuations of the relative concentrations of
        oxyhaemoglobin (the red cells in the blood that carry oxygen) and
        deoxyhaemoglobin (the same red cells after they have delivered the
        oxygen). Oxyhaemoglobin and deoxyhaemoglobin have different magnetic
        properties (diamagnetic and paramagnetic, respectively), and they
        affect the local magnetic field in different ways.
        The signal picked up by the MRI scanner is sensitive to these
        modifications of the local magnetic field.

    functional connectivity
        Functional connectivity is a measure of the similarity of the response
        patterns in two or more regions.

    MNI
        MNI stands for "Montreal Neurological Institute". Usually, this is
        used to reference the MNI space/template. The current standard MNI
        template is the ICBM152, which is the average of 152 normal MRI scans
        that have been matched to the MNI305 using a 9 parameter affine
        transform.

    QC
        Quality Control defines a set of procedures used to identify, flag, or
        exclude data that do not meet predefined quality standards. QC
        focuses on detecting processing problems.

    QA
        Quality Assurance aimed at ensuring that acquired data meet predifined
        quality standards. QA focuses on detecting acquisition problems.

    resting-state
        `Resting state`_ :term:`fMRI` is a method of functional magnetic
        resonance imaging that is used in brain mapping to evaluate regional
        interactions that occur in a resting or task-negative state, when an
        explicit task is not being performed.

    RBM
        Region-Based Morphometry is a morphometric method that quantifies
        tissue properties within predefined anatomical regions of interest
        (ROIs) instead of performing voxel-wise or surface-based analyses.
        RBM summarizes structural measures (e.g., gray matter volume,
        cortical thickness) at the regional level, enabling robust comparisons.

    SBM
        Surface-Based Morphometry is a structural neuroimaging approach that
        analyzes cortical properties (such as thickness, surface area,
        curvature, and folding patterns) on the reconstructed cortical surface
        rather than in voxel space. SBM provides a detailed characterization
        of cortical morphology and is well suited for studying subtle
        anatomical differences across individuals or groups.

    VBM
        `Voxel-Based Morphometry`_ measures differences in local concentrations
        of brain tissue, through a voxel-wise comparison of multiple brain
        images.

    vertex
        A vertex (plural vertices) represents the coordinate
        of an angle face on a triangular mesh in 3D space.

    voxel
        A voxel represents a value on a regular grid in 3D space.


.. LINKS

.. _`Brain Imaging Data Structure`:
    https://bids.neuroimaging.io/

.. _`Resting state`:
    https://en.wikipedia.org/wiki/Resting_state_fMRI
.. _`Voxel-Based Morphometry`:
    https://en.wikipedia.org/wiki/Voxel-based_morphometry
