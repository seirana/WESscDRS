nextflow.enable.dsl = 2

params.repo_tar = 'https://github.com/seirana/WESscDRS/archive/refs/heads/main.tar.gz'

workflow {
    wes_dir_ch = DOWNLOAD_WESscDRS()
    RUN_WESscDRS(wes_dir_ch)
}

process DOWNLOAD_WESscDRS {

    tag "download WESscDRS"

    // Use project root as publish target; will create ./WESscDRS/
    publishDir "${baseDir}", mode: 'copy', overwrite: true

    output:
    path "WESscDRS"

    script:
    """
    set -e

    rm -rf WESscDRS
    mkdir -p WESscDRS

    curl -L ${params.repo_tar} | tar xz --strip-components=1 -C WESscDRS

    # Now we have:
    #   WESscDRS/bin
    #   WESscDRS/data
    #   WESscDRS/requirements.txt
    """
}

process RUN_WESscDRS {

    tag "run.py"

    input:
    path wes_dir

    publishDir "${baseDir}/WESscDRS/results", mode: 'copy', overwrite: true

    script:
    """
    set -e

    echo "Using WESscDRS directory: ${wes_dir}"

    cd ${wes_dir}

    python -m pip install --user --no-cache-dir -r requirements.txt

    python bin/run.py
    """
}
