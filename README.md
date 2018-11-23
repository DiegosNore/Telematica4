#Python-WC-RM

This contains MPI-parallelized Python routines to compute word count (WC) + running median (RM) line size for a list of text files.

The key technical aspect is to partition meta-data related to the files to optimize memory usage, that is:
<br \>
** We don't want, for example, MPI process 1 to construct a Python Counter for the words in a 5KB file and have
to wait for MPI process 2 to do the same task with a 75MB size file. Moreover, we do not want each process to analyze, say, 10GB of data and have a bottleneck when gathering/reducing the distributed data.  We thus want each process to analyze data on the order of 10 MB at a time, which ensures (1) the branching of processes is worthwhile and (2) no memory bottlenecks are created.  The code is thus well suited for large-scale problems and optmizes the use of multiple cores**  

Using MPI, meta-data from the root process is iteratively generated
and sent to all other processes.  The meta-data contains:

> filenames <br \>
 location in bytes for where to start reading a file <br \>
 the filesize <br \>


For WC:
<br />
Using that meta-data, each process can do a word count, which is then gathered
to MPI rank 0 to MasterCounter.  Then more meta-data, more word counts are done
and MasterCounter is further updated. This process is repeated
until all the files have been read.  

For RM:
<br />
Rank 0 loads a data chunk, computes the running median.  In parallel, Rank 1 gets the next
data chunk, but takes in the last N = nTail lines from rank 0 to make the running median a bit
more consistent.  Thus, the process begins by having rank0 creates a list of integers
<br />
r0 = [k_0, …, k_n, k_{n+1}, … ,k_{n+nTail}]
<br />
and rank0 computes the running mean for that list, and saves it to file. Rank1 has the list
<br />
r1 = [k_{n+1}, … ,k_{n+nTail}] + [l_0, …, l_m, l_{m+1}, … ,l_{m+nTail}]
<br />
computes the running mean for that list using an existing heap-based method, but does not save the first nTail entries.  The first nTail
entries are only computed to get a small sample from previous data.  This allows for some consistency,
along with high scalibility.  A perfectly accurate running mean calculation is not scalable.  
<br />

When run.sh is executed, the WC portion will run first, then the RM part.  You’ll see output like this after each "iteration"(using 3 processes here):

 - files_loc.filenames  from rank =  0      ['aatest.txt', 'aatest1.txt', 'text1.txt']
 - files_loc.byteStart  from rank =  0      [0, 0, 0]
 - files_loc.filenames  from rank =  2      ['text1.txt', 'text1.txt']
 - files_loc.byteStart  from rank =  2      [20971520, 31457280]
 - files_loc.filenames  from rank =  1      ['text1.txt']
 - files_loc.byteStart  from rank =  1      [10485760]

An “iteration” is when all process each analyze up to 10MB of data, before each process get another 10MB, and so on.  Note that 

- .filenames is a list of filenames that rank n (=0,1,2) is currently processing
- .byteStart is the starting point, in bytes for which the data is being read.  

This means rank0 is reading ‘aatest.txt’,  ‘attest1.txt’ and ’text1.txt’.  ‘aatest.txt’ and ‘attest1.txt’ are small, so rank0 keeps adding more files.
‘text1.txt’ is more than 10MB, so rank0 only reads the first 10MB.

Rank 1 is also reading ‘text1.txt’ but starting at 10MB into the file, and reading the next 10MB.  

I kept the printing of this data in the production version, it helps the user to visualize the splitting when first testing.
#############################################
##A remark about dependencies:
The only dependency that needs to be installed is mpi4py.  This requires, for example, a version of Open-MPI, which can be installed on Mac using MacPorts `port install openmpi` or on Ubuntu `apt-get install openmpi-bin openmpi-doc libopenmpi-dev`.
<br/>
<br />
and one can compile via `mpicc mpi_hello_world.c -o mpi_hello_world` and running on, e.g 3 cores, using mpirun:  `mpirun -np 3 ./mpi_hello_world`.  If this basic test fails, the Python code will likely not run, and a manual installation of Open-MPI may need to be done.  Macs are more prone to MPI installation issues using port, straight-forward manual instructions can be found here for Mac: https://wiki.helsinki.fi/display/HUGG/Installing+Open+MPI+on+Mac+OS+X
<br/>
<br />
 The massive scalability obtained using MPI is worth the trouble, 
Using multiprocessing (e.g. http://pymotw.com/2/multiprocessing/mapreduce.html)
created large memory issues (e.g with 2 files ~ 1GB, it breaks and > 20GB or RAM is used)
and, from what I understand, can really only be used on a single node if one is running on a cluster

If the Python scripts do not run, a fairly safe bet is to use the Anaconda Python distribution.  This still needs, e.g, Open-MPI.  This is what I personally had installed prior to starting this challenge for another reason, and a simple “pip install mpi4py” worked like a charm.  For additional details on installing mpi4py, please consult: http://mpi4py.scipy.org/docs/usrman/install.html

