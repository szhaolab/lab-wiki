**Job Dependency Chain**

In the notebook `Job Dependency Chain.ipynb`, I provided an example.
Sometimes, on an HPC system, we can see other users’ jobs in the squeue output with the state Dependency — this example makes full use of that feature.

In this workflow, the process follows the sequence:

split(1) → wilcoxon(1–200)  
       ↓  
split(2) → wilcoxon(201–400)  
       ↓  
split(3) → ...

Through this **Job Dependency Chain**, we can ensure that each loop depends on the previous one being completely finished before the next starts.
In this context, it means that the next round of split jobs will only begin after all 200 Wilcoxon test tasks from the previous round have fully completed.

**split step**  
Splits the large single-cell dataset into smaller subsets to make parallel computation feasible.  

**wilcoxon step**  
Performs differential expression (DE) analysis using the Wilcoxon test on each subset.


The script `huang_master.sh` serves as the master controller for submitting a sequence of batch jobs to the HPC cluster.
It implements a Job Dependency Chain, ensuring that each stage begins only after the previous stage (or batch of array jobs) has fully completed.

To submit those tasks to the HPC cluster, simply run `bash huang_master.sh` on the login node.
