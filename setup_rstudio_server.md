# Set up RStudio server  

This tutorial will help you to set up rstudio server. With rstudio server, you will use the R installed on the server and have access to all the files on the server. (I recommended you use `conda` to manage your environment and install your own R with `conda`).

* On **polaris**, do the following.

```
# create a screen
screen

# Pull down the Singularity image
# Note: you only need to do this once. In the first time you set up rstudio server, you run the following command to get rstudio.simg. Then you can keep it in the home directory and skip this step later on.
singularity pull --name rstudio.simg docker://rocker/tidyverse:latest

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

* On my local computer/laptop, do the following: 

  be sure to change user ID and port number accordingly.

```
# Create the SSH tunnel
ssh -N -f -L 8789:localhost:8789 d92495j@polaris.dartmouth.edu

http://localhost:8789
# log in as d92495j and password is aaa
```

# Set up RStudio server using Conda environment
## 1. open up a terminal window, log in **Polaris**

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

## 2. open another terminal window, log in **Discovery7**
```
ssh f*****@discovery7.hpcc.dartmouth.edu
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

## 3. Go back to the **Polaris** terminal window
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

## 4. open the third terminal window
```
 % ssh -N -f -L ****:localhost:**** f******@polaris.dartmouth.edu
```
then type your password

## 5. open up a browser
```
localhost:****
```
You are now able to use your Rstudio server within a conda environment.
 
## 6. On your RStudio Server console
```
.libPaths("/dartfs-hpc/rc/home/k/f******/.conda/envs/r_env/lib")
```
then type this to check and see you’re connected to the correct path.
```
.libPaths()
```
* **Remember, try to install packages using terminal**
```
$ conda activate ‘your env’
```
**Try not to install through Rstudio server, Rstudio server is a bit strange when it comes to installing packages.**
