#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Seirana

This program generates a file which is in the desired format of bcftools funtion

input: 
    './scDRS/data/SAIGE_single_marker_test.txt'
output:
    ./scDRS/output/bcf_variants_PSC_WES_SAIGE.vcf'
"""

from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')

import os
os.system('clear')

import sys
sys.path.append('./scDRS/code/')

import pandas as pd


file = './scDRS/data/SAIGE_single_marker_test.txt'

with open(file, 'rt') as f:
    lines = f.readlines()

clmns = lines[0]
clmns = clmns.split()
l = len(clmns)
if clmns[l-1].endswith('\n'):
    s = clmns[l-1]
    sl = len(s)
    clmns[l-1] = s[0:sl-1]

y = pd.DataFrame([x.strip().split() for x in lines], columns=clmns)
y.drop(y.index[0], axis=0, inplace=True)
y.reset_index(drop=True, inplace=True)
reg = y
reg.loc[:, 'reg_index'] = range(len(reg))
reg.iloc[:, 2] = reg.iloc[:, 2].str.replace('chr', '', regex=False)

bcf = pd.DataFrame({
    "#CHROM": reg.iloc[:, 0],
    "POS": reg.iloc[:, 1],
    "ID": ".",
    "REF": reg.iloc[:, 3],
    "ALT": reg.iloc[:, 4],
    "QUAL": ".",
    "FILTER": ".",
    "INFO": "."
})

with open('./scDRS/output/bcf_variants_PSC_WES_SAIGE.vcf', 'w') as f:
    f.write("##fileformat=VCFv4.2\n")
    bcf.to_csv(f, sep="\t", index=False)