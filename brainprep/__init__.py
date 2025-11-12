##########################################################################
# NSAp - Copyright (C) CEA, 2021 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

"""
BrainPrep is an integrated tool designed to preprocess MRI data with a strong
emphasis on **transparency**, **traceability**, **usability**, and
**portability**.

Core Principles
---------------

**Transparency**

BrainPrep is built to be understandable. Every step in the preprocessing
workflow is explicitly defined, documented, and inspectable. Users can trace
how data is transformed, which parameters are applied, and which tools are
invoked—without needing to dig through opaque scripts or hidden configurations.

**Traceability**

Reproducibility is central to scientific integrity. BrainPrep ensures that
every preprocessing run is traceable, with automatic logging of inputs,
outputs, tool versions, and execution metadata. This makes it easy to audit
results, share workflows, and reproduce findings across labs and platforms.

**Usability**

BrainPrep is designed for researchers, not just developers. Its interfaces are
intuitive, its wrappers are consistent, and its workflows are modular.
Whether you're a novice or an expert, BrainPrep aims to reduce the cognitive
load of preprocessing so you can focus on your science.

**Portability with Docker**

To ensure consistent execution across different systems, BrainPrep is
distributed and executed using **Docker**. This containerized approach
guarantees that all dependencies, tools, and configurations are bundled
together, eliminating environment-specific issues and simplifying deployment.

Design Trade-offs
-----------------

BrainPrep consciously deprioritizes:

- **Performance**: While efficiency matters, BrainPrep favors clarity over
  speed. It avoids aggressive parallelization or optimization that might
  obscure the logic of the workflow.
- **BIDS Compliance**: BrainPrep supports BIDS principles but does not
  enforce strict adherence. Instead, it provides flexible input/output
  handling that can accommodate diverse data structures and legacy formats.

Wrapper Architecture
--------------------

All preprocessing steps in BrainPrep are implemented using **decorators**,
which wrap either:

- **Command-line tools**: These wrappers return a command or list of commands
  to be executed, along with a tuple of generated output paths.
- **Python functions**: These wrappers return only a tuple of generated output
  paths, encapsulating logic written directly in Python.

This architecture promotes modularity, reusability, and clarity—making it
easy to build, inspect, and extend workflows.
"""

from ._version import __version__
