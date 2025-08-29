nextflow.enable.dsl = 2

// -------- Parameters (override at runtime if you want) --------
params.repo_url    = params.repo_url    ?: 'https://github.com/seirana/WESscDRS.git'
params.branch      = params.branch      ?: 'main'
params.run_args    = params.run_args    ?: ''          // e.g. '--foo 123 --bar x'
params.outdir      = params.outdir      ?: 'results'   // collected outputs
params.container   = params.container   ?: 'wes-scdrs:latest'

// Google Drive file (default = the link you gave)
params.gdrive_url  = params.gdrive_url  ?: 'https://drive.google.com/file/d/1st4mJF1CORXlRX6mNQDDgz7VKn_IdzAt/view?usp=drive_link'
params.gdrive_dest = params.gdrive_dest ?: 'data'      // where to save inside the repo

workflow {
    repo_ch = CLONE_REPO()
    with_drive_ch = DOWNLOAD_GDRIVE(repo_ch)
    RUN_PY(with_drive_ch)
}

// --- Process: clone the repo so we get /data and /bin/run.py ---
process CLONE_REPO {
    tag "clone ${params.branch}"
    container 'alpine/git:2.45.2'
    echo true

    output:
    path "WESscDRS"

    """
    rm -rf WESscDRS
    git clone --depth 1 --branch ${params.branch} ${params.repo_url} WESscDRS
    """
}

// --- Process: download the Google Drive file into data/ ---
process DOWNLOAD_GDRIVE {
    tag "gdrive download"
    container "${params.container}"
    echo true

    input:
    path repo_dir

    output:
    path "WESscDRS"

    """
    set -euo pipefail

    # Normalize output directory name for Nextflow
    if [ "${repo_dir}" != "WESscDRS" ]; then
      cp -r "${repo_dir}" "WESscDRS"
    fi

    cd WESscDRS
    mkdir -p ${params.gdrive_dest}

    echo "Downloading Google Drive file into ${params.gdrive_dest}/"
    # gdown handles Drive 'confirm' tokens via --fuzzy
    gdown --fuzzy "${params.gdrive_url}" -O ${params.gdrive_dest}/

    echo "Downloaded files:"
    ls -lah ${params.gdrive_dest}

    # leave the updated repo as the process output
    """
}

// --- Process: run bin/run.py inside your Python container ---
process RUN_PY {
    tag "run.py"
    container "${params.container}"
    echo true

    publishDir "${params.outdir}", mode: 'copy', overwrite: true

    input:
    path repo_dir

    output:
    path "${params.outdir}"

    """
    set -euo pipefail
    cd ${repo_dir}

    echo "Python version in container:"
    python --version || python3 --version || true

    echo "Repo contents:"
    ls -lah
    echo "Data directory after GDrive download:"
    ls -lah data || true

    # If run.py needs data path, provide it as an env var
    export DATA_DIR="$(pwd)/data"

    # Run the script
    (python bin/run.py ${params.run_args}) || (python3 bin/run.py ${params.run_args})

    # Collect outputs into ${params.outdir}
    mkdir -p "${params.outdir}"

    # If your script created a 'results' folder, copy it in
    if [ -d results ]; then
      cp -r results/* "${params.outdir}/" 2>/dev/null || true
    fi

    # Also copy any files created at top-level that look like outputs
    for f in *; do
      case "$f" in
        results|${params.outdir}|.git|.github) continue ;;
      esac
      if [ -f "$f" ]; then
        cp "$f" "${params.outdir}/" 2>/dev/null || true
      fi
    done
    """
}

