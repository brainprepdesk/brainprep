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

process morphologist_workflow {
    container "brainprepdesk/brainprep-sulcirec:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path t1_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface morphologist-workflow \\
            --t1_file ${t1_file} \\
            --output_dir ${task.workDir} \\
            --workspace_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}

process mriqc {
    container "brainprepdesk/brainprep-quality_assurance:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path t1_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface subject-level-qa \\
            --image_files ${t1_file} \\
            --output_dir "${task.workDir}/sub-${sub}/ses-${ses}" \\
            --workspace_dir "${task.workDir}/workspace" \\
            ${params.dryrun_flag}
        """
}


process writebatch {
    container "brainprepdesk/brainprep-vbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path t1_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface writebatch \\
            --t1_files ${t1_file} \\
            --output_dir "${task.workDir}/sub-${sub}" \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process cat12vbm {
    container "brainprepdesk/brainprep-vbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path t1_file
        path batch_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface cat12vbm-workflow \\
            --t1_files ${t1_file} \\
            --batch_file ${batch_file} \\
            --output_dir "${task.workDir}/sub-${sub}" \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process anonfile {
    container "brainprepdesk/brainprep-vbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path input_file
        val derivatives_dir
        val rawdata_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface anonfile \\
            --input_file ${input_file} \\
            --derivatives_dir ${derivatives_dir} \\
            --rawdata_dir "${rawdata_dir}" \\
            ${params.dryrun_flag}
        """
}


process reconall {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path t1_file
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface reconall \\
            --t1_file ${t1_file} \\
            --output_dir ${task.workDir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process freesurfer_status {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path log_file
        val command
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface freesurfer-status \\
            --log_file ${log_file} \\
            --command ${command} \\
            ${params.dryrun_flag}
        """
}


process reconall_surfreg {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path fs_subject_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface reconall-surfreg \\
            --output_dir ${fs_subject_dir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process reconall_projection {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path(left_reg_file, stageAs: "left/*") 
        path(right_reg_file, stageAs: "right/*") 
        path fs_subject_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface reconall-projection \\
            --left_reg_file ${left_reg_file} \\
            --right_reg_file ${right_reg_file} \\
            --output_dir ${fs_subject_dir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process convertmgz {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path fs_subject_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface convertmgz \\
            --output_dir ${fs_subject_dir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process reconall_tissues {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path fs_subject_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface reconall-tissues \\
            --workspace_dir ${task.workDir} \\
            --output_dir ${fs_subject_dir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process plot_brainparc {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "lowmem"

    input:
        path wm_mask_file
        path gm_mask_file
        path csf_mask_file
        path brain_mask_file
        path fs_subject_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface plot-brainparc \\
            --wm_mask_file ${wm_mask_file} \\
            --gm_mask_file ${gm_mask_file} \\
            --csf_mask_file ${csf_mask_file} \\
            --brain_mask_file ${brain_mask_file} \\
            --output_dir ${fs_subject_dir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}


process nextbrain {
    container "brainprepdesk/brainprep-sbm:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "highmem"

    input:
        path t1_file
        path fs_subject_dir
        val sub
        val ses
        val run
        val mod

    output:
        stdout emit: txt_paths

    script:
        """
        brainprep \\
            interface nextbrain \\
            --t1_file ${t1_file} \\
            --output_dir ${fs_subject_dir} \\
            --entities sub-${sub}_ses-${ses}_run-${run}_mod-${mod} \\
            ${params.dryrun_flag}
        """
}
