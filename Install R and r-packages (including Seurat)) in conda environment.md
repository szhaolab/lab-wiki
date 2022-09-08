Create Install R and r-packages (including Seurat)) in conda environment
## Install R and r-packages in conda environment 
  ### 1.Conda 
  Conda is a tool to manage environments and packages. 
  
   If you haven't used conda before or `conda` command doesn't work in your HPC, add the code below into your .bashrc file at the root of your DartFS home. 
  
   ``` 
  source /optnfs/common/miniconda3/etc/profile.d/conda.sh 
  ``` 
  
   Then reopen your hpc or run `$source .bashrc` to reload .bashrc file. 
  
   ### 2.Create R environment using conda 
  Use line below to create your environment. 
  
   ``` 
  $conda create -name YOUR_ENV_NAME 
  ``` 
  
   Your environment created by conda lives in **_.conda/envs** folder. 
  
   ### 3.Activate your environment 
  
   ``` 
  conda activate YOUR_ENV_NAME 
  ``` 
  
   ### 4.Install R and some packages 
  
   ``` 
  conda install r r-essentials --channel conda-forge 
  ``` 
  
   If you want to install new packages (but not for Seurat, it may cause compatibility problem): 
  
   ``` 
  $R 
  install.packages("PACKAGE_NAME") 
  q() # to exit R 
  ``` 
  
   Remember to activate environment if you have deactivated it. 
  
   ### 5.Install Seurat 
  Download  seurat.yml (provided by Nic Sugiarto) from lab-wiki. Drag it into your HPC.
```
$conda undate -n YOUR_ENV --file seurat.yml
```
After installation,

```
$conda activate YOUR_ENV
$R
$install.packages("Seurat")
$q()
```

### 6.Set the path in Rstudio to get access to your environment
```
.libPaths("/dartfs-hpc/rc/home/*/f******/.conda/envs/YOUR_ENV/lib")
