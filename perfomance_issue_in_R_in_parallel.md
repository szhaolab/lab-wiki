# Performance issue in parallelized R code
## Issue
The parallelized code runs faster when the number of rows in the data is 1,000. Why parallelized code does not run faster than the nonparallelized code when the number of rows increase from 1,000 to 10,000?

example code:
```
rownum <- 10000

# nonparallel ####
system.time({
  geno.i.new <- matrix(, nrow = rownum, ncol = 413)
  for (k in 1:rownum) {
    geno.i.new[k,] <- sample(0:2, size = 413, replace = TRUE)
  }
  pheno <- rnorm(rownum)
  for(part in 1:10) {
    for (k in 1:ncol(geno.i.new)) {
      a <- summary(glm(pheno ~ snp,family=gaussian,
                       data=data.frame("pheno" = pheno, "snp" = geno.i.new[,k])))
    }
  }
})

# user  system elapsed (with 10000 rows) (with ntask-per-node = 1, cpu-per-task = 10)
# 57.895 216.665  27.885


# parallel ####
library(future) # availableCores
library(doParallel)
library(foreach)

ncore_avail <- max(1, availableCores())
print(ncore_avail)
cl <- makeCluster(ncore_avail)
registerDoParallel(cl)

clusterEvalQ(cl, .libPaths(c("/dartfs-hpc/rc/home/4/f006ys4/R/x86_64-pc-linux-gnu-library/4.3",
                             "/optnfs/el8/Rlibs/4.3","/dartfs-hpc/admin/opt/el8/R/4.3.3/lib/R/library")))

system.time({
  geno.i.new <- matrix(, nrow = rownum, ncol = 413)
  for (k in 1:rownum) {
    geno.i.new[k,] <- sample(0:2, size = 413, replace = TRUE)
  }
  pheno <- rnorm(rownum)
  res <- foreach(part = 1:10)  %dopar% { # For hpc
    for (k in 1:ncol(geno.i.new)) {
      a <- summary(glm(pheno ~ snp,family=gaussian,
                     data=data.frame("pheno" = pheno, "snp" = geno.i.new[,k])))
    }
  }
})

# user  system elapsed (with 10000 rows) (with ntask-per-node = 1, cpu-per-task = 10)
# 0.363   0.049  33.954
```

## Useful commands for this issue
`top -u $USER`: check the active memory and CPU usage; press `1` on the keyboard to see detailed usage for individual CPU cores (will not mark with CPU cores in use though). 

`export OMP_NUM_THREADS=1`: overwrite the current OMP_NUM_THREADS to 1. This will force R to use single threaded BLAS. Set this before running parallelized code.

`unset OMP_NUM_THREADS`: reset the OMP_NUM_THREADS to default (i.e. the number of available cores).

`echo $OMP_NUM_THREADS`: print the current value stored in OMP_NUM_THREADS. If nothing is printed except for a blank line, then it is in the default setting.

## Detailed explanation
By default, on Dartmouth’s HPC, R functions like `glm` automatically utilize multiple cores assigned to the session (configured with --cpus-per-task). This is because R uses a multi-threaded implementation of BLAS, which enables it to perform calculations across multiple cores automatically. The environment variable OMP_NUM_THREADS is set to match the number of available cores by default.

When running parallelized code, setting OMP_NUM_THREADS=1 forces R to use a single core per thread. This approach minimizes overhead (the extra computational time and resources required to manage parallel tasks) and reduces memory pressure. If you don’t set OMP_NUM_THREADS=1, each `glm` function may compete for multiple cores, leading to higher-than-expected CPU usage (often greater than 100% in %CPU) and slowing down the overall program.

## Orignal reply from RC
```
(Reply from Simon Stone from Research Data Services in the Dartmouth Libraries:)

When parallelizing workloads, we always have to keep in mind that every additional thread or process comes at a cost: The system needs extra time to create a thread or process (let’s call them “workers”), allocate memory to it, copy any required data (in case of a process without shared-memory access), and to wind down a thread or process once it completes. So if our workload consists of many very small tasks, it might not be a good strategy to assign each tiny task to a new worker, because the overhead involved in that might be larger than the actual task itself. This is the case here: Each glm fit is a relatively small task, so there is no benefit (or even a net negative) to parallelize that. However, we have to do many of these tasks (one per column), so there is a lot to gain to parallelize the for loop, but only when we keep the actual glm fit single-threaded (because we otherwise incur the same overhead as before). So the optimal strategy would be to use %dopar% in the for loop, but set OMP_NUM_THREADS=1.


I suspect that you see different behavior in different environments because the underlying BLAS libraries might be built without multithreading support. In that case the glm function always runs single-threaded, and you don’t run the risk of accidentally getting all the overhead from the glm function trying to run in parallel.


The reason the array size plays a role is because BLAS makes some internal decisions what size of a task actually triggers leveraging multiple threads. That way small arrays are processed single-threaded to avoid the potentially outsized overhead.


To see that, reduce the array size to 1000 rows and run the program with OMP_NUM_THREADS set to 10. Then inspect the output of the system.time call. Here is what I got for the non-parallel function:


user system elapsed

8.598 0.037 8.733


The user time (CPU time the program occupied) plus the system time (time the CPU spent on system-related things) roughly adds up to the elapsed wallclock time. That is what you would expect to see in a single-threaded computation. So BLAS decided that splitting the glm fit into parallel tasks was not worth the overhead. Now change the array size back to 10000 and run the non-parallel function again:


user system elapsed

316.968 0.729 35.713


Now we see that the user time is a multiple of the actual wallclock time, which is only possible if the program occupied multiple CPU cores in parallel. So, the array was big enough for BLAS to decide to go multithreaded!


FYI: When looking at the user time of the %dopar% loop, things get a little confusing. System.time only reports the user time of the current process. %dopar% runs the workload in parallel in separate processes, so the computation time does not show up correctly here.
```
