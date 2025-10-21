#!/bin/bash

#SBATCH --job-name=zqr_wilcoxon
#SBATCH --output=/dartfs/rc/lab/S/Szhao/qiruiz/perturb-predict-apply/task/result/huang_wilcoxon_%A_%a.out
#SBATCH --time=02:00:00             
#SBATCH --partition=standard
#SBATCH --account=nccc        
#SBATCH --ntasks=1                     
#SBATCH --cpus-per-task=1  
#SBATCH --mem=24G 
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=f0070pp@dartmouth.edu
          

echo $SLURM_JOB_ID starting execution `date` on `hostname`

source /software/python-anaconda-2022.05-el8-x86_64/etc/profile.d/conda.sh
conda activate gears_cpu

cd /dartfs/rc/lab/S/Szhao/perturbation_prediction/SeqExpDesign/vcc/data

python -u huang_parallel_huang_wilcoxon.py ${SLURM_ARRAY_TASK_ID}
echo "Finished execution at: `date`"
