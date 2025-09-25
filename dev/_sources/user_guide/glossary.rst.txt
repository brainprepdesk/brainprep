.. glossary:

Glossary
========

.. currentmodule:: brainprep

The Glossary provides short definitions of neuro-imaging concepts as well
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

    decoding
        Decoding consists in predicting, from brain images, the conditions
        associated to trial.

    EEG
        `Electroencephalography`_ is a monitoring method to record electrical
        activity of the brain.

    EPI
        Echo-Planar Imaging. This is the type of sequence used to acquire
        functional or diffusion MRI data.

    faces
        When referring to surface data, a face corresponds to one of the
        triangles of a triangular :term:`mesh`.

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

    fMRIPrep
        `fMRIPrep`_ is a :term:`fMRI` data preprocessing pipeline designed
        to provide an interface robust to variations in scan acquisition
        protocols with minimal user input. It performs basic processing
        steps (coregistration, normalization, unwarping, noise component
        extraction, segmentation, skullstripping etc.) providing outputs,
        often called confounds or nuisance parameters, that can be easily
        submitted to a variety of group level analyses, including task-based
        or resting-state :term:`fMRI`, graph theory measures, surface or
        volume-based statistics, etc.

    functional connectivity
        Functional connectivity is a measure of the similarity of the response
        patterns in two or more regions.


    functional connectome
        functional connectome is a set of connections representing brain
        interactions between regions.

    MEG
        `Magnetoencephalography`_ is a functional neuroimaging technique for mapping
        brain activity by recording magnetic fields produced by electrical currents
        occurring naturally in the brain.

    mesh
        In the context of brain surface data, a mesh refers to a 3D representation
        of the brain's surface geometry.
        It is a collection of vertices, edges, and faces
        that define the shape and structure of the brain's outer surface.
        Each :term:`vertex` represents a point in 3D space,
        and edges connect these vertices to form a network.
        :term:`Faces<faces>` are then created by connecting
        three or more vertices to form triangles.

    MNI
        MNI stands for "Montreal Neurological Institute". Usually, this is
        used to reference the MNI space/template. The current standard MNI
        template is the ICBM152, which is the average of 152 normal MRI scans
        that have been matched to the MNI305 using a 9 parameter affine transform.

    MVPA
        Multi-Voxel Pattern Analysis. This is the way :term:`supervised learning`
        methods are called in the field of brain imaging.

    Neurovault
        `Neurovault`_ is a public repository of unthresholded statistical maps,
        parcellations, and atlases of the human brain.

    parcellation
        Act of dividing the brain into smaller regions, i.e. parcels. Parcellations
        can be defined by many different criteria including anatomical or functional
        characteristics. Parcellations can either be composed of "hard" deterministic
        parcels with no overlap between individual regions or "soft" probabilistic
        parcels with a non-zero probability of overlap.

    probabilistic atlas
        Probabilistic atlases define soft parcellations of the brain in which
        the regions may overlap. In such atlases, and contrary to
        deterministic atlases, a :term:`voxel` can belong to several
        components. These atlases are represented by 4D images where the 3D
        components, also called 'spatial maps', are
        stacked along one dimension (usually the 4th dimension). In each
        3D component, the value at a given :term:`voxel` indicates how
        strongly this :term:`voxel` is related to this component.

    resting-state
        `Resting state`_ :term:`fMRI` is a method of functional magnetic resonance
        imaging that is used in brain mapping to evaluate regional interactions that
        occur in a resting or task-negative state, when an explicit task is not being
        performed.

    SNR
        `SNR`_ stands for "Signal to Noise Ratio" and is a measure comparing the level
        of a given signal to the level of the background noise.

    SPM
        `Statistical Parametric Mapping`_ is a statistical technique for examining
        differences in brain activity recorded during functional neuroimaging
        experiments. It may alternatively refer to a `software`_ created by the Wellcome
        Department of Imaging Neuroscience at University College London to carry out
        such analyses.

    supervised learning
        `Supervised learning`_ is interested in predicting an output variable,
        or target, y, from data X. Typically, we start from labeled data (the
        training set). We need to know the y for each instance of X in order to
        train the model. Once learned, this model is then applied to new unlabeled
        data (the test set) to predict the labels (although we actually know them).
        There are essentially two possible types of problems:

        .. glossary::

            regression
                 In regression problems, the objective is to predict a continuous
                 variable, such as participant age, from the data X.

            classification
                In classification problems, the objective is to predict a binary
                variable that splits the observations into two groups, such as
                patients versus controls.

        In neuroimaging research, supervised learning is typically used to derive an
        underlying cognitive process (e.g., emotional versus non-emotional theory of
        mind), a behavioral variable (e.g., reaction time or IQ), or diagnosis status
        (e.g., schizophrenia versus healthy) from brain images.

    TR
        Repetition time. This is the time in seconds between the beginning of an
        acquisition of one volume and the beginning of acquisition of the volume following it.

    unsupervised learning
        `Unsupervised learning`_ is concerned with data X without any labels. It analyzes
        the structure of a dataset to find coherent underlying structure, for instance
        using clustering, or to extract latent factors, for instance using independent
        components analysis.

        In neuroimaging research, it is typically used to create functional and anatomical
        brain atlases by clustering based on connectivity or to extract the main brain
        networks from resting-state correlations. An important option of future research
        will be the identification of potential neurobiological subgroups in psychiatric
        and neurobiological disorders.

    VBM
        `Voxel-Based Morphometry`_ measures differences in local concentrations of brain
        tissue, through a voxel-wise comparison of multiple brain images.

    vertex
        A vertex (plural vertices) represents the coordinate
        of an angle of :term:`face<faces>`
        on a triangular :term:`mesh` in 3D space.

    voxel
        A voxel represents a value on a regular grid in 3D space.


.. LINKS

.. _`Analysis of variance`:
    https://en.wikipedia.org/wiki/Analysis_of_variance

.. _`Brain Imaging Data Structure`:
    https://bids.neuroimaging.io/

.. _`Canonical independent component analysis`:
    https://arxiv.org/abs/1006.2300

.. _`Closing`:
    https://en.wikipedia.org/wiki/Closing_(morphology)

.. _`contrast`:
    https://en.wikipedia.org/wiki/Contrast_(statistics)

.. _`Dictionary learning`:
    https://en.wikipedia.org/wiki/Sparse_dictionary_learning

.. _`Dilation`:
    https://en.wikipedia.org/wiki/Dilation_(morphology)

.. _`Electroencephalography`:
    https://en.wikipedia.org/wiki/Electroencephalography

.. _`Erosion`:
    https://en.wikipedia.org/wiki/Erosion_(morphology)

.. _`False discovery rate`:
    https://en.wikipedia.org/wiki/False_discovery_rate

.. _`Family-wise error rate`:
    https://en.wikipedia.org/wiki/Family-wise_error_rate

.. _`fMRIPrep`:
    https://fmriprep.org/en/stable/

.. _`FREM`:
    https://doi.org/10.1016/j.neuroimage.2017.10.005

.. _`FWHM`:
    https://en.wikipedia.org/wiki/Full_width_at_half_maximum

.. _`Independent component analysis`:
    https://en.wikipedia.org/wiki/Independent_component_analysis

.. _`Magnetoencephalography`:
    https://en.wikipedia.org/wiki/Magnetoencephalography

.. _`mathematical morphology`:
    https://en.wikipedia.org/wiki/Mathematical_morphology

.. _`Neurovault`:
    https://www.neurovault.org/

.. _`Opening`:
    https://en.wikipedia.org/wiki/Opening_(morphology)

.. _`Predictive modeling`:
    https://en.wikipedia.org/wiki/Predictive_modelling

.. _`Recursive nearest agglomeration`:
    https://hal.science/hal-01366651/

.. _`receiver operating characteristic curve`:
    https://en.wikipedia.org/wiki/Receiver_operating_characteristic

.. _`Resting state`:
    https://en.wikipedia.org/wiki/Resting_state_fMRI

.. _`SNR`:
    https://en.wikipedia.org/wiki/Signal-to-noise_ratio

.. _`software`:
    https://www.fil.ion.ucl.ac.uk/spm/software/

.. _`Statistical Parametric Mapping`:
    https://en.wikipedia.org/wiki/Statistical_parametric_mapping

.. _`Supervised learning`:
    https://en.wikipedia.org/wiki/Supervised_learning

.. _`Unsupervised learning`:
    https://en.wikipedia.org/wiki/Unsupervised_learning

.. _`Voxel-Based Morphometry`:
    https://en.wikipedia.org/wiki/Voxel-based_morphometry
