import os
import sys
os.environ["OMP_NUM_THREADS"] = "11"
os.environ["OPENBLAS_NUM_THREADS"] = "8" # export OPENBLAS_NUM_THREADS=4 
os.environ["MKL_NUM_THREADS"] = "11" # export MKL_NUM_THREADS=6
os.environ["VECLIB_MAXIMUM_THREADS"] = "8" # export VECLIB_MAXIMUM_THREADS=4
os.environ["NUMEXPR_NUM_THREADS"] = "11" # export NUMEXPR_NUM_THREADS=6
os.environ["NUMBA_CACHE_DIR"]='/tmp/numba_cache'
import numpy as np
import pandas as pd
import scipy as sp
import scipy.sparse

import pickle

import anndata as ad
import scanpy as sc

import numba
import multiprocessing
# njobs = max(1, multiprocessing.cpu_count())
njobs = min(1, multiprocessing.cpu_count())
numba.set_num_threads(njobs)

import gc
from tqdm import tqdm
print(pd.__version__, sc.__version__, ad.__version__)


def summarize(adata):
    N_C, N_G = adata.shape
    N_P = adata.obs['perturbation'].nunique()
    N_P_2 = adata.obs['perturbation'][adata.obs['perturbation'].str.contains('_')].nunique()
    return N_C, N_G, N_P, N_P - N_P_2, N_P_2

def comp_bulk_expressions(adata, key='perturbation'):
    '''
    Calculate the bulk expressions (in the log-scale) in the given DataFrame.
    This function groups the DataFrame by the 'perturbation' column and then 
    applies a transformation to calculate the average effect. The transformation 
    involves taking logarithm of the mean of the exponentiated values minus one for each group.

    Parameters
    ----------
    adata : anndata.AnnData or pandas.DataFrame
        An AnnData or a DataFrame containing the data with a column 'key'.
    key : str, optional
        The column name to group by, default is 'condition'.

    Returns
    -------
    adata_bulk : anndata.AnnData or pandas.DataFrame
        An AnnData or a DataFrame with the average effect of each perturbation.
    '''
    if isinstance(adata, ad.AnnData):
        df = adata.to_df()
        key_pert = adata.obs[key]        
    else:
        df = adata
        key_pert = key
    obs = adata.obs.drop_duplicates(subset=[key]).set_index(key).sort_values(key)
    obs['n_cells'] = adata.obs.groupby(key, observed=True).size()
    var = adata.var
    # save memory by removing the original adata
    # del adata
    gc.collect()
    df = df.astype(np.float32)  # Ensure consistent data type for calculations
    grouped = df.groupby(key_pert, observed=True)
    sums = grouped.sum().astype(np.float32)
    sizes = grouped.size().astype(np.float32)
    means = sums / sizes.values[:, None]
    stds = grouped.std().astype(np.float32)
    adata_bulk = means  # You can return or use both means and stds as needed
    del df
    gc.collect()
    adata_bulk = ad.AnnData(
        X=sp.sparse.csr_matrix(adata_bulk.values), 
        obs=obs, 
        var=var
        )
    return adata_bulk, stds

def comp_bulk_expressions_batch(adata, key='perturbation', group_size=1000):
    """
    Wrapper function to calculate bulk expressions in smaller groups to save memory.

    Parameters
    ----------
    adata : anndata.AnnData
        An AnnData object containing the data with a column 'key'.
    key : str, optional
        The column name to group by, default is 'perturbation'.
    group_size : int, optional
        Number of perturbation conditions to process in each group, default is 10.

    Returns
    -------
    adata_bulk : anndata.AnnData
        An AnnData object with the average effect of each perturbation.
    """
    perturbations = np.sort(np.array(adata.obs[key].unique()))
    grouped_bulk = []
    stds = []
    for i in tqdm(range(0, len(perturbations), group_size), desc='Processing perturbations'):
        subset_perturbations = perturbations[i:(i+group_size)]
        sub_adata = adata[adata.obs[key].isin(subset_perturbations)]
        if sub_adata.shape[0] == 0:
            continue
        sub_bulk, std = comp_bulk_expressions(sub_adata, key=key)
        grouped_bulk.append(sub_bulk.copy())        
        stds.append(std)
    # Concatenate all sub-bulk results
    adata_bulk = ad.concat(grouped_bulk, merge='same')
    stds = pd.concat(stds, axis=0)
    adata_bulk.uns['std'] = stds.copy()
    return adata_bulk



datasets = [
    # single perturbation
    "Adamson", "Frangieh",    
    "Replogle-GW-k562", "Replogle-E-k562", "Replogle-E-rpe1",
    "Tian-crispra", "Tian-crispri",
    "Jiang-IFNB", "Jiang-IFNG", "Jiang-INS", "Jiang-TGFB", "Jiang-TNFA",
    "Huang-HCT116", "Huang-HEK293T",

    "Nadig-HEPG2", "Nadig-JURKAT",

    # double perturbation
    "Norman", "Wessels",
]

path_origin = 'origin/'
path_sc = 'sc/';os.makedirs(path_sc, exist_ok=True)
path_bulk = 'bulk/';os.makedirs(path_bulk, exist_ok=True)
path_bulk_log = 'bulk_log/';os.makedirs(path_bulk_log, exist_ok=True)

dataset = "Huang-HCT116"
print(f'Processing {dataset}...')

adata = sc.read_h5ad(f'{path_origin}{dataset}.h5ad')
print(adata)
if dataset == 'Adamson':
    adata.obs.rename({'gene':'perturbation'}, axis=1, inplace=True)
    adata.obs.loc[:,'perturbation'] = adata.obs['perturbation'].astype(str).replace({'CTRL':'control'}).values
    adata = adata[adata.obs['perturbation']!='None']
elif dataset.startswith('Huang'):
    adata.obs.rename({'gene_target':'perturbation'}, axis=1, inplace=True)
    adata.obs.loc[:,'perturbation'] = adata.obs['perturbation'].astype(str).replace({'Non-Targeting':'control'}).values
elif dataset.startswith('Nadig'):
    adata.obs.rename({'gene':'perturbation'}, axis=1, inplace=True)
    adata.obs['perturbation'] = adata.obs['perturbation'].astype(str)
    adata.obs.loc[:,'perturbation'] = adata.obs['perturbation'].astype(str).replace({'non-targeting':'control'}).values
    adata.var.set_index('gene_name', inplace=True)
elif dataset.startswith('Jiang'):
    raise NotImplementedError("Currently not supported for Jiang dataset.")

print(summarize(adata))

# filter out cells
if dataset.startswith('Huang'):
    print('Skipping filtering cells for Huang datasets')
    print('Min genes by counts:', adata.obs['n_genes_by_counts'].min())
else:
    sc.pp.filter_cells(adata, min_genes=100)
print(summarize(adata))

# filter perturbation condition
ncells_pert = adata.obs.groupby('perturbation', observed=True).size()
min_cells = 25 if dataset.startswith('Nadig') else 50
valid_pert = np.array(ncells_pert[ncells_pert >= min_cells].index)
valid_pert = valid_pert[np.isin(valid_pert, adata.var.index)]
# TODO: filter inefficient perturbations
adata = adata[adata.obs['perturbation'].isin(np.append(valid_pert, ['control']))]
print(summarize(adata))


# # filter cells by perturbation quantile effect
# adata = filter_cells_by_pert_effect(adata)
# print(summarize(adata))

if not sp.sparse.issparse(adata.X):
    adata.X = scipy.sparse.csr_matrix(adata.X)

# Filter genes with less than 100 cells in the control groups, but keep those in adata.obs.index
gene_filter = (np.sum(adata[adata.obs['perturbation'] == 'control'].X > 0, axis=0) >= 100) | adata.var.index.isin(valid_pert)
adata = adata[:, gene_filter]

duplicate_var_names = adata.var_names[adata.var_names.duplicated()]
print(f"Duplicate var names: {duplicate_var_names}")
adata = adata[:, ~adata.var_names.duplicated()]
# sc.pp.filter_genes(adata, min_cells=100)
# sc.pp.filter_genes(adata, max_counts=10) # this seems to be too strict
print(summarize(adata))


# Add information
adata.obs.loc[:,'dataset'] = dataset
# TODO: add celltype/pathway information
# if 'pathway' not in adata.obs:
if dataset.startswith('Huang') or dataset.startswith('Nadig'):
    adata.obs.loc[:,'celltype'] = dataset.split('-')[1]    
elif not dataset.startswith('Jiang'):
    dict_cts = {
        'Adamson': 'K562',
        'Replogle-GW-k562': 'K562',
        'Replogle-E-k562': 'K562',
        'Replogle-E-rpe1': 'RPE1',
        'Frangieh':'melanoma',
        "Tian-crispra": 'iPSC', 
        "Tian-crispri": 'iPSC'
        }
    adata.obs.loc[:,'celltype'] = dict_cts[dataset]

    adata.X = scipy.sparse.csr_matrix(adata.X)

print(summarize(adata))


col = adata.obs['perturbation'].astype(str)
perts = sorted(p for p in col.unique() if p != 'control')
# pert_path = "/project/jingshuw/SeqExpDesign/vcc/data/pert_Huang-HCT116.csv"
# pd.Series(perts, name="perturbation").to_csv(pert_path, index=False)
print("The number of perturbations:", len(perts))

batch_size = 200
batch_idx = int(sys.argv[1])
start = (batch_idx - 1) * batch_size
end = min(batch_idx * batch_size, len(perts))

batch_perts = perts[start:end]
print(f"Batch {batch_idx}: {len(batch_perts)} perturbations ({start+1}-{end})")

for pert in batch_perts:
    adata_split = adata[col.isin([pert, 'control'])].copy()
    print(f"[PAIR] pert={pert} | cells={adata_split.n_obs} | genes={adata_split.n_vars}")
    out_path = os.path.join(path_sc, dataset, f'{pert}.h5ad')
    adata_split.write_h5ad(out_path)

# # adata = sc.read_h5ad(f'{path_sc}{dataset}_overlap_vcc.h5ad')

# ##############################################################################
# #
# # Save the bulk expression data
# #
# ##############################################################################
# # print('Save the bulk expression data')

# # For pseudo bulk aggregation
# # Aggregate counts of adata.X according to perturbation
# # adata_bulk = comp_bulk_expressions_batch(adata, key='perturbation')

# # # calculate the library size
# # adata_bulk.obs['n_counts'] = adata_bulk.X.sum(axis=1)

# # print(adata_bulk)
# # adata_bulk.write_h5ad(f'{path_bulk}{dataset}_overlap_vcc.h5ad')



# ##############################################################################
# #
# # Save the bulk expression data (after log transformantion)
# #
# ##############################################################################
# # print('Save the bulk expression data (after log transformantion)')


# # For mean aggreagation
# sc.pp.normalize_total(adata)
# sc.pp.log1p(adata)

# # # Aggregate counts of adata.X according to perturbation
# # adata_bulk = comp_bulk_expressions_batch(adata, key='perturbation')

# # # calculate the library size
# # adata_bulk.obs['n_counts'] = adata_bulk.X.sum(axis=1)

# # print(adata_bulk)
# # adata_bulk.write_h5ad(f'{path_bulk_log}{dataset}_overlap_vcc.h5ad')



# ##############################################################################
# #
# # Calculate DE genes from single-cell data
# #
# ##############################################################################
# print('Calculate DE genes from single-cell data')

# path_de = f'de/';os.makedirs(path_de, exist_ok=True)
# data_dir = 'sc/'

# def calculate_de_genes_group(adata, rankby_abs, test_name='t-test'):
#     perturbations = adata.obs['perturbation'].unique()
#     tie_correct = 'tie' if test_name == 'wilcoxon' else 't-test'
#     sc.tl.rank_genes_groups(
#         adata, groupby='perturbation', reference='control',
#         n_genes=adata.shape[1], rankby_abs=rankby_abs=='abs',
#         method=test_name, tie_correct=tie_correct=='tie',
#         use_raw=False, n_jobs=njobs)
#     df = pd.DataFrame(adata.uns['rank_genes_groups']['names']).T
#     df_rank = df.apply(lambda x: pd.Series(x.index, index=x.values)[adata.var.index], axis=1).astype(int)
#     df_rank = df_rank[sorted(df_rank.columns)]
#     de_result = {"perturbations": perturbations, "rank_genes_groups": adata.uns['rank_genes_groups'], "df_rank": df_rank}
#     return de_result


# def calculate_de_genes(adata, path_de, dataset, test_name='t-test'):
#     """
#     Calculate DE genes from single-cell data using different statistical tests.
    
#     Parameters
#     ----------
#     adata : anndata.AnnData
#         The input AnnData object containing single-cell data.
#     path_de : str
#         The path where DE results will be saved.
    
#     Returns
#     -------
#     None
#         Results are saved to disk as pickle files.
#     """
#     cell_types = adata.obs['celltype'].unique()
#     per = [p for p in adata.obs['perturbation'].astype(str).unique() if p != 'control']; assert len(per)==1; pert_name = per[0]
#     for rankby_abs in ['abs']: #['abs', 'noabs']
#         path = f'{path_de}{test_name}/{rankby_abs}/{dataset}/';os.makedirs(path, exist_ok=True)
#         assert len(cell_types) == 1
#         de_genes = calculate_de_genes_group(adata, rankby_abs, test_name=test_name)
            
#         with open(f'{path}{pert_name}.pkl', 'wb') as f:
#             pickle.dump(de_genes, f)



# for test_name in ['wilcoxon']:
#     calculate_de_genes(adata, path_de, dataset, test_name=test_name)