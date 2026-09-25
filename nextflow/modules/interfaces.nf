process locate_module {
    input:
        val module_name

    output:
        stdout emit: txt_paths

    script:
        """
        #!/usr/bin/env python3

        import importlib
        from pathlib import Path

        module = importlib.import_module("${module_name}")
        
        module_dir = Path(module.__file__).parent
        print(f"{module_dir}", end="")
        """
}

process reorient {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path image_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface reorient \\
            --image_file ${image_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}

process brainmask {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "medmem"
    
    input:
        path image_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface brainmask \\
            --image_file ${image_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}

process biasfield {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path image_file
        path mask_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface biasfield \\
            --image_file ${image_file} \\
            --mask_file ${mask_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}

process applymask {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path image_file
        path mask_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface applymask \\
            --image_file ${image_file} \\
            --mask_file ${mask_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}

process scale {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path image_file
        val scale
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface scale \\
            --image_file ${image_file} \\
            --scale ${scale} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}

process align {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path image_file
        path template_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface align \\
            --anatomical_file ${image_file} \\
            --template_file ${template_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            --rigid False \\
            --quick True \\
            ${params.dryrun_flag}
        """
}

process applyaffine {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path image_file
        path template_file
        path transform_file
        val interpolation
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface applyaffine \\
            --image_file ${image_file} \\
            --template_file ${template_file} \\
            --transform-file ${transform_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            --interpolation ${interpolation} \\
            ${params.dryrun_flag}
        """
}
