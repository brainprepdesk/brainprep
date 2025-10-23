.. -*- mode: rst -*-

1.0.0.dev
=========

HIGHLIGHTS
----------

NEW
---

- :bdg-success:`Doc` Create doc with `furo <https://github.com/pradyunsg/furo>`_.
- :bdg-success:`Enhancement` Worflows generate a report file.
- :bdg-success:`Enhancement` Worflows generate BIDS-compliant organization.
- :bdg-success:`Enhancement` New workflows can generate HTML reporting.
- :bdg-success:`Datasets` Toy datasets have been added to test the module.
- :bdg-success:`Enhancement` Quasi-RAW preprocessing compute the brain mask
  using `mri_synthstrip <https://surfer.nmr.mgh.harvard.edu/docs/synthstrip>`_.

Fixes
-----

Enhancements
------------

- :bdg-success:`API` A `keep_intermediate` argument has been added to all
  workflows to retain intermediate results; useful for debugging.

Changes
-------

- :bdg-success:`API` Building blocks are now grouped in an interfaces
  submodule.
- :bdg-danger:`Deprecation` Path custom white matter mask to `recon-all` has
  been deprecated.
- :bdg-success:`Enhancement` Use '--no-annot' in surfreg to avoid using the
  annotation (aparc) to help with the registration. This was described to
  create some artifacts on the edge of the medial wall
  (https://surfer.nmr.mgh.harvard.edu/fswiki/Xhemi).


0.0.2
=====

**Released September 2022**

HIGHLIGHTS
----------

- :bdg-success:`API` This release includes different workflows to process
  antomical, functional and diffusion MR images.
- :bdg-success:`API` All workflows are integrated in a dedicated container
  to enforce reproducible research.

NEW
---

- :bdg-success:`API` The following workflows are released:

* fsreconall
* fsreconall-summary
* fsreconall-qc
* fsreconall-longitudinal
* cat12vbm
* cat12vbm-qc
* cat12vbm-roi
* quasiraw
* quasiraw-qc
* fmriprep
* fmriprep-conn
* mriqc
* mriqc-summary
* deface
* tbss-preproc
* tbss
* dmriprep

Fixes
-----

Enhancements
------------

Changes
-------

