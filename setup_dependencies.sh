#!/usr/bin/env bash
set -euo pipefail

echo "==========================================="
echo "   WESscDRS - ONE-TIME SETUP"
echo "==========================================="
echo

### 1. Python virtual environment + dependencies
if [ ! -d ".venv" ]; then
    echo ">>> Creating Python virtual environment (.venv)"
    python3 -m venv .venv
else
    echo ">>> Python virtual environment (.venv) already exists, reusing"
fi

echo ">>> Activating environment"
# shellcheck disable=SC1091
source .venv/bin/activate

echo ">>> Installing Python dependencies from requirements.txt"
pip install --upgrade pip
pip install -r requirements.txt

echo
echo ">>> Python environment ready."
echo

### 2. Install HTSlib + BCFtools (only if not yet there)

mkdir -p external
HTSLIB_DIR="external/htslib"
BCFTOOLS_DIR="external/bcftools"

if [ ! -d "$HTSLIB_DIR" ]; then
    echo ">>> Cloning htslib into $HTSLIB_DIR"
    git clone --recurse-submodules https://github.com/samtools/htslib.git "$HTSLIB_DIR"
else
    echo ">>> htslib already exists in $HTSLIB_DIR, skipping clone"
fi

if [ ! -d "$BCFTOOLS_DIR" ]; then
    echo ">>> Cloning bcftools into $BCFTOOLS_DIR"
    git clone https://github.com/samtools/bcftools.git "$BCFTOOLS_DIR"
else
    echo ">>> bcftools already exists in $BCFTOOLS_DIR, skipping clone"
fi

echo ">>> Building bcftools (make)"
cd "$BCFTOOLS_DIR"
make
cd ../../

echo
echo "==========================================="
echo "   ONE-TIME SETUP COMPLETED ✅"
echo "==========================================="

