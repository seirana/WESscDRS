#!/usr/bin/env python

import fire
import pandas as pd
import numpy as np
from statsmodels.stats.multitest import multipletests
import scdrs
from typing import Dict, List
import scanpy as sc
import os
import time


def get_cli_head():
    MASTHEAD = "******************************************************************************\n"
    MASTHEAD += "* Single-cell disease relevance score (scDRS)\n"
    MASTHEAD += "* Version %s\n" % scdrs.__version__
    MASTHEAD += "* Martin Jinye Zhang and Kangcheng Hou\n"
    MASTHEAD += "* HSPH / Broad Institute / UCLA\n"
    MASTHEAD += "* MIT License\n"
    MASTHEAD += "******************************************************************************\n"
    return MASTHEAD


def compute_score(
    h5ad_file: str,
    h5ad_species: str,
    gs_file: str,
    gs_species: str,
    out_folder: str,
    cov_file: str = None,
    ctrl_match_opt: str = "mean_var",
    weight_opt: str = "vs",
    adj_prop: str = None,
    flag_filter_data: bool = True,
    flag_raw_count: bool = True,
    n_ctrl: int = 1000,
    flag_return_ctrl_raw_score: bool = False,
    flag_return_ctrl_norm_score: bool = True,
):
    """
    Compute scDRS scores. Generate `.score.gz` and `.full_score.gz` files for each trait.

    Parameters
    ----------
    h5ad_file : str
        Single-cell .h5ad file.
    h5ad_species : str
        Species of h5ad_file. One of "hsapiens", "human", "mmusculus", or "mouse".
    gs_file : str
        scDRS gene set .gs file.
    gs_species : str
        Species of the gs file. One of "hsapiens", "human", "mmusculus", or "mouse".
    out_folder : str
        Output folder. Save scDRS score files as `<out_folder>/<trait>.score.gz` and
        scDRS full score files as `<out_folder>/<trait>.full_score.gz`, where trait 
        identifier <trait> is from gs_file file.
    cov_file : str, optional
        scDRS covariate .cov file. Default is None.
    ctrl_match_opt : str, optional
        Control matching option. One of "mean" and "mean_var". Default is "mean_var".
    weight_opt : str, optional
        Weighting option. One of "uniform", "vs", "inv_std", and "od". Default is "vs".
    adj_prop : str, optional
        Cell group annotation (e.g., cell type) in `adata.obs.columns` used for adjusting 
        for cell group proportions. Cells are inversely weighted by the corresponding 
        group size. Default is None.
    flag_filter_data : bool, optional
        If to apply minimal cell and gene filtering to h5ad_file. Default is True.
    flag_raw_count : bool, optional
        If to apply size-factor normalization and log1p-transformation to h5ad_file.
        Default is True.
    n_ctrl : int, optional
        Number of control gene sets. Default is 1000.
    flag_return_ctrl_raw_score : bool, optional
        If to return raw control scores. Default is False.
    flag_return_ctrl_norm_score : bool, optional
        If to return normalized control scores. Default is True.
        
    Examples
    --------
    scdrs compute-score \
        --h5ad-file <h5ad_file>\
        --h5ad-species mouse\
        --gs-file <gs_file>\
        --gs-species human\
        --out-folder <out_folder>\
        --cov-file <cov_file>\
        --flag-filter-data True\
        --flag-raw-count True\
        --n-ctrl 1000\
        --flag-return-ctrl-raw-score False\
        --flag-return-ctrl-norm-score True
    """

    sys_start_time = time.time()

    ###########################################################################################
    ######                                    Parse Options                              ######
    ###########################################################################################
    H5AD_FILE = h5ad_file
    H5AD_SPECIES = h5ad_species
    COV_FILE = cov_file
    GS_FILE = gs_file
    GS_SPECIES = gs_species
    CTRL_MATCH_OPT = ctrl_match_opt
    WEIGHT_OPT = weight_opt
    ADJ_PROP = adj_prop
    FLAG_FILTER_DATA = flag_filter_data
    FLAG_RAW_COUNT = flag_raw_count
    N_CTRL = n_ctrl
    FLAG_RETURN_CTRL_RAW_SCORE = flag_return_ctrl_raw_score
    FLAG_RETURN_CTRL_NORM_SCORE = flag_return_ctrl_norm_score
    OUT_FOLDER = out_folder

    if H5AD_SPECIES != GS_SPECIES:
        H5AD_SPECIES = scdrs.util.convert_species_name(H5AD_SPECIES)
        GS_SPECIES = scdrs.util.convert_species_name(GS_SPECIES)

    header = get_cli_head()
    header += "Call: scdrs compute-score \\\n"
    header += "--h5ad-file %s \\\n" % H5AD_FILE
    header += "--h5ad-species %s \\\n" % H5AD_SPECIES
    header += "--cov-file %s \\\n" % COV_FILE
    header += "--gs-file %s \\\n" % GS_FILE
    header += "--gs-species %s \\\n" % GS_SPECIES
    header += "--ctrl-match-opt %s \\\n" % CTRL_MATCH_OPT
    header += "--weight-opt %s \\\n" % WEIGHT_OPT
    header += "--adj-prop %s \\\n" % ADJ_PROP
    header += "--flag-filter-data %s \\\n" % FLAG_FILTER_DATA
    header += "--flag-raw-count %s \\\n" % FLAG_RAW_COUNT
    header += "--n-ctrl %d \\\n" % N_CTRL
    header += "--flag-return-ctrl-raw-score %s \\\n" % FLAG_RETURN_CTRL_RAW_SCORE
    header += "--flag-return-ctrl-norm-score %s \\\n" % FLAG_RETURN_CTRL_NORM_SCORE
    header += "--out-folder %s\n" % OUT_FOLDER
    print(header)

    # Check options
    if H5AD_SPECIES != GS_SPECIES:
        if H5AD_SPECIES not in ["mmusculus", "hsapiens"]:
            raise ValueError(
                "--h5ad-species needs to be one of [mmusculus, hsapiens] "
                "unless --h5ad-species==--gs-species"
            )
        if GS_SPECIES not in ["mmusculus", "hsapiens"]:
            raise ValueError(
                "--gs-species needs to be one of [mmusculus, hsapiens] "
                "unless --h5ad-species==--gs-species"
            )
    if CTRL_MATCH_OPT not in ["mean", "mean_var"]:
        raise ValueError("--ctrl-match-opt needs to be one of [mean, mean_var]")
    if WEIGHT_OPT not in ["uniform", "vs", "inv_std", "od"]:
        raise ValueError("--weight-opt needs to be one of [uniform, vs, inv_std, od]")

    ###########################################################################################
    ######                                     Load data                                 ######
    ###########################################################################################
    print("Loading data:")

    # Load .h5ad file
    adata = scdrs.util.load_h5ad(
        H5AD_FILE, flag_filter_data=FLAG_FILTER_DATA, flag_raw_count=FLAG_RAW_COUNT
    )
    print(
        "--h5ad-file loaded: n_cell=%d, n_gene=%d (sys_time=%0.1fs)"
        % (adata.shape[0], adata.shape[1], time.time() - sys_start_time)
    )
    print("First 3 cells: %s" % (str(list(adata.obs_names[:3]))))
    print("First 5 genes: %s" % (str(list(adata.var_names[:5]))))

    # Load .cov file
    if COV_FILE is not None:
        df_cov = pd.read_csv(COV_FILE, sep="\t", index_col=0)
        print(
            "--cov-file loaded: covariates=%s (sys_time=%0.1fs)"
            % (str(list(df_cov.columns)), time.time() - sys_start_time)
        )
        for col in df_cov.columns:
            print(
                "First 5 values for '%s': %s" % (col, str(list(df_cov[col].values[:5])))
            )
    else:
        df_cov = None

    # Load .gs file
    dict_gs = scdrs.util.load_gs(
        GS_FILE,
        src_species=GS_SPECIES,
        dst_species=H5AD_SPECIES,
        to_intersect=adata.var_names,
    )

    print(
        "--gs-file loaded: n_trait=%d (sys_time=%0.1fs)"
        % (len(dict_gs), time.time() - sys_start_time)
    )
    print("Print info for first 3 traits:")
    for gs in list(dict_gs)[:3]:
        print(
            "First 3 elements for '%s': %s, %s"
            % (gs, str(dict_gs[gs][0][:3]), str(dict_gs[gs][1][:3]))
        )
    print("")

    ###########################################################################################
    ######                                  Computation                                  ######
    ###########################################################################################

    # Preprocess
    print("Preprocessing:")
    scdrs.preprocess(
        adata, cov=df_cov, adj_prop=ADJ_PROP, n_mean_bin=20, n_var_bin=20, copy=False
    )
    print("")

    # Compute score
    print("Computing scDRS score:")
    for trait in dict_gs:
        gene_list, gene_weights = dict_gs[trait]
        if len(gene_list) < 10:
            print(
                "trait=%s: skipped due to small size (n_gene=%d, sys_time=%0.1fs)"
                % (trait, len(gene_list), time.time() - sys_start_time)
            )
            continue

        df_res = scdrs.score_cell(
            adata,
            gene_list,
            gene_weight=gene_weights,
            ctrl_match_key=CTRL_MATCH_OPT,
            n_ctrl=N_CTRL,
            weight_opt=WEIGHT_OPT,
            return_ctrl_raw_score=FLAG_RETURN_CTRL_RAW_SCORE,
            return_ctrl_norm_score=FLAG_RETURN_CTRL_NORM_SCORE,
            verbose=False,
        )

        df_res.iloc[:, 0:6].to_csv(
            os.path.join(OUT_FOLDER, "%s.score.gz" % trait),
            sep="\t",
            index=True,
            compression="gzip",
        )
        if FLAG_RETURN_CTRL_RAW_SCORE | FLAG_RETURN_CTRL_NORM_SCORE:
            df_res.to_csv(
                os.path.join(OUT_FOLDER, "%s.full_score.gz" % trait),
                sep="\t",
                index=True,
                compression="gzip",
            )
        v_fdr = multipletests(df_res["pval"].values, method="fdr_bh")[1]
        n_rej_01 = (v_fdr < 0.1).sum()
        n_rej_02 = (v_fdr < 0.2).sum()
        print(
            "Trait=%s, n_gene=%d: %d/%d FDR<0.1 cells, %d/%d FDR<0.2 cells (sys_time=%0.1fs)"
            % (
                trait,
                len(gene_list),
                n_rej_01,
                df_res.shape[0],
                n_rej_02,
                df_res.shape[0],
                time.time() - sys_start_time,
            )
        )
    return


def munge_gs(
    out_file: str,
    pval_file: str = None,
    zscore_file: str = None,
    weight: str = "zscore",
    fdr: float = None,
    fwer: float = None,
    n_min: int = 100,
    n_max: int = 1000,
):
    """
    Convert a .tsv GWAS gene statistics file to an scDRS .gs file.
    
    Input file (`pval_file` or `zscore_file`) format: 
    - .tsv file 
    - First column corresponds to gene names, preferably with header 'GENE'.
    - Each of other columns corresponds to a disease with header being the disease name
        and the values being either the gene-level p-values (`pval_file`) or
        gene-level one-sided z-scores (`zscore_file`).

    For example, `pval_file` looks like

        GENE    BMI    HEIGHT
        OR4F5   0.001  0.01
        DAZ3    0.01   0.001
        ...
    
    Main steps.
    1. Read result from a p-value or a z-score file
    2. Select a subset of disease genes for each disease:
        - If both `fdr` and `fwer` are None, select the top `n_max` genes.
        - If `fdr` is not None, select genes based on FDR and cap between `n_min` and `n_max`. 
        - If `fwer` is not None, select genes based on FWER and cap between `n_min` and `n_max`. 
    3. Assign gene weights based on `--weight`.
    4. Write the .gs file to `out_file`.
    
    Parameters
    ----------
    out_file : str
        Path to the output .gs file.
    pval_file : str, optional
        P-value file. A .tsv file with first column corresponding to genes and other columns 
        corresponding to p-values of traits (one trait per column). One of `pval_file` and 
        `zscore_file` is expected. Default is None.
    zscore_file : str, optional
        Z-score file. A .tsv file with first column corresponding to genes and other columns 
        corresponding to z-scores of traits (one trait per column). One of `pval_file` and 
        `zscore_file` is expected. Default is None.
    weight : str, optional
        Gene weight options. One of "zscore" or "uniform". Default is "zscore".
    fdr : float, optional
        FDR threshold. Default is None. E.g., `--fdr 0.05`
    fwer : float, optional
        FWER threshold. Default is None. E.g., `--fwer 0.05`
    n_min : int, optional
        Minimum number of genes for each gene set. Default is 100. E.g., `--n-min 100`
    n_max : int, optional
        Maximum number of genes for each gene set. Default is 1000. E.g., `--n-min 1000`
    

    Examples
    --------
    scdrs munge-gs \
        --out_file <out> \
        --pval-file <pval_file> \
        --weight <weight> \
        --n-max <n_max>
    """

    sys_start_time = time.time()

    ###########################################################################################
    ######                                    Parse Options                              ######
    ###########################################################################################
    header = get_cli_head()
    header += "Call: scdrs munge-gs \\\n"

    assert (
        sum([(pval_file is not None), (zscore_file is not None)]) == 1
    ), "One of --pval-file and --zscore-file is expected."
    if pval_file is not None:
        header += "--pval-file %s \\\n" % pval_file
    if zscore_file is not None:
        header += "--zscore-file %s \\\n" % zscore_file

    assert weight in [
        "zscore",
        "uniform",
    ], "--weight needs to be one of 'zscore', 'uniform'"
    header += "--weight %s \\\n" % weight

    assert (fdr is None) or (
        fwer is None
    ), "At most one of --fdr and --fwer is allowed."
    if fdr is not None:
        header += "--fdr %s \\\n" % fdr
    if fwer is not None:
        header += "--fwer %s \\\n" % fdr

    n_min = min(n_min, n_max)
    header += "--n-min %s \\\n" % n_min
    header += "--n-max %s \\\n" % n_max

    assert out_file is not None, "--out-file is expected."
    header += "--out-file %s\n" % out_file
    print(header)

    ###########################################################################################
    ######                                     Load data                                 ######
    ###########################################################################################
    if pval_file is not None:
        df_pval = pd.read_csv(pval_file, sep="\t", index_col=0)
        print(
            "--pval-file loaded: n_gene=%d, n_trait=%d (sys_time=%0.1fs)"
            % (df_pval.shape[0], df_pval.shape[1], time.time() - sys_start_time)
        )
        print("Print info for the first 3 traits and first 10 genes")
        print("%-20s" % "Traits", str(list(df_pval.columns[:3])))
        for gene in df_pval.index[:10]:
            print("%-20s" % gene, str(list(df_pval.loc[gene, df_pval.columns[:3]])))
        # Check index is unique
        if not df_pval.index.is_unique:
            raise ValueError(
                "Gene names in the provided p-value files are not unique: ",
                ",".join(df_pval.index[df_pval.index.duplicated()]),
                ". Please make sure the gene names are unique beforehand.",
            )

        # Check range
        max_ = df_pval.max(skipna=True).max()
        min_ = df_pval.min(skipna=True).min()
        if (min_ > 0) and (max_ < 1):
            print("--pval-file values are all between 0 and 1. Seems fine.")
        else:
            print("Warning: pval-file are not all between 0 and 1.")
        print("")

    if zscore_file is not None:
        df_zscore = pd.read_csv(zscore_file, sep="\t", index_col=0)
        print(
            "--zscore-file loaded: n_gene=%d, n_trait=%d (sys_time=%0.1fs)"
            % (df_zscore.shape[0], df_zscore.shape[1], time.time() - sys_start_time)
        )
        print("Print info for the first 3 traits and first 10 genes")
        print("%-20s" % "Traits", str(list(df_zscore.columns[:3])))
        for gene in df_zscore.index[:10]:
            print("%-20s" % gene, str(list(df_zscore.loc[gene, df_zscore.columns[:3]])))

        # Check index is unique
        if not df_zscore.index.is_unique:
            raise ValueError(
                "Gene names in the provided z-score files are not unique: ",
                ",".join(df_zscore.index[df_zscore.index.duplicated()]),
                ". Please make sure the gene names are unique beforehand.",
            )

        # Check range
        max_ = df_zscore.max(skipna=True).max()
        min_ = df_zscore.min(skipna=True).min()
        if (min_ < 0) and (max_ > 1):
            print("--zscore-file have values above 1 or below 0. Seems fine.")
        else:
            print("Warning: zscore-file values are all between 0 and 1.")

        df_pval = df_zscore.copy()
        for col in df_pval:
            df_pval[col] = scdrs.util.zsc2pval(df_zscore[col])
        print("")

    trait_list = sorted(df_pval.columns)
    ###########################################################################################
    ######                                  Computation                                  ######
    ###########################################################################################
    dict_gene_weights = {"TRAIT": [], "GENESET": []}
    for trait in trait_list:
        # Drop missing p-values
        df_trait_pval = df_pval[[trait]].copy()
        df_trait_pval.dropna(axis=0, inplace=True)

        # Determine number of disease genes
        if fdr is not None:
            n_gene = multipletests(
                df_trait_pval[trait].values, alpha=fdr, method="fdr_bh"
            )[0].sum()
        elif fwer is not None:
            n_gene = multipletests(
                df_trait_pval[trait].values, alpha=fwer, method="bonferroni"
            )[0].sum()
        else:
            # If both are None, select top n_max genes
            n_gene = n_max

        # Restrict `n_gene` to be between `n_min` and `n_max`
        n_gene = min(n_gene, n_max)
        n_gene = max(n_gene, n_min)

        # Select `n_gene` genes with the smallest p-values
        df_trait_pval.sort_values(trait, ascending=True, inplace=True)
        df_trait_pval = df_trait_pval.iloc[:n_gene]

        gene_list = df_trait_pval.index
        gene_pvals = df_trait_pval[trait].values.clip(min=1e-100)

        if weight == "zscore":
            gene_weights = scdrs.util.pval2zsc(gene_pvals).clip(max=10)
        if weight == "uniform":
            gene_weights = np.ones(len(gene_list))

        dict_gene_weights["TRAIT"].append(trait)
        dict_gene_weights["GENESET"].append(
            ",".join([f"{g}:{w:.5g}" for g, w in zip(gene_list, gene_weights)])
        )
    df_gs = pd.DataFrame(dict_gene_weights)
    df_gs.to_csv(out_file, sep="\t", index=False)
    print(
        "Finish munging %d gene sets (sys_time=%0.1fs)"
        % (df_gs.shape[0], time.time() - sys_start_time)
    )
    return


def perform_downstream(
    h5ad_file: str,
    score_file: str,
    out_folder: str,
    group_analysis: str = None,
    corr_analysis: str = None,
    gene_analysis: str = None,
    flag_filter_data: bool = True,
    flag_raw_count: bool = True,
    knn_n_neighbors: int = 15,
    knn_n_pcs: int = 20,
):
    """
    Perform scDRS downstream analyses based on precomputed scDRS `.full_score.gz` files.
    
    --group-analysis
        For a given cell-group-level annotation (e.g., tissue or cell type), assess cell 
        group-disease association (control-score-based MC tests using 5% quantile) and within-cell
        group disease-association heterogeneity (control-score-based MC tests using Geary's C).
        
    --corr-analysis
        For a given individual cell-level variable (e.g., T cell effectorness gradient), assess 
        association between disease and the individual cell-level variable (control-score-based 
        MC tests using Pearson's correlation).
    
    --gene-analysis: 
        Compute Pearson's correlation between expression of each gene and the scDRS disease score.

    Parameters
    ----------
    h5ad_file : str
        Single-cell .h5ad file.
    score_file : str
        scDRS .full_score.gz file. Use “@” to specify multiple file names, e.g.,
        <score_folder>/@.full_score.gz. However, <score_folder> should not contain “@”.
    out_folder : str
        Output folder.
    group_analysis : str, optional
        Comma-seperated column names for cell group annotations in adata.obs.columns, 
        e.g., cell types or tissues. Results are saved as <out_folder>/<trait>.scdrs_group.<annot>, 
        one file per annotation. Default is None.
    corr_analysis : str, optional
        Comma-seperated column names for continuous annotations in adata.obs.columns, 
        e.g., T cell effectorness gradient. Results are saved as 
        <out_folder>/<trait>.scdrs_cell_corr for all variables. Default is None.
    gene_analysis : str, optional
        Flag to perform the gene prioritization by correlating gene expression with scDRS scores.
        Specifying --gene-analysis without any arguments. Results are saved as 
        <out_folder>/<trait>.scdrs_gene for all genes. Default is None.
    flag_filter_data : bool, optional
        If to apply minimal cell and gene filtering to h5ad_file. Default is True.
    flag_raw_count : bool, optional
        If to apply size-factor normalization and log1p-transformation to h5ad_file.
        Default is True.
    knn_n_neighbors : int, optional
        `n_neighbors` for computing KNN graph using `sc.pp.neighbors`.
        Default is 15 (consistent with the TMS pipeline).
    knn_n_pcs : int, optional
        `n_pcs` for computing KNN graph using `sc.pp.neighbors`.
        Default is 20 (consistent with the TMS pipeline).
        
    Examples
    --------
    scdrs perform-downstream \
        --h5ad-file <h5ad_file> \
        --score-file <full_score_file> \
        --out-folder <out_folder> \
        --group-analysis cell_type \
        --corr-analysis causal_variable,non_causal_variable,covariate \
        --gene-analysis \
        --flag-filter-data True \
        --flag-raw-count True
    """

    sys_start_time = time.time()

    ###########################################################################################
    ######                                    Parse Options                              ######
    ###########################################################################################
    header = get_cli_head()
    header += "Call: scdrs perform-downstream \\\n"

    assert h5ad_file is not None, "--h5ad-file is expected."
    header += "--h5ad-file %s \\\n" % h5ad_file

    assert score_file is not None, "--score-file is expected."
    header += "--score-file %s \\\n" % score_file

    assert out_folder is not None, "--out-folder is expected."
    header += "--out-folder %s \\\n" % out_folder

    assert (
        sum(
            [
                group_analysis is not None,
                corr_analysis is not None,
                gene_analysis is not None,
            ]
        )
        > 0
    ), "Expect at least one of `--group_analysis`, `--corr_analysis`, `--gene_analyis`"
    if group_analysis is not None:
        # Determine if string or list_like using duck-typing
        input_type = scdrs.util.str_or_list_like(group_analysis)
        if input_type == "str":
            group_analysis = group_analysis.split(",")
        elif input_type == "list_like":
            group_analysis = list(group_analysis)
        else:
            raise ValueError("Expect --group_analysis to be a comma-separated string.")
        # group_analysis header
        header += "--group-analysis %s\\\n" % ",".join(group_analysis)
    if corr_analysis is not None:
        # Determine if string or list_like using duck-typing
        input_type = scdrs.util.str_or_list_like(corr_analysis)
        if input_type == "str":
            corr_analysis = corr_analysis.split(",")
        elif input_type == "list_like":
            corr_analysis = list(corr_analysis)
        else:
            raise ValueError("Expect --corr_analysis to be a comma-separated string.")
        # corr_analysis header
        header += "--corr-analysis %s \\\n" % ",".join(corr_analysis)
    if gene_analysis is not None:
        header += "--gene-analysis %s \\\n" % gene_analysis

    header += "--flag-filter-data %s \\\n" % flag_filter_data
    header += "--flag-raw-count %s \\\n" % flag_raw_count
    header += "--knn-n-neighbors %s \\\n" % knn_n_neighbors
    header += "--knn-n-pcs %s\n" % knn_n_pcs
    print(header)

    ###########################################################################################
    ######                                     Load data                                 ######
    ###########################################################################################
    adata = scdrs.util.load_h5ad(
        h5ad_file=h5ad_file,
        flag_filter_data=flag_filter_data,
        flag_raw_count=flag_raw_count,
    )
    print(
        "--h5ad-file loaded: n_cell=%d, n_gene=%d (sys_time=%0.1fs)"
        % (adata.shape[0], adata.shape[1], time.time() - sys_start_time)
    )
    print("First 3 cells: %s" % (str(list(adata.obs_names[:3]))))
    print("First 5 genes: %s" % (str(list(adata.var_names[:5]))))
    print(score_file)
    dict_score = scdrs.util.load_scdrs_score(score_file)
    print(dict_score)
    print(
        "--score-file loaded: n_trait=%d (sys_time=%0.1fs)"
        % (len(dict_score), time.time() - sys_start_time)
    )
    assert len(dict_score) > 0, "Expect at least 1 score file."
    print("Print info for the first trait, first 3 cells, and first 8 columns:")
    trait = list(dict_score)[0]
    print("%-20s" % "Trait", trait)
    print("%-20s" % "Cells", str(list(dict_score[trait].index[:3])))
    for col in dict_score[trait].columns[:8]:
        print("%-20s" % col, str(dict_score[trait][col].values[:3]))

    # Check cols in `group_analysis` are also in `adata.obs`
    if group_analysis is not None:
        assert (
            len(set(group_analysis) - set(adata.obs)) == 0
        ), "Missing --group-analysis variables from `adata.obs.columns`."

    # Check cols in `corr_analysis` are also in `adata.obs`
    if corr_analysis is not None:
        assert (
            len(set(corr_analysis) - set(adata.obs)) == 0
        ), "Missing --corr-analysis variables from `adata.obs.columns`."
    print("")
    ###########################################################################################
    ######                                  Computation                                  ######
    ###########################################################################################
    if group_analysis is not None:
        print("Performing scDRS group-analysis")
        # Compute KNN if not present in `adata`
        if "connectivities" not in adata.obsp:
            if knn_n_pcs > (min(adata.shape) - 1):
                print(
                    "`knn_n_pcs`=%d > `min(adata.shape)-1`=%d; set `knn_n_pcs`=%d"
                    % (knn_n_pcs, min(adata.shape) - 1, min(adata.shape) - 1)
                )
                knn_n_pcs = min(adata.shape) - 1
            sc.pp.pca(adata, n_comps=knn_n_pcs)
            sc.pp.neighbors(adata, n_neighbors=knn_n_neighbors, n_pcs=knn_n_pcs)
            print(
                "`connectivities` not found in `adata.obsp`; run `sc.pp.neighbors` first"
            )
        # scDRS group-level analysis
        for trait in dict_score:
            dict_df_res = scdrs.method.downstream_group_analysis(
                adata=adata,
                df_full_score=dict_score[trait],
                group_cols=group_analysis,
            )
            for group_col in group_analysis:
                dict_df_res[group_col].to_csv(
                    os.path.join(
                        out_folder,
                        f"{trait}.scdrs_group.{group_col.replace(' ', '_').replace(',', '_')}",
                    ),
                    sep="\t",
                    index=True,
                )
            print(
                "Finish group-analysis for %s (sys_time=%0.1fs)"
                % (trait, time.time() - sys_start_time)
            )
        print("")

    if corr_analysis is not None:
        print("Performing scDRS corr-analysis")
        for trait in dict_score:
            df_res = scdrs.method.downstream_corr_analysis(
                adata=adata, df_full_score=dict_score[trait], var_cols=corr_analysis
            )
            df_res.to_csv(
                os.path.join(out_folder, f"{trait}.scdrs_cell_corr"),
                sep="\t",
                index=True,
            )
            print(
                "Finish corr-analysis for %s (sys_time=%0.1fs)"
                % (trait, time.time() - sys_start_time)
            )
        print("")

    if gene_analysis is not None:
        print("Performing scDRS gene-analysis")
        for trait in dict_score:
            df_res = scdrs.method.downstream_gene_analysis(
                adata=adata, df_full_score=dict_score[trait]
            )
            # save results
            df_res.to_csv(
                os.path.join(out_folder, f"{trait}.scdrs_gene"), sep="\t", index=True
            )
            print(
                "Finish gene-analysis for %s (sys_time=%0.1fs)"
                % (trait, time.time() - sys_start_time)
            )
        print("")

    return


if __name__ == "__main__":
    fire.Fire()
