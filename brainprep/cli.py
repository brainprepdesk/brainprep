##########################################################################
# NSAp - Copyright (C) CEA, 2022 - 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" Provide a command line interface.
"""


def main():
    """
    BrainPrep command-line interface.

    This function exposes all BrainPrep workflows through a unified
    command-line interface powered by ``fire``. Each workflow
    corresponds to a processing pipeline implemented in
    ``brainprep.workflow`` and can be invoked directly from the terminal.

    Notes
    -----
    This function relies on ``fire.Fire`` to automatically generate a
    command-line interface from a dictionary mapping workflow names to
    their corresponding functions. Any additional keyword arguments
    provided on the command line are forwarded to the selected workflow.
    """
    import fire

    import brainprep.workflow as wf

    fire.Fire({
        "subject-level-qa": wf.brainprep_quality_assurance,
        "group-level-qa": wf.brainprep_group_quality_assurance,
        "subject-level-defacing": wf.brainprep_defacing,
        "subject-level-quasiraw": wf.brainprep_quasiraw,
        "group-level-quasiraw": wf.brainprep_group_quasiraw,
        "subject-level-brainparc": wf.brainprep_brainparc,
        "group-level-brainparc": wf.brainprep_group_brainparc,
        "longitudinal-brainparc": wf.brainprep_longitudinal_brainparc,
        "subject-level-vbm": wf.brainprep_vbm,
        "group-level-vbm": wf.brainprep_group_vbm,
        "longitudinal-vbm": wf.brainprep_longitudinal_vbm,
        "subject-level-fmriprep": wf.brainprep_fmriprep,
        # "tbss-preproc": wf.brainprep_tbss_preproc,
        # "tbss": wf.brainprep_tbss,
        "subject-level-dmriprep": wf.brainprep_dmriprep,
        "group-level-dmriprep": wf.brainprep_group_dmriprep
    })
