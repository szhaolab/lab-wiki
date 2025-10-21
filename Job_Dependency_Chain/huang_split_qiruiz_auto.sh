#!/bin/bash

#SBATCH --job-name=zqr_huang_split
#SBATCH --output=/dartfs/rc/lab/S/Szhao/qiruiz/perturb-predict-apply/task/result/huang_split_%A_%x_%j.out
#SBATCH --time=06:00:00             
#SBATCH --partition=standard
#SBATCH --account=nccc
#SBATCH --ntasks=1                     
#SBATCH --cpus-per-task=1  
#SBATCH --mem=750G 
#SBATCH --mail-user=f0070pp@dartmouth.edu
#SBATCH --mail-type=BEGIN,END,FAIL          

idx=${IDX:-$1}
if [[ -z "$idx" ]]; then
  echo "ERROR: IDX (split index) not provided; exiting."
  exit 1
fi

echo "$SLURM_JOB_ID  starting split $idx  at $(date) on $(hostname)"

source /optnfs/common/miniconda3/etc/profile.d/conda.sh
conda activate gears

rm -rf /dartfs/rc/lab/S/Szhao/perturbation_prediction/SeqExpDesign/vcc/data/sc/Huang-HCT116/*

cd /dartfs/rc/lab/S/Szhao/perturbation_prediction/SeqExpDesign/vcc/data
python -u huang_parallel_split_adata.py "$idx"

echo "Split $idx completed"
echo "Finished execution at: $(date)"
