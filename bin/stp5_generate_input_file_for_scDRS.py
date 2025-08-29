#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Seirana

This program
 1. Selects 1000 genes with the highest z-score, then finds approved gene names based on Entrez IDs,
 2. generates a gene set list for the scDRS function,
 3. generates a Manhattan plot of MAGMA gene-based analyses,
 4. makes a list of genes with a significant p-value.

input:
    ./scDRS/output/PSC_WES_SAIGE_step2.genes.out
    ./scDRS/data/magma_10kb_top1000_zscore.74_traits.rv1.gs
    
output:  
    ./scDRS/output/zscore_PSC_WES_SAIGE.csv
    ./scDRS/output/geneset/PSC_WES_SAIGE_geneset.gs
    ./scDRS/output/PLOT_PSC_WES_SAIGE.png
    ./scDRS/output/significant_genes_PSC_WES_SAIGE_MAGMA.csv
"""

from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')

import os
os.system('clear')

import sys
sys.path.append('./scDRS/code/')

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import requests
import re


def list_maker(df):
    x_geneset = ''
    for i in range(len(df)-1):
        c = round(float(df.iloc[i, 1]), 4)
        tmp = str(df.iloc[i, 0]) + ':' + str(c) + ','
        x_geneset = x_geneset + tmp

    tmp = str(df.iloc[i+1, 0]) + ':' + str(df.iloc[i+1, 1])
    x_geneset = x_geneset + tmp
    return x_geneset


def get_gene_symbol(entrez_id):
    url = f"https://www.ncbi.nlm.nih.gov/gene/{entrez_id}"

    # Send GET request to the NCBI Gene page
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve data for Entrez ID {
              entrez_id}. Status code: {response.status_code}")
        return None

    # Use a regular expression to find the "Approved Symbol" and its corresponding gene name
    match = re.search(r'GeneCard for\s*(.*?)\s*</a>', response.text)
    if match:
        gene_name = match.group(1).strip()
        gene_name = re.sub(r'</span>', '', gene_name)
        return gene_name
    else:
        print(f"Approved symbol not found for Entrez ID {entrez_id}")
        return None


if __name__ == '__main__':

    # List of Entrez Gene IDs to convert
    gene_name = pd.DataFrame(index=range(1000), columns=['gene_symbol'])

    file = './scDRS/output/PSC_WES_SAIGE_step2.genes.out'
    df = pd.read_csv(file, sep=r'\s+')
    df = df.nlargest(1000, 'ZSTAT') #top 1000 z-scores
    df.index = range(1000)
    df.loc[df['ZSTAT'] > 10, 'ZSTAT'] = 10
    gene_ids = list(df.iloc[:, 0])
    gene_ids = [str(g) for g in gene_ids]

    for j in range(1000):
        # Fetch gene symbols
        gene_name.iloc[j, 0] = get_gene_symbol(gene_ids[j])
    df = pd.concat([df, gene_name], axis=1)
    df.to_csv('./scDRS/output/zscore_PSC_WES_SAIGE.csv', index=False)
    
    #..........................................................................
    # make geneset fine
    file = './scDRS/data/magma_10kb_top1000_zscore.74_traits.rv1.gs'
    cntrl = pd.read_csv(file, sep="\t")
    geneset = cntrl.loc[[0], :]
    geneset.index = range(len(geneset))
    geneset.loc[0, 'TRAIT'] = 'PSC_WES_SAIGE'

    df = df.loc[:, ['gene_symbol', 'ZSTAT']]
    geneset.loc[0, 'GENESET'] = list_maker(df)

    write_file = './scDRS/output/geneset/PSC_WES_SAIGE_geneset.gs'
    geneset.to_csv(write_file, sep="\t", index=False)
    
    # .........................................................................
    # build Manhattan plo
    file = './scDRS/output/PSC_WES_SAIGE_step2.genes.out'
    df = pd.read_csv(file, sep=r'\s+')
    df = df.loc[:, ['CHR', 'P']]
    dm = df.shape
    
    df.loc[:, 'LOG10P'] = -np.log10(df.loc[:, 'P'])
    df['ind'] = range(len(df))
    
    df.CHR = df.CHR.astype('category')
    df_grouped = df.groupby(('CHR'))
    
    # manhattan plot
    fig = plt.figure(figsize=(14, 8))  # Set the figure size
    ax = fig.add_subplot(111)
    colors = ['#7FC97F','#FDC086'] #yellow, green
    x_labels = []
    x_labels_pos = []
    for num, (name, group) in enumerate(df_grouped):
        group.plot(kind='scatter', x='ind', y='LOG10P',
                   color=colors[num % len(colors)], ax=ax)
        x_labels.append(name)
        x_labels_pos.append(
            (group['ind'].iloc[-1] - (group['ind'].iloc[-1] - group['ind'].iloc[0])/2))
    ax.set_xticks(x_labels_pos)
    ax.set_xticklabels(x_labels)
    plt.axhline(y=5.58, color='gray', linestyle='--')
    # set axis limits
    ax.set_xlim([0, len(df)])
    ax.set_ylim([0, int(df.loc[:,'LOG10P'].max()+1)])
    
    # x axis label
    ax.set_xlabel('Chromosome')
    plt.ylabel("-log10p")
    plt.title('MAGMA gene-based test', fontsize=16, fontweight='bold', loc='center', pad=20)
    
    # show the graph
    plt.savefig('./scDRS/output/PLOT_PSC_WES_SAIGE.png')
    plt.show()
    # .........................................................................
    # make list of significant genes
    data = pd.DataFrame()
    
    file = './scDRS/output/zscore_PSC_WES_SAIGE.csv'
    df = pd.read_csv(file, sep=',')
    val_genes = df.loc[df['P'] <= 2.5*1e-6, ['gene_symbol', 'CHR', 'P']]
    val_genes = pd.concat([val_genes, pd.DataFrame(
        {'Column': ['SAIGE'] * len(val_genes)})], axis=1)
    data = pd.concat([data, val_genes], axis=0)
    data.to_csv(
        './scDRS/output/significant_genes_PSC_WES_SAIGE_MAGMA.csv', index=False)