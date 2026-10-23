Containers
==========

Welcome to the ``brainprep`` containerization project. This guide will walk you
through the process of building and using containers for brainprep. By
leveraging Docker and Apptainer, we ensure that all necessary software
components are isolated and easily manageable. The multi-stage build approach
allows for efficient and modular configuration, while the automated build
script simplifies the creation and export of container images.
Let's get started!

Multi-Stage Builds
------------------

The container build process utilizes a multi-stage Docker build approach.
Each stage in the build process is dedicated to installing and configuring a
specific software component required by ``brainprep``. This modular approach
ensures that each component is isolated and can be updated and used
independently.

Workflow-Dedicated Containers
----------------------------

In addition to the software-specific stages, there are dedicated containers
for the different ``brainprep`` workflows. These workflow containers are built
from the previously defined software stages, ensuring that all necessary
dependencies are included. This allows for a streamlined and efficient
execution of various workflows within isolated environments.

Configuration with Bake
------------------------

The configuration of the containers is managed using
`Bake <https://docs.docker.com/build/bake>`_. Bake allows for the definition
of multi-container applications and the specification of build and run
instructions in a declarative manner. This simplifies the configuration
process.

Automated Build Process
-----------------------

The build process is automated using the ``build.sh`` script. This script
handles the creation of the Docker images and their export in both Docker
tar format and Apptainer sif format.

Usage
-----

1. **Install Docker and Apptainer**:
   Ensure that Docker and Apptainer are installed on your system. Follow the
   installation instructions provided in the respective documentation.

   - Docker: `Docker Installation Guide <https://docs.docker.com/engine/installation>`_
   - Apptainer: `Apptainer Installation Guide <https://apptainer.org/docs/user/latest/quick_start.html#installation>`_

2. **Run the Build Script**:
   Execute the ``build.sh`` script to initiate the container build process.
   This script will handle the multi-stage build and export the final images.

   .. code-block:: bash

      ./build.sh

3. **Use the Containers**:
   Once the build process is complete, you can use the generated Docker and
   Apptainer images to run your workflows. Refer to the specific workflow
   documentation for instructions on how to use the generated containers.

   - **Explore Docker Image Layers**:
     To explore the layers of a Docker image, you can use the following command:

     .. code-block:: bash

        tar -tvf <TAR_IMAGE> | sort -k 3 -n -r | head -n 20 | awk '{print $3, $6}' | numfmt --to=iec

   - **List Docker Image Labels**:
     To display the labels of a Docker image, you can use the following command:

     .. code-block:: bash

        docker inspect --format='{{json .Config.Labels}}' <IMAGE>:<VERSION> | jq

   - **Connect Apptainer Image**:
     To connect and interact with an Apptainer image, use the following command:

     .. code-block:: bash

        apptainer shell <SIF_IMAGE>
