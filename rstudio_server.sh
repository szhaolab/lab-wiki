#!/bin/bash
#SBATCH --job-name=rstudio_server
#SBATCH --time=3-00:00:00
#SBATCH --mem=20G
#SBATCH --output=rstudio_server.txt
#SBATCH --error=rstudio_server.err
#SBATCH --account=zhao
#SBATCH --partition=a5000
#SBATCH --nodes=1                    # Number of nodes you require
#SBATCH --ntasks=1                   # Total # of tasks across all nodes
#SBATCH --cpus-per-task=10            # Cores per task (>1 if multithread tasks)

# Create the local filesystem
TMPDIR=$HOME/rstudio-tmp
mkdir -p $TMPDIR/tmp/rstudio-server
mkdir -p $TMPDIR/var/{lib,run}
uuidgen > $TMPDIR/tmp/rstudio-server/secure-cookie-key
chmod 600 $TMPDIR/tmp/rstudio-server/secure-cookie-key

# Set OMP_NUM_THREADS to prevent OpenBLAS (and any other OpenMP-enhanced
# libraries used by R) from spawning more threads than the number of processors
# allocated to the job.
export SINGULARITYENV_OMP_NUM_THREADS=${SLURM_JOB_CPUS_PER_NODE}

# Don't run on the login node, but on a compute node, get the name.
node=$(hostname -s)

# Run the container
export SINGULARITYENV_RSTUDIO_SESSION_TIMEOUT=0
PASSWORD='aaa' singularity exec \
--bind $TMPDIR/var/lib:/var/lib/rstudio-server \
--bind $TMPDIR/var/run:/var/run/rstudio-server \
--bind $TMPDIR/tmp:/tmp \
--bind /dartfs/rc/lab/S/Szhao \
$HOME/rstudio.simg \
rserver \
--auth-none=0 \
--auth-pam-helper-path=pam-helper \
--auth-stay-signed-in-days=30 \
--auth-timeout-minutes=0 \
--www-address=${node} \
--www-port=8789 \
--server-user $USER

# Exit
printf 'rserver exited' 1>&2
