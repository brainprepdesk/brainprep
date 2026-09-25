/**
 * Extracts a specific file path from a comma-separated list located on the 
 * last line of a raw text block (e.g., from interface outputs or logs).
 *
 * It cleans up system formatting artifacts like 'PosixPath', parentheses, or
 * quotes.
 * It validates file existence or initializes an empty fallback file if the
 * path contains 'null'.
 *
 * @param raw_text The raw, multi-line string text to be parsed.
 * @param index    The zero-based position of the target item in the CSV list
 *                 (defaults to 0).
 * @return         A Nextflow Path object pointing to the file, or null if
 *                 the text is empty.
 * @throws         NextflowRuntimeException if the requested index is out of
 *                 bounds for the split list.
 */
def toFile(String raw_text, int index = 0) {

    if (!raw_text) return null

    def last_line = raw_text.trim().split("\n")[-1]
    def parts = last_line.split(",")

    if (index >= parts.size()) {
        error "Out of bound index ${index}"
    }

    def file_text = parts[index].trim()
        .replace("PosixPath", "")
        .replaceAll(/['"()]/, "")

    def out_file = file(file_text)

    if (!out_file.exists()) {
        if ( file_text.contains("null") ) {
            out_file.text = ""
        } else {
            error "File does not exist: ${out_file}"
        }
    }

    return out_file
}

/**
 * Prints the contents of a Nextflow channel to the console for debugging
 * purposes, executing only when the global debug parameter is explicitly
 * enabled.
 *
 * @param channel The Nextflow Data/Queue Channel whose emitted items are to
 *                be inspected.
 * @param name    A descriptive label or tag to prefix the log output for
 *                easier identification.
 * @return        The original input channel, allowing this helper to be
 *                chained with other operators.
 */
def viewChannel(channel, String name) {
    if (params.debug) {
        channel.view { item -> "'${name}' channel: ${item}" }
    }
    return channel
}

/**
 * Transforms an incoming channel by parsing its text payloads into clean, 
 * resolved Nextflow Path objects using the {@link #toFile} helper.
 *
 * @param channel A Nextflow channel emitting rows, maps, or objects
 *                containing text path data.
 * @param index   The structural index of the string element to extract and
 *                resolve.
 * @return        A new Nextflow channel emitting fully qualified Path objects.
 */
def mapFilePaths(channel, int index) {
    return channel.map { row -> toFile(row, index) }
}

/**
 * Combines a module directory channel with a structural modality channel to
 * generate standardized absolute paths targeting specific MNI152 neuroimaging
 * brain templates.
 *
 * @param channel_module A Nextflow channel emitting root paths for pipeline
 *                       modules.
 * @param channel_mod    A Nextflow channel emitting scanning modalities:
 *                       'T1' or 'T2'.
 * @param resolution     The target spatial resolution of the template: '1mm'
 *                       or '2mm'.
 * @return               A combined Nextflow channel emitting Path objects to
 *                       the resolved template .nii.gz files.
 */
def createTemplateChannel(channel_module, channel_mod, String resolution) {
    return channel_module
        .combine(channel_mod)
        .map { module_dir, mod ->
            return file("${module_dir}/resources/MNI152_${mod}_${resolution}_brain.nii.gz")
        }
}


/**
 * Prints the workflow welcome message to the terminal.
 *
 * @param void
 * @return void (outputs text directly to the console via log.info)
 */
def welcomeMessage() {
    def script_file = workflow.projectDir.resolve(file(workflow.scriptFile).name)
    log.info"""
    ===================================================================
           🧠 Welcome to Brainprep NextFlow interface! 🧠

    License: Cecill-B
    Script: ${script_file}
    Run Profile : ${workflow.profile}
    Exec Command: ${workflow.commandLine}
    -------------------------------------------------------------------
     Execution Parameters:
      - projectDir          : ${workflow.projectDir}
      - launchDir           : ${workflow.launchDir}
      - workDir             : ${workflow.workDir}
      - containerEngine     : ${workflow.containerEngine}
    -------------------------------------------------------------------
     Configured Parameters:
      - workflow            : ${params.workflow}
      - data                : ${params.data}
      - rtype               : ${params.rtype}
      - outdir              : ${params.outdir}
      - keep                : ${params.keep}
      - dryrun              : ${params.dryrun}
      - debug               : ${params.debug}
    ===================================================================
    """.stripIndent()
}

/**
 * Prints the workflow help message to the terminal.
 *
 * This function outlines all available command-line parameters, 
 * their expected data types, and their current default values. It also
 * list all available workflows.
 *
 * @param void
 * @return void (outputs text directly to the console via log.info)
 */
def helpMessage() {
    def script_file = workflow.projectDir.resolve(file(workflow.scriptFile).name)
    def workflow_list = "\n"
    script_file.eachLine { line ->
        def matcher = (line =~ /workflow_id\s*==\s*["']([a-zA-Z0-9_]+)["']/)
        if (matcher.find()) {
            workflow_list += "      - ${matcher[0][1]}\n"
        }
    }
    log.info"""
    ===================================================================
    Help
    -------------------------------------------------------------------
     Usage:
      nextflow run brainprep.nf [options]

    External Options:
      APPTAINER_CACHEDIR="./apptainer/cache"  nextflow run brainprep.nf [options]
      APPTAINER_TMPDIR="./apptainer/tmp" nextflow run brainprep.nf [options]
    -------------------------------------------------------------------
     Main Options:
      --workflow     [string]  Name of the workflow.
                               [Default: ${params.workflow}]

      --data         [file]    CSV file containing the data to process.
                               Columns: 'file', 'sub', 'ses', 'run', 'mod'.
                               [Default: ${params.data}]

      --rtype        [string]  Run type.
                               Options: 'pool', 'flow'.
                               [Default: ${params.rtype}]

      --outdir       [file]    Root directory to export the final results.
                               [Default: ${params.outdir}]

      --keep         [boolean] Keep tool intermediate files. Valid only for
                               'pool' runs.
                               Options: true, false.
                               [Default: ${params.keep}]

      --dryrun       [boolean] Run workflow in dry run mode..
                               Options: true, false.
                               [Default: ${params.dryrun}]

      --debug        [boolean] Display debug messages.
                               Options: true, false.
                               [Default: ${params.debug}]

      --help                   Display this help message.

      -profile       [str]     Select software and execution profiles.
                               Multiple profiles can be specified as a
                               comma-separated list.
                               Options: standard, slurm, docker, apptainer 
                               [Default: ${workflow.profile}]
    -------------------------------------------------------------------
     Available Workflows:
    ${workflow_list}
    -------------------------------------------------------------------

           🚀 Ready to launch your workflow! 🚀
    ===================================================================
    """.stripIndent()
}
