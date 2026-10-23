include {
    viewChannel;
    mapFilePaths;
    createTemplateChannel
} from "../modules/utils.nf"
include {
    anonfile;
    align;
    applymask;
    applyaffine as applyaffine_anatomical;
    applyaffine as applyaffine_mask;
    biasfield;
    brainmask;
    locate_module;
    reorient;
    scale;
    morphologist_workflow;
    mriqc;
    writebatch;
    cat12vbm;
    nextbrain;
    reconall;
    freesurfer_status as reconall_status;
    freesurfer_status as xhemireg_status;
    reconall_surfreg;
    reconall_projection;
    convertmgz;
    reconall_tissues;
    plot_brainparc
} from "../modules/interfaces.nf"


process quasiraw_pool {
    container "brainprepdesk/brainprep-quasiraw:${params.container_version}"
    tag "sub-${sub}_ses-${ses}_run-${run}_mod-${mod}"
    label "medmem"

    input:
        path anatomical_file
        path output_dir
        val sub
        val ses
        val run
        val mod

    script:
        """
        brainprep \\
            subject-level-quasiraw \\
            --anatomical_file ${anatomical_file} \\
            --output_dir ${output_dir} \\
            ${params.keep_flag} \\
            ${params.dryrun_flag}
        """
}


workflow quasiraw {
    take:
        anatomical_ch
        sub_ch
        ses_ch
        run_ch
        mod_ch

    main:
        locate_module_output = locate_module("brainprep")
        def module_ch = mapFilePaths(locate_module_output, 0)
        viewChannel(module_ch, "locate_module")

        def template_ch = createTemplateChannel(module_ch, mod_ch, "1mm")
        def lowres_template_ch = createTemplateChannel(module_ch, mod_ch, "2mm")
        viewChannel(template_ch, "template")
        viewChannel(lowres_template_ch, "lowres_template")

        reorient_output = reorient(
            anatomical_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def reoriented_anatomical_ch = mapFilePaths(reorient_output, 0)
        viewChannel(reoriented_anatomical_ch, "reorient")

        brainmask_output = brainmask(
            reoriented_anatomical_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def mask_ch = mapFilePaths(brainmask_output, 1)
        viewChannel(mask_ch, "brainmask")

        biasfield_output = biasfield(
            reoriented_anatomical_ch,
            mask_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def bc_anatomical_ch = mapFilePaths(biasfield_output, 0)
        viewChannel(bc_anatomical_ch, "biasfield")

        applymask_output = applymask(
            bc_anatomical_ch,
            mask_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def bc_brain_ch = mapFilePaths(applymask_output, 0)
        viewChannel(bc_brain_ch, "applymask")

        scale_output = scale(
            bc_brain_ch,
            2,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def scaled_bc_brain_ch = mapFilePaths(scale_output, 0)
        viewChannel(scaled_bc_brain_ch, "scale")

        align_output = align(
            scaled_bc_brain_ch,
            lowres_template_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def affine_transform_ch = mapFilePaths(align_output, 1)
        viewChannel(affine_transform_ch, "align")

        applyaffine_output = applyaffine_anatomical(
            bc_anatomical_ch,
            template_ch,
            affine_transform_ch,
            "spline",
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def aligned_anatomical_ch = mapFilePaths(applyaffine_output, 0)
        viewChannel(aligned_anatomical_ch, "applyaffine_anatomical")

        applyaffine_output = applyaffine_mask(
            mask_ch,
            template_ch,
            affine_transform_ch,
            "nearestneighbour",
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def aligned_mask_ch = mapFilePaths(applyaffine_output, 0)
        viewChannel(aligned_mask_ch, "applyaffine_mask")

    emit:
        aligned_anatomical = aligned_anatomical_ch
        aligned_mask = aligned_mask_ch
        affine_transform = affine_transform_ch
}


workflow sulcirec {
    take:
        t1_ch
        sub_ch
        ses_ch
        run_ch
        mod_ch

    main:
        morphologist_output = morphologist_workflow(
            t1_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def qc_ch = mapFilePaths(morphologist_output, -1)
        viewChannel(qc_ch, "qc")

    emit:
        qc = qc_ch
}


workflow quality_assurance {
    take:
        t1_ch
        sub_ch
        ses_ch
        run_ch
        mod_ch

    main:
        mriqc_output = mriqc(
            t1_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def qc_ch = mapFilePaths(mriqc_output, 0)
        viewChannel(qc_ch, "qc")

    emit:
        qc = qc_ch
}


workflow vbm {
    take:
        t1_ch
        sub_ch
        ses_ch
        run_ch
        mod_ch

    main:
        writebatch_output = writebatch(
            t1_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def batch_ch = mapFilePaths(writebatch_output, 0)
        viewChannel(batch_ch, "batch")

        cat12vbm_output = cat12vbm(
            t1_ch,
            batch_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def qc_ch = mapFilePaths(cat12vbm_output, -1)
        viewChannel(qc_ch, "qc")

        anonfile(
            batch_ch,
            "${workflow.workDir}",
            "None",
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )

    emit:
        qc = qc_ch
}


workflow sbm {
    take:
        t1_ch
        sub_ch
        ses_ch
        run_ch
        mod_ch

    main:
        reconall_output = reconall(
            t1_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def reconall_log_ch = mapFilePaths(reconall_output, 0)
        def fsdir_ch = reconall_log_ch
            .map { file -> 
                file.parent.parent
            }
        viewChannel(fsdir_ch, "subject directory")
        viewChannel(reconall_log_ch, "reconall log")

        reconall_status(
            reconall_log_ch,
            "recon-all",
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )

        surfreg_output = reconall_surfreg(
            fsdir_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def left_reg_ch = mapFilePaths(surfreg_output, 0)
        def right_reg_ch = mapFilePaths(surfreg_output, 1)
        def surfreg_log_ch = mapFilePaths(surfreg_output, 2)
        viewChannel(left_reg_ch, "surfreg left")
        viewChannel(right_reg_ch, "surfreg right")
        viewChannel(surfreg_log_ch, "surfreg log")

        xhemireg_status(
            surfreg_log_ch,
            "xhemireg",
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )

        projection_output = reconall_projection(
            left_reg_ch,
            right_reg_ch,
            fsdir_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def left_thickness_ch = mapFilePaths(surfreg_output, 0)
        def right_thickness_ch = mapFilePaths(surfreg_output, 1)
        viewChannel(left_thickness_ch, "thickness left")
        viewChannel(right_thickness_ch, "thickness right")

        tissues_output = reconall_tissues(
            fsdir_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def wm_mask_ch = mapFilePaths(tissues_output, 0)
        def gm_mask_ch = mapFilePaths(tissues_output, 1)
        def csf_mask_ch = mapFilePaths(tissues_output, 2)
        def brain_mask_ch = mapFilePaths(tissues_output, 3)
        viewChannel(wm_mask_ch, "wm mask")
        viewChannel(gm_mask_ch, "gm mask")
        viewChannel(csf_mask_ch, "csf mask")
        viewChannel(brain_mask_ch, "brain mask")

        convertmgz_output = convertmgz(
            fsdir_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def aparc_aseg_ch = mapFilePaths(convertmgz_output, 0)
        def aparc_a2009s_aseg_ch = mapFilePaths(convertmgz_output, 1)
        viewChannel(aparc_aseg_ch, "aparc aseg")
        viewChannel(aparc_a2009s_aseg_ch, "aparc a2009s aseg")

        plot_output = plot_brainparc(
            wm_mask_ch,
            gm_mask_ch,
            csf_mask_ch,
            brain_mask_ch,
            fsdir_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def brainparc_ch = mapFilePaths(plot_output, 0)
        viewChannel(brainparc_ch, "brainparc")

        nextbrain_output = nextbrain(
            t1_ch,
            fsdir_ch,
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )
        def left_seg_ch = mapFilePaths(nextbrain_output, 0)
        def right_seg_ch = mapFilePaths(nextbrain_output, 1)
        viewChannel(left_seg_ch, "seg left")
        viewChannel(right_seg_ch, "seg right")

        def wait_signal = surfreg_output.collect().map { true }
        log_ch = fsdir_ch
            .flatMap { subject_dir ->
                def pattern = "${subject_dir}/scripts/{recon-all.*,seg2cc.log,unknown-args.txt}"
                return file(pattern, checkIfExists: false)
            }
            .combine( wait_signal )
            .map { log, ready -> log } 
        anonfile(
            log_ch,
            "${workflow.workDir}",
            "None",
            sub_ch,
            ses_ch,
            run_ch,
            mod_ch
        )


    emit:
        fsdir = fsdir_ch
}

