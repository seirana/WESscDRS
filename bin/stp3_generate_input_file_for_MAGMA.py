#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: seirana

This program gets generates files needed for MAGMA gene-based test

input:
    ./scDRS/output/variants_with_rsID_PSC_WES_SAIGE.vcf 
    .scDRS/data/SAIGE_single_marker_test.txt
output:
    ./scDRS/output/PSC_WES_SAIGE_for_step2.txt
    ./scDRS/output/PSC_WES_SAIGE_for_MAGMA.txt
"""

from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')

import os
os.system('clear')

import read_write as rw
import pandas as pd


file = './scDRS/output/variants_with_rsID_PSC_WES_SAIGE.vcf'
split = ('\t')
with open(file) as f:
    lines = f.readlines()

clmns = lines[27]
lines = lines[28:]
clmns = list(clmns.split(split))
l = len(clmns)
if clmns[l-1].endswith('\n'):
    s = clmns[l-1]
    sl = len(s)
    clmns[l-1] = s[0:sl-1]

y = pd.DataFrame([x.strip().split(split) for x in lines], columns=clmns)
vcf = y.copy()
vcf.rename(columns={'#CHROM': 'CHROM'}, inplace=True)

PSC_WES_for_MAGMA = vcf.loc[:, ['ID', 'CHROM', 'POS']].copy()
PSC_WES_for_MAGMA.columns = ['Variant name', 'CHROM', 'GENPOS']

file = './scDRS/output/PSC_WES_SAIGE_for_MAGMA'
rw.write_txt(file, PSC_WES_for_MAGMA, ' ', False)

# .............................................................................
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
df = y

PSC_WES_for_step2 = df.loc[:, ['MarkerID', 'p.value']].copy()
PSC_WES_for_step2.loc[:, 'MarkerID'] = vcf.loc[:, 'ID']
PSC_WES_for_step2.columns = ['SNP id', 'p-value']
file = './scDRS/output/PSC_WES_SAIGE_for_step2'