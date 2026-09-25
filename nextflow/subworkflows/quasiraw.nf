include {
    viewChannel;
    mapFilePaths;
    createTemplateChannel
} from "../modules/utils.nf"
include {
    align;
    applymask;
    applyaffine as applyaffine_anatomical;
    applyaffine as applyaffine_mask;
    biasfield;
    brainmask;
    locate_module;
    reorient;
    scale
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


workflow quasiraw_flow {
    take:
        anatomical_ch
        output_ch
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
