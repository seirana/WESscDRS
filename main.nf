nextflow.enable.dsl = 2

// URLs and parameters
params.repo_tar = 'https://github.com/seirana/WESscDRS/archive/refs/heads/main.tar.gz'

// Main workflow
workflow {
    // Step 1: download code + data from GitHub into ./WESscDRS
    wes_dir_ch = DOWNLOAD_WESscDRS()

    // Step 2: install Python dependencies and run run.py
    RUN_WESscDRS(wes_dir_ch)
}

/**
 * DOWNLOAD_WESscDRS
 * - Downloads the repo tarball from GitHub
 * - Extracts it into a directory called "WESscDRS"
 * - Publishes that directory to the project root, so you get ./WESscDRS/bin and ./WESscDRS/data
 */
process DOWNLOAD_WESscDRS {

    tag "download WESscDRS"

    // Use the Singularity image as well (optional but neat)
    container "${baseDir}/wes-scdrs.sif"

    publishDir "${baseDir}", mode: 'copy', overwrite: true

    output:
    path "WESscDRS"

    script:
    """
    set -e

    # Clean any previous run inside work dir
    rm -rf WESscDRS

    mkdir -p WESscDRS

    # Download and extract the repo tarball
    # This will create bin/, data/, requirements.txt, etc., in WESscDRS/
    curl -L ${params.repo_tar} | tar xz --strip-components=1 -C WESscDRS

    # At this point inside this process work dir we have:
    #   WESscDRS/bin
    #   WESscDRS/data
    #   WESscDRS/requirements.txt
    #
    # publishDir will copy "WESscDRS" to ${baseDir}/WESscDRS
    """
}

/**
 * RUN_WESscDRS
 * - Installs Python dependencies from WESscDRS/requirements.txt (user site)
 * - Runs bin/run.py
 */
process RUN_WESscDRS {

    tag "run.py"

    container "${baseDir}/wes-scdrs.sif"

    input:
    path wes_dir

    // Optional: produce a results folder under WESscDRS/results
    publishDir "${baseDir}/WESscDRS/results", mode: 'copy', overwrite: true

    script:
    """
    set -e

    echo "Using WESscDRS directory: ${wes_dir}"

    cd ${wes_dir}

    # Install Python deps into user site-packages (in \$HOME/.local)
    # This avoids writing into the read-only container filesystem.
    python -m pip install --user --no-cache-dir -r requirements.txt

    # Run the main script
    python bin/run.py
    """
}
