Updated on Nov 27th, 2024. Incorporated Owen Wilkins' (DAC) rstudio server set up tutorial.

# Set up Rstudio server on HPC.

-   This tutorial has two sections. One is about setting up the server on Polaris. The other one is about setting up the server on discovery.\*

The advantage of using Polaris is that you directly set up the server on Polaris, no need to apply for a computer node. Theoretically, it should last forever, unless Polaris crashes. However, when many people are using Polaris, it can crash often. The inconvenient thing is that you have to separately set up the R environment on Polaris. You can use the R already installed on Polaris or conda R.

Alternatively, you can set up Rstudio server on Discovery. On Discovery, you will need to apply for a compute with specified memory, and the maximum running time of a node is 30 days. Thus you will need to set up your server every 30 days, but the advantage of using discovery is that this give you more control of the node. The compute node is not affected by other users, while on Polaris there are times then the system is overloaded with many users. Another advantage of using Discovery is that, the R used the server will be the exact same one that you use when running jobs on Discovery.

## Section 1: Set up RStudio server on Polaris.

You can set up the server with R installed on Polaris or use the R installed by `conda`.

### Set up RStudio server on Polaris with the R installed on Polaris.

-   Pull down the Singularity image.

Note: you only need to do this once. In the first time you set up rstudio server, you run the following command on Polaris to get rstudio.simg. Then you can keep it in the home directory and skip this step later on.

```         
singularity pull --name rstudio.simg docker://rocker/tidyverse:latest
```

-   Run singlarity to set up rstudio server. Do the following on Polaris:

```         
# create a screen
screen

# Create the local filesystem
TMPDIR=$HOME/rstudio-tmp
mkdir -p $TMPDIR/tmp/rstudio-server
mkdir -p $TMPDIR/var/{lib,run}
uuidgen > $TMPDIR/tmp/rstudio-server/secure-cookie-key
chmod 600 $TMPDIR/tmp/rstudio-server/secure-cookie-key

# Run the container
PASSWORD='aaa' singularity exec \
--bind $TMPDIR/var/lib:/var/lib/rstudio-server \
--bind $TMPDIR/var/run:/var/run/rstudio-server \
--bind $TMPDIR/tmp:/tmp \
--bind /dartfs/rc/lab/S/Szhao \
rstudio.simg \
rserver \
--auth-none=0 \
--auth-pam-helper-path=pam-helper \
--www-address=127.0.0.1 \
--www-port=8789 \
--server-user $USER

# detach from the screen
# press ctrl + A + D
```

Note if this port is being used, change the port number. and of course you need to change the port number in the following commands too.

-   On local computer/laptop

Create a SSH tunnel by opening the Terminal and run the following:

```         
# Create the SSH tunnel
ssh -N -f -L 8789:localhost:8789 d92495j@polaris.dartmouth.edu
```

Be sure to change the username in the above command when running. Then open the url: `http://localhost:8789` on your browser and log in using your username and the password is aaa.

Occasionally, you may get the the error message "port already in use". To solve this error, you can kill the process using the port by `lsof -ti:8789 | xargs kill -9`. Please change the port number accordingly in this command.

### Set up RStudio server on Polaris using Conda environment

There are two methods to do this. If Method 1 does not work for you, please try Method 2.

-   **Method 1**:

1.  open up a terminal window, log in Polaris

make a directory within the home directory

```         
$ mkdir singularity_imgs
```

print working diretory

```         
$ pwd 
```

```         
/dartfs-hpc/rc/home/k/f******/singularity_images
```

2.  open another terminal window, log in to **Discovery**

```         
ssh f*****@discovery.hpcc.dartmouth.edu
```

If prompt asks **‘Are you sure you want to continue connecting (yes/no/[fingerprint])?**

Type

```         
> yes
```

Copy the rstudio.simg file from scratch space to your newly made directory

```         
$ cp /scratch/rstudio/rstudio.simg /dartfs-hpc/rc/home/k/f******/singularity_images
```

3.  Go back to the **Polaris** terminal window

```         
singularity exec \
--bind /dartfs-hpc/rc/home/k/f******/.conda/envs/r_env \
--bind $(pwd)  /dartfs-hpc/rc/home/k/f******/singularity_images/rstudio.simg rserver \
--www-address=127.0.0.1 \
--www-port **** \
--rsession-which-r=/dartfs-hpc/rc/home/k/f******/.conda/envs/r_env/bin/R \
--rsession-ld-library-path=/dartfs-hpc/rc/home/k/f******/.conda/envs/r_env/lib \
--server-user $USER
```

Be sure to change the working directory paths to your own and change the port number!

4.  open the third terminal window

```         
 % ssh -N -f -L ****:localhost:**** f******@polaris.dartmouth.edu
```

then type your password

5.  open up a browser

```         
localhost:****
```

You are now able to use your Rstudio server within a conda environment.

6.  On your RStudio Server console

```         
.libPaths("/dartfs-hpc/rc/home/k/f******/.conda/envs/r_env/lib")
```

then type this to check and see you’re connected to the correct path.

```         
.libPaths()
```

**Remember, try to install packages using terminal**

```         
$ conda activate ‘your env’
```

**Try not to install packages through Rstudio server, Rstudio server is a bit strange when it comes to installing packages.**

-   **Method 2:**

```         
1. Create/pull down singularity image as above (SKIP if already done)

# create a screen
screen

# Pull down the Singularity image
# Note: you only need to do this once. In the first time you set up rstudio server, you run the following command to get rstudio.simg. Then you can keep it in the home directory and skip this step later on.
singularity pull --name rstudio.simg docker://rocker/tidyverse:latest

2. Have the conda environment you want to use with RStudio server set up (confirm R is present in conda environment)

conda create -n env
conda activate env
# OR use directory path
conda create -p /dartfs/rc/lab/S/Szhao/user/conda/base
conda activate /dartfs/rc/lab/S/Szhao/user/conda/base

# install R if not already in environment 
conda install -c r r-essentials

3. Open another terminal and log into Polaris

# create a screen
screen

# Modify code and run
# Modifications: change `user` to user's foldername, add port number, `$USER` is dartmouth ID 

TMPDIR=/dartfs/rc/lab/S/Szhao/user/rstudio-tmp
PASSWORD='lab' singularity exec \
--bind /dartfs/rc/lab/S/Szhao/user/conda/base \
--bind $TMPDIR/var/lib:/var/lib/rstudio-server \
--bind $TMPDIR/var/run:/var/run/rstudio-server \
--bind $TMPDIR/tmp:/tmp \
--bind /dartfs/rc/lab/S/Szhao \
rstudio.simg \
rserver \
--auth-none=0 \
--auth-pam-helper-path=pam-helper \
--www-address=127.0.0.1 \
--www-port=#### \
--rsession-which-r=/dartfs/rc/lab/S/Szhao/user/conda/base/bin/R \
--rsession-ld-library-path=/dartfs/rc/lab/S/Szhao/user/conda/base/R \
--server-user $USER

# Note: Confirm the path to the location of your R and R libraries are correct
```

If no error pops up, please refer to Steps 4 and 5 in Method 1 to sign into RStudio Server.

## Section 2: Set up RStudio server on Discovery.

-   Obtain `rstudio_server.sh` from the lab-wiki repo.

    You can modify `rstudio_server.sh` to specify the number of cores, memory, run time, *etc* that you need for the rstudio server.

    Also download singularity like described in the above section "Set up RStudio server on Polaris with the R installed on Polaris." . Note you only need to do this step once.

    ```         
    singularity pull --name rstudio.simg docker://rocker/tidyverse:latest
    ```

-   On Discovery run the following:

```         
sbatch rstudio_server.sh
```

This step will apply a node for you and set up rstudio server. The R you are using and its library will be the same as in the environment you run this `sbatch` command.

You can modify memory, run time, port number, password, the location of your singalarity image, *etc* in `rstudio_server.sh` .

-   Then use `squeue -u $USER` on discovery to check for node name. I usually do this in morning, when the node is easy to get. For example, you may get the following output

```         
   JOBID PARTITION     NAME     USER ST       TIME  NODES NODELIST(REASON)
           2982981  standard rstudio_  f**** PD       0:00      1 s18
```

The node you applied for this job is named "s18".

-   Then on your local computer

    create ssh tunnel by running

    ```         
    ssh -N -f -L 8789:s18:8789 f****@discovery.dartmouth.edu
    ```

    here s18 is the node's name you applied on Discovery. Remember to change it the actual node name, as it will change each time you set up the server.

-   On your local computer, open your browser with url: `http://localhost:8789` and log in using your username and the password is aaa.

**Remember, cancel your rstudio job after you are done!**  
Don't waste resources! Use `squeue -u $USER` to see the job ID with name rstudio server. Then cancel the job using `scancel xxx`, where xxx is the job ID.  

**Remember, try to install packages using terminal, not from rstudio server.**
