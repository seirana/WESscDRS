// --- Process: clone the repo so we get /data and /bin/run.py ---
process CLONE_REPO {
    tag "clone ${params.branch}"
    container 'docker://alpine/git:2.45.2'
    shell '/bin/sh'
    debug true

    output:
    path "WESscDRS"

    shell:
    '''
    set -eu
    rm -rf WESscDRS
    git clone --depth 1 --branch "!{params.branch}" "!{params.repo_url}" WESscDRS
    '''
}

// --- Process: download the Google Drive file into data/ ---
process DOWNLOAD_GDRIVE {
    tag "gdrive download"
    container "${params.container}"
    shell '/bin/sh'
    debug true

    input:
    path repo_dir

    output:
    path "WESscDRS"

    shell:
    '''
    set -eu

    # Normalize output directory name for Nextflow
    if [ "!{repo_dir}" != "WESscDRS" ]; then
      cp -r "!{repo_dir}" "WESscDRS"
    fi

    cd WESscDRS
    mkdir -p "!{params.gdrive_dest}"

    echo "Downloading Google Drive file into !{params.gdrive_dest}/"
    gdown --fuzzy "!{params.gdrive_url}" -O "!{params.gdrive_dest}/"

    echo "Downloaded files:"
    ls -lah "!{params.gdrive_dest}"
    '''
}

// --- Process: run bin/run.py inside your Python container ---
process RUN_PY {
    tag "run.py"
    container "${params.container}"
    shell '/bin/sh'
    debug true

    publishDir "${params.outdir}", mode: 'copy', overwrite: true

    input:
    path repo_dir

    output:
    path "${params.outdir}"

    shell:
    '''
    set -eu
    cd "!{repo_dir}"

    echo "Python version in container:"
    (python --version || python3 --version) || true

    echo "Repo contents:"; ls -lah
    echo "Data directory after GDrive download:"; ls -lah data || true

    # Provide data path to the script
    DATA_DIR="$PWD/data"
    export DATA_DIR

    # Run the script with any extra args
    (python bin/run.py !{params.run_args}) || (python3 bin/run.py !{params.run_args})

    # Collect outputs into !{params.outdir}
    mkdir -p "!{params.outdir}"

    # If your script created a 'results' folder, copy it in
    if [ -d results ]; then
      cp -r results/* "!{params.outdir}/" 2>/dev/null || true
    fi

    # Also copy any top-level files created during this run (except known dirs)
    for f in *; do
      case "$f" in results|!{params.outdir}|.git|.github) continue ;; esac
      if [ -f "$f" ]; then
        cp "$f" "!{params.outdir}/" 2>/dev/null || true
      fi
    done
    '''
}
