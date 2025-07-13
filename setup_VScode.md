# Connect to HPC in VScode

## Step 1: Request resources for an interactive job
You can refer to the "Interactive jobs" section at:
https://services.dartmouth.edu/TDClient/1806/Portal/KB/ArticleDet?ID=132625
Here is an example:
[f0070pp@discovery-01 ~]$ srun --nodes=2 --ntasks-per-node=4 --mem-per-cpu=1GB --cpus-per-task=1 --pty /bin/bash
[f0070pp@s28 ~]$

## Step2: Activate conda environment
Make sure the environment includes jupyter-notebook; otherwise, you need to install it using: conda install -y notebook

## Step 3: Launch Jupyter Notebook server
- Get host IP for Jupyter
HOST_IP=`/sbin/ip route get 8.8.8.8 | awk '{print $7;exit}'`
echo $HOST_IP

- Launch Jupyter Notebook server
jupyter-notebook --no-browser --ip=$HOST_IP --port=15021

Then you will get a link like http://10.248.140.169:15021/tree?token=786af28426ac188f4e39f482698357aa6b011b85d60d1392
Copy it.  

<img width="980" height="209" alt="image" src="https://github.com/user-attachments/assets/5721306c-426d-452b-9e47-12cc0c9caf0f" />

## Step 4: Open VS Code and connect to the compute node 
Click the button “><” at the bottom-left corner and select “Open a Remote Window”.  

<img width="190" height="107" alt="image" src="https://github.com/user-attachments/assets/364679b4-12bd-448b-bfe0-065c74f2ebdf" />

Click “Connect to Host”
Connect to SSH Host “discovery8.dartmouth.edu”
Open a .ipynb file (Jupyter Notebook)  

<img width="700" height="30" alt="image" src="https://github.com/user-attachments/assets/950cc6b1-77bd-49e3-a482-6508f3d3072b" />

Then click “Select Kernel” at the top right.
Click “Select Another Kernel…”
<img width="700" height="60" alt="image" src="https://github.com/user-attachments/assets/847035c9-a11e-4cab-ace5-0104345145df" />

Click “Existing Jupyter Server…”
<img width="700" height="180" alt="image" src="https://github.com/user-attachments/assets/aa8626a5-7902-4d18-94d1-200142ab53c7" />

Paste the link you copied (http://10.248.140.169:15021/tree?token=786af28426ac188f4e39f482698357aa6b011b85d60d1392) earlier into here.

