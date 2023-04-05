## Interactive-Mode-HPC-tutorial
Interactive Mode (HPC) tutorial on Bash

## 1. Sign in Discovery7 account
```
$ ssh -Y *******@discovery7.dartmouth.edu
```

## srun manual
```
$ man srun
```

## 2. Set working directory
To set your DartFS home directory as working directory:
```
$ cd 
```
or specify file path 
```
$ cd /filepath
```
It may be helpful to create a symbolic link in your home directory to access the lab share
```
$ cd 
$ ln -s /dartfs/rc/lab/S/Szhao Zhao-labshare/
```

## 3. After configuring files, run the interactive mode
```
$ srun --pty /bin/bash
```
Jobs submitted with srun –-pty /bin/bash will be assigned the cluster default values of 1 CPU and 1024MB of memory. The account must also be specified; the job will not run otherwise. If additional resources are required, they can be requested as options to the srun command. The following example job is assigned 2 nodes with 2 CPUS and 4GB of memory each:
```
srun --nodes=2 --ntasks-per-node=4 --mem-per-cpu=1GB --cpus-per-task=1 --pty /bin/bash
```
If the error is
```
Package bash-completion was not found in the pkg-config search path.
Perhaps you should add the directory containing `bash-completion.pc'
to the PKG_CONFIG_PATH environment variable
No package 'bash-completion' found
bash: /yum: No such file or directory
```
install the package
```
$ conda install -c conda-forge bash-completion
```
Proceed ([y]/n)?
```
y
```

## 4. Interactive Mode
```
$ srun --pty /bin/bash
```
if error appears again
```
srun: Cancelled pending job step with signal 2
srun: error: Unable to create step for job 1257531: Job/step already completing or completed
```
add your file at the end
```
$ srun --pty /bin/bash snakemake.sbatch
```
## Checking job priorities
```
$ squeue
```
## Checking all available partitions
```
$ sinfo
```
## Checking the hostname
```
$ hostname
discovery7.hpcc.dartmouth.edu

```
## SLURM
If running on the cluster, please edit the cluster.json config file to match your cluster configuration. Once complete, submit the given sbatch file to the cluster.
```
$ sbatch snakemake.sbatch
```
