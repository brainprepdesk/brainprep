include {
    welcomeMessage;
    helpMessage
} from "./modules/utils.nf"
include {
    quasiraw_flow as quasiraw;
    quasiraw_pool
} from "./subworkflows/quasiraw.nf"


workflow {

    main:
        welcomeMessage()

        def workflow_id = "${params.workflow}_${params.rtype}"
        def aligned_anatomical_ch = Channel.empty()

        if ( params.workflow == "first_level_quasiraw" ) {
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
        else if ( workflow_id == "first_level_quasiraw_pool" ) {
            quasiraw_pool(
                anatomical_ch,
                output_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
        }
        else if ( workflow_id == "first_level_quasiraw_flow" ) {
            quasiraw_outputs = quasiraw(
                anatomical_ch,
                output_ch,
                sub_ch,
                ses_ch,
                run_ch,
                mod_ch,
            )
            aligned_anatomical_ch = quasiraw_outputs.aligned_anatomical
                .merge(sub_ch, ses_ch, run_ch, mod_ch)
                .map { it.flatten() }
        }
        else {
            error "Error: Invalid workflow ID specified: ${workflow_id}"
        }

    publish:
        aligned_anatomical = aligned_anatomical_ch

}

output {
    aligned_anatomical {
        path { file, sub, ses, run, mod ->
            return "derivatives/quasiraw/subjects/sub-${sub}/ses-${ses}"
        }
    }
}
