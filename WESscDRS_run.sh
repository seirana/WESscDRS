#!/usr/bin/env bash
set -euo pipefail

echo ">>> RUNNING FULL WESscDRS PIPELINE"
echo

### === STEP 1: Python ===
echo ">>> [1/7] stp1_generate_input_file_for_BCFtools.py"
python3 stp1_generate_input_file_for_BCFtools.py
echo

### === STEP 2: Bash ===
echo ">>> [2/7] stp2_generate_rsIDs_with_BCFtools"
bash stp2_generate_rsIDs_with_BCFtools
echo

### === STEP 3: Python ===
echo ">>> [3/7] stp3_generate_input_file_for_MAGMA.py"
python3 stp3_generate_input_file_for_MAGMA.py
echo

### === STEP 4: Bash ===
echo ">>> [4/7] stp4_MAGMA_genebased_test.txt"
bash stp4_MAGMA_genebased_test.txt
echo

### === STEP 5: Python ===
echo ">>> [5/7] stp5_generate_input_file_for_scDRS.py"
python3 stp5_generate_input_file_for_scDRS.py
echo

### === STEP 6: Python ===
echo ">>> [6/7] stp6_scDRS.py"
python3 stp6_scDRS.py
echo

### === STEP 7: Python ===
echo ">>> [7/7] stp7_scDRS_result_evaluation.py"
python3 stp7_scDRS_result_evaluation.py
echo

echo ">>> PIPELINE FINISHED SUCCESSFULLY ✅"
