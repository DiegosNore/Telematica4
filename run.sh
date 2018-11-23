
#### input parameters, number of MPI processes, input + output directories
NUM_MPI_PROCS=3
INPUT_DIR=wc_input_larger/
OUTPUT_DIR=wc_output/

### wc_input/ is a very small test, using two files similar to the cc-example 
##  wc_input_larger/ has a test with larger files

###############################
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!
## In case "pip install mpi4py" does not work, please consult the README file
## !!!!!!!!!!!!!!!!!!!!!!!!!!!!
###############################
pip install mpi4py
rm -f src/*.pyc

mpiexec -n $NUM_MPI_PROCS python src/mpi_wordcount_runningmedian.py $INPUT_DIR $OUTPUT_DIR wc

mpiexec -n $NUM_MPI_PROCS python src/mpi_wordcount_runningmedian.py $INPUT_DIR $OUTPUT_DIR rm
