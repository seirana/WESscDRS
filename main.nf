nextflow.enable.dsl = 2

workflow {
    // Step 1: prepare local WESscDRS/ with bin/ and data/ in the user’s run directory
    wes_dir_ch = PREPARE_WESscDRS()

    // Step 2: install deps and run run.py
    RUN_WESscDRS(wes_dir_ch)
}

/**
 * PREPARE_WESscDRS
 * - Copies code and data from the pipeline repo (projectDir)
 * - Creates ./WESscDRS/bin and ./WESscDRS/data in the run directory
 */
process PREPARE_WESscDRS {

    tag "prepare WESscDRS directory"

    // This publishes the WESscDRS directory *into the user’s working directory*
    publishDir "${baseDir}", mode: 'copy', overwrite: true

    output:
    path "WESscDRS"

    script:
    """
    set -e

    # Clean up any leftover directory in the process work dir
    rm -rf WESscDRS
    mkdir -p WESscDRS

    # Copy bin and data from the pipeline repository location
    # projectDir is where Nextflow checked out seirana/WESscDRS
    cp -r ${projectDir}/bin WESscDRS/
    cp -r ${projectDir}/data WESscDRS/ || true

    # Copy requirements if present
    if [ -f ${projectDir}/requirements.txt ]; then
        cp ${projectDir}/requirements.txt WESscDRS/
    fi

    # After publishDir:
    #   ./WESscDRS/bin
    #   ./WESscDRS/data
    #   ./WESscDRS/requirements.txt
    """
}

/**
 * RUN_WESscDRS
 * - Installs Python dependencies
 * - Resolves input as WESscDRS/<params.input>
 * - Runs: python bin/run.py --input <resolved> --outdir <tmp_results>
 * - Publishes results to <baseDir>/<params.outdir>
 */
process RUN_WESscDRS {

    tag "run.py"

    input:
    path wes_dir

    // Final results directory in the user's working directory
    publishDir "${baseDir}/${params.outdir}", mode: 'copy', overwrite: true

    // Declare the temp results dir as the process output
    output:
    path "${params.outdir}"

    script:
    """
    set -e

    echo "Using WESscDRS directory: ${wes_dir}"

    cd ${wes_dir}

    # Resolve input path: with --input data → WESscDRS/data
    INPUT_PATH="\${PWD}/${params.input}"

    # Temp results dir inside WESscDRS
    OUTDIR_LOCAL="\${PWD}/${params.outdir}"
    mkdir -p "\${OUTDIR_LOCAL}"

    # Install Python deps into user site-packages
    if [ -f requirements.txt ]; then
        python -m pip install --user --no-cache-dir -r requirements.txt
    fi

    # Run your main script
    python bin/run.py --input "\${INPUT_PATH}" --outdir "\${OUTDIR_LOCAL}"
    """
}
