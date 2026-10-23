include {
    welcomeMessage;
    helpMessage
} from "./modules/utils.nf"
include {
    quasiraw;
    quasiraw_pool;
    sulcirec;
    quality_assurance;
    vbm;
    sbm
} from "./subworkflows/subject_level.nf"


workflow {

    main:
        welcomeMessage()

        def workflow_id = "${params.workflow}_${params.rtype}"
        def quasiraw_aligned_anatomical_ch = Channel.empty()
        def quasiraw_aligned_mask_ch = Channel.empty()
        def quasiraw_affine_transform_ch = Channel.empty()
        def sulcirec_outdir_ch = Channel.empty()
        def qa_outdir_ch = Channel.empty()
        def vbm_outdir_ch = Channel.empty()
        def sbm_outdir_ch = Channel.empty()

        if ( params.workflow in ["subject_level_quasiraw",
                                 "subject_level_sulcirec",
                                 "subject_level_qa",
                                 "subject_level_vbm",
                                 "subject_level_sbm"]
           ) {
            (anatomical_ch, output_ch, sub_ch, ses_ch,
             run_ch, mod_ch) = channel.fromPath(params.data)
                .splitCsv(header: true, strip: true)
                // .view { row -> "Raw line : ${row}" }
                .multiMap { row ->
                    def input_file_ = row.file ? file(row.file) : null
                    anatomical_file: input_file_
                    output_dir: params.outdir
                    sub: row.sub
                    ses: row.ses
                    run: row.run
                    mod: row.mod
                }
        }

        if ( params.workflow == "help" ) {
            helpMessage()
            exit 0
        }
        else if ( workflow_id == "subject_level_quasiraw_pool" ) {
            quasiraw_pool(
                anatomical_ch,
                output_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
        }
        else if ( workflow_id == "subject_level_quasiraw_flow" ) {
            quasiraw_outputs = quasiraw(
                anatomical_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
            quasiraw_aligned_anatomical_ch = quasiraw_outputs.aligned_anatomical
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
            quasiraw_aligned_mask_ch = quasiraw_outputs.aligned_mask
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
            quasiraw_affine_transform_ch = quasiraw_outputs.affine_transform
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
        }
        else if ( workflow_id == "subject_level_sulcirec_flow" ) {
            sulcirec_outputs = sulcirec(
                anatomical_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
            sulcirec_outdir_ch = sulcirec_outputs.qc
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
                .map { file, sub, ses, run, mod -> 
                    tuple(file.parent, sub, ses, run, mod) 
                }
        }
        else if ( workflow_id == "subject_level_qa_flow" ) {
            qa_outputs = quality_assurance(
                anatomical_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
            qa_outdir_ch = qa_outputs.qc
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
                .map { file, sub, ses, run, mod -> 
                    tuple(file.parent, sub, ses, run, mod) 
                }
        }
        else if ( workflow_id == "subject_level_vbm_flow" ) {
            vbm_outputs = vbm(
                anatomical_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
            vbm_outdir_ch = vbm_outputs.qc
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
                .map { file, sub, ses, run, mod -> 
                    tuple(file.parent.parent, sub, ses, run, mod) 
                }
        }
        else if ( workflow_id == "subject_level_sbm_flow" ) {
            sbm_outputs = sbm(
                anatomical_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
            sbm_outdir_ch = sbm_outputs.fsdir
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
                .map { dir, sub, ses, run, mod -> 
                    tuple(dir, sub, ses, run, mod) 
                }
        }
        else {
            error "Error: Invalid workflow ID specified: ${workflow_id}"
        }

    publish:
        quasiraw_aligned_anatomical = quasiraw_aligned_anatomical_ch
        quasiraw_aligned_mask = quasiraw_aligned_mask_ch
        quasiraw_affine_transform = quasiraw_affine_transform_ch
        sulcirec_outdir = sulcirec_outdir_ch
        qa_outdir = qa_outdir_ch
        vbm_outdir = vbm_outdir_ch
        sbm_outdir = sbm_outdir_ch
}


output {
    quasiraw_aligned_anatomical {
        path { file, sub, ses, run, mod ->
            file >> "derivatives/quasiraw/subjects/sub-${sub}/ses-${ses}/${file.name.replace('mod-' + mod + '_applyaffine', mod)}"
        }
    }
    quasiraw_aligned_mask {
        path { file, sub, ses, run, mod ->
            file >> "derivatives/quasiraw/subjects/sub-${sub}/ses-${ses}/${file.name.replace('_applyaffine', '_brainmask')}"
        }
    }
    quasiraw_affine_transform {
        path { file, sub, ses, run, mod ->
            file >> "derivatives/quasiraw/subjects/sub-${sub}/ses-${ses}/${file.name}"
        }
    }
    sulcirec_outdir {
        path { dir, sub, ses, run, mod ->
            return "derivatives/sulcirec/subjects/sub-${sub}/ses-${ses}/run-${run}"
        }
    }
    qa_outdir {
        path { dir, sub, ses, run, mod ->
            return "derivatives/quality_assurance/subjects/sub-${sub}/ses-${ses}/run-${run}"
        }
    }
    vbm_outdir {
        path { dir, sub, ses, run, mod ->
            return "derivatives/vbm/subjects/sub-${sub}/ses-${ses}/run-${run}"
        }
    }
    sbm_outdir {
        path { dir, sub, ses, run, mod ->
            return "derivatives/sbm/subjects/sub-${sub}/ses-${ses}/run-${run}"
        }
    }
}
