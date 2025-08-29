#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Seirana

This function runs the scDRS function over the desired traits and tissues.

input:
    ./scDRS/data/tissues.csv
    ./scDRS/data/traits.csv
    ../scDRS/data/sinlge cell datasets/{tissue}.h5ad
    ./scDRS/output/geneset/{trait}_geneset.gs
    
output:
    ./scDRS/output/cov/{tissue}_cov.tsv
    ./scDRS/output/{tissue}/{trait}.full_score.gz
    ./scDRS/output/{tissue}/{trait}.score.gz
    ./scDRS/output/{tissue}/{trait}.scdrs_group.cell_ontology_class
    ./scDRS/code/figures/cell_ontology_classes_{tissue}.png
    ./scDRS/code/figures/associated_cells_of_{tissue}_to_{geneset}.png
"""

from IPython import get_ipython
get_ipython().run_line_magic('reset','-sf')

import os
os.system('clear')

import sys
sys.path.append('./scDRS/code/')

import pandas as pd
import scanpy as sc
import numpy as np
import subprocess
import warnings
import scdrs_
import sys


warnings.filterwarnings("ignore")

tissues = pd.read_csv('./scDRS/data/tissues.csv', sep=",")
traits = pd.read_csv('./scDRS/data/traits.csv', sep=",")

for _, t1 in tissues.iterrows():
    tissue = t1[0]

    hm = 'hsapiens'

    path = './scDRS/output/'+tissue
    if not os.path.exists(path):
        os.mkdir(path)

    adata = sc.read_h5ad('../scDRS/data/sinlge cell datasets/{tissue}.h5ad')

    cell_id = adata.obs.index
    cell_id = cell_id.to_frame(index=False)
    n_genes = adata.obs.loc[:, ['n_genes']]
    n_genes.index = range(len(n_genes))
    const = np.ones((len(cell_id), 1), dtype=int)
    const = pd.DataFrame(columns=['const'], data=const)
    cov = pd.concat([cell_id, n_genes, const], axis=1)
    cov.to_csv('./scDRS/output/cov/{tissue}_cov.tsv', sep="\t", index=False)

    for _, t2 in traits.iterrows():
        which_traits = t2[0]
        which_geneset = f'{which_traits}_geneset.gs'

        args = [
            '--h5ad_file', '../scDRS/data/sinlge cell datasets/{tissue}.h5ad',
            '--h5ad_species', hm,
            '--cov_file', './scDRS/output/cov/{tissue}_cov.tsv',
            '--gs_file', './scDRS/output/geneset/{which_geneset}',
            '--gs_species', 'hsapiens',
            '--ctrl_match_opt', "mean_var",
            '--weight_opt', "vs",
            '--flag_raw_count', "False",
            '--n_ctrl', "1000",
            '--flag_return_ctrl_raw_score', "False",
            '--flag_return_ctrl_norm_score', "True",
            '--out_folder', './scDRS/output/{tissue}/',
        ]

        subprocess.run(
            ['python', '/home/shashemi/scDRS/compute_score.py'] + args)

        df_gs = pd.read_csv('./scDRS/output/geneset/' +
                            which_geneset, sep="\t", index_col=0)
        dict_score = {
            trait: pd.read_csv(
                "./scDRS/output/{tissue}/{trait}.full_score.gz", sep="\t", index_col=0)
            for trait in df_gs.index
            if os.path.isfile("./scDRS/output/{tissue}/{trait}.full_score.gz")
        }

        for trait in dict_score:
            if os.path.isfile("./scDRS/output/{tissue}/{trait}.full_score.gz"):
                adata.obs[trait] = dict_score[trait]["norm_score"]

        if len(dict_score) > 0:
            sc.set_figure_params(figsize=[2.5, 2.5], dpi=150)
            sc.pl.umap(
                adata,
                color="cell_ontology_class",
                ncols=1,
                color_map="RdBu_r",
                vmin=-5,
                vmax=5,
                save=f'cell_ontology_classes_{tissue}.png'
            )

            sc.pl.umap(
                adata,
                color=dict_score.keys(),
                color_map="RdBu_r",
                vmin=-5,
                vmax=5,
                s=20,
                save=f'associated_cells_of_{tissue}_to_{which_geneset}.png'
            )

        if os.path.isfile("./scDRS/output/{tissue}/{which_traits}.full_score.gz"):
            scdrs_.perform_downstream(
                h5ad_file='./scDRS/output/{tissue}.h5ad',
                score_file='./scDRS/output/{tissue}/{which_traits}.full_score.gz',
                out_folder='./scDRS/output/{tissue}/',
                group_analysis="cell_ontology_class",
            )