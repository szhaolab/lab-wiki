#!/bin/bash
#SBATCH --job-name=rstudio_server
#SBATCH --time=29-00:00:00
#SBATCH --mem=32G
#SBATCH --output=rstudio_server.txt
#SBATCH --error=rstudio_server.err
#SBATCH --account=nccc

# Create the local filesystem
TMPDIR=$HOME/rstudio-tmp
mkdir -p $TMPDIR/tmp/rstudio-server
mkdir -p $TMPDIR/var/{lib,run}
uuidgen > $TMPDIR/tmp/rstudio-server/secure-cookie-key
chmod 600 $TMPDIR/tmp/rstudio-server/secure-cookie-key

# Don't run on the login node, but on a compute node, get the name.
node=$(hostname -s)

# Run the container
PASSWORD='aaa' singularity exec \
--bind $TMPDIR/var/lib:/var/lib/rstudio-server \
--bind $TMPDIR/var/run:/var/run/rstudio-server \
--bind $TMPDIR/tmp:/tmp \
--bind /dartfs/rc/lab/S/Szhao \
$HOME/rstudio.simg \
rserver \
--auth-none=0 \
--auth-pam-helper-path=pam-helper \
--www-address=${node} \
--www-port=8789 \
--server-user $USER

# keep it alive
sleep 3600
