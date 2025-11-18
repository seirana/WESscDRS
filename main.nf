nextflow.enable.dsl = 2

/*
 * Minimal workflow: a single process that calls bin/run.py
 * using params.input and params.outdir (defined in nextflow.config).
 */

workflow {
    RUN_SCDRS()
}

process RUN_SCDRS {

    tag "wes_scdrs"

    /*
     * Save results to params.outdir
     * (this directory is created if it does not exist)
     */
    publishDir params.outdir, mode: 'copy', overwrite: true

    script:
    """
    mkdir -p "${params.outdir}"
    run.py --input "${params.input}" --outdir "${params.outdir}"
    """
}
