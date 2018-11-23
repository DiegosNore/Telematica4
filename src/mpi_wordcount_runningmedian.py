

"""
Word Count (WC) and Running Mean (RM) calculations.


Using MPI, meta-data from the root process is iteratively generated
and sent to all other processes.  The meta-data includes
-- filenames
-- location in bytes for where to start reading the file
-- filesize

For WC:
Using that meta-data, each process can do a word count, which is then gathered
to MPI rank 0 to MasterCounter.  Then more meta-data and more word counts are done
and MasterCounter is further updated. This process is repeated
until all the files have been read.  

For RM:
Rank 0 loads a data chunk, computes the running median.  In parallel, Rank 1 gets the next
data chunk, but takes in the last N = nTail lines from rank 0 to make the running median a bit
more consistent.  The running mean is written to file each time a chunk is completed.

"""

import sys
import os
import glob
import collections
from operator import itemgetter
from mpi4py import MPI

from partitionMetaData import partitionMetaData
from fileClass import fileClass
from wc import wc
from runMed import runMed

comm = MPI.COMM_WORLD
rank = comm.Get_rank()
nprocs = comm.Get_size()

input_dir = sys.argv[1]
output_dir = sys.argv[2]

### Reading in sys.argv and test to ensure vaildity
if rank == 0:
	if not os.path.exists(input_dir):
		sys.exit("Input directory:  " + input_dir + "  does not exist!")
	
	if not os.path.exists(output_dir):
		print "Output directory:  " + output_dir + "  does not exist, creating new directory!"
		os.makedirs(output_dir)									

WC_or_RM = sys.argv[3] 		## Used to  merge codes
if rank == 0:				
	if WC_or_RM == "wc":	
		fWordCount = open(output_dir + 'wc_result.txt', 'w')
	elif WC_or_RM == "rm":
		fRunMed = open(output_dir + 'med_result.txt', 'w')
	else:
		sys.exit("Invalid third argument sys.argv" +  WC_or_RM  + " !  please use 'wc' or 'rm' ")
			

input_files = [os.path.basename(x) for x in glob.glob(input_dir + '*.txt')]

files_loc = fileClass()
MasterCounter = collections.Counter()

maxReadSize = 10*1024*1024
runningFileSize = 0.0
fCount = 0
Nfiles = len(input_files)
chunk = 1
currentFileSize = 0.0
AddedFiles = False			
finalRank = 0
FirstIter = True	## Used in RM to determine whether to send the tail of size nTail
nTail = 100			## of rank i to rank i - 1

####################################  Begin of meta-data send/recv common to both WC and RM	

while fCount < Nfiles:					# rank0 does a quick, low-memory retrieval of
	if rank == 0:        				# meta-data.  This is iterative, only a single 
		for iRank in range(0, nprocs):	# rank can do this.  Meta-data is sent
										# to other ranks so they can load the right data
			AddedFiles = False			
			filenames_tmp, byteStart_tmp, filesize_tmp, fCount, chunk, AddedFiles = \
			partitionMetaData(maxReadSize, input_dir, input_files, fCount, chunk, AddedFiles)
			#### Sending the meta-data 
			if iRank > 0:
				comm.send(filenames_tmp, dest = iRank, tag = 100*(iRank + 1))
				comm.send(byteStart_tmp, dest = iRank, tag = 101*(iRank + 1))
				comm.send(filesize_tmp, dest = iRank, tag = 102*(iRank + 1))

			else:
				files_loc.filenames.extend(filenames_tmp)
				files_loc.byteStart.extend(byteStart_tmp)
				files_loc.filesize.extend(filesize_tmp)		
			if fCount >= Nfiles:
				break
			
		if AddedFiles:          ## finalRank,AddFiles are to avoid stalling during a recv
			finalRank = iRank
		else:
			finalRank = iRank - 1

	finalRank = comm.bcast(finalRank, root=0)
	AddedFiles = comm.bcast(AddedFiles, root=0)
		
	if AddedFiles:					#### Receiving the meta-data
		if rank <= finalRank and rank > 0:
			files_loc.filenames.extend(comm.recv(source = 0, tag = 100*(rank + 1)))
			files_loc.byteStart.extend(comm.recv(source = 0, tag = 101*(rank + 1)))
			files_loc.filesize.extend(comm.recv(source = 0, tag = 102*(rank + 1)))

	else:
		if rank < finalRank and rank > 0:
			files_loc.filenames.extend(comm.recv(source = 0, tag = 100*(rank + 1)))
			files_loc.byteStart.extend(comm.recv(source = 0, tag = 101*(rank + 1)))
			files_loc.filesize.extend(comm.recv(source = 0, tag = 102*(rank + 1)))
			
	### Chose to keep printing these, good way to visualize what is being done		
	print " files_loc.filenames  from rank = ", rank , "    ", files_loc.filenames
	print " files_loc.byteStart  from rank = ", rank , "    ", files_loc.byteStart

####################################  End of meta-data send/recv common to both WC and RM
	
	files_loc.loadLines(input_dir, maxReadSize)   ### loads lines based on meta-data
	
	if WC_or_RM == "rm":			### loads words/line if running median
		files_loc.loadWordsPerLine()
		wplTail = files_loc.wordsPerLine[-nTail:]	## extend rank i by tail of rank i-1
			
		if rank < nprocs -1:		## Sending of tail done irrespective of step
			comm.send(wplTail, dest = rank + 1, tag = 103*(rank + 1))
		comm.barrier()
		if rank > 0:
			files_loc.wordsPerLine = comm.recv(source=rank - 1, tag = 103*(rank)) + files_loc.wordsPerLine
		comm.barrier()
		
		## Extra recv if not first step, last rank sends rank0 its tail at end of loop
		if FirstIter is False and rank == 0:
			files_loc.wordsPerLine.extend(comm.recv(source=nprocs-1, tag=999))

		if rank == 0 and FirstIter:			##### the loaded data, including tail of
									##### previous rank, but does not re-write tail
			Runmed = runMed(files_loc.wordsPerLine, 0)
		else:
			Runmed = runMed(files_loc.wordsPerLine, nTail)					
		comm.Barrier()								
		RunmedFull = comm.gather(Runmed, root=0)

		if rank == 0:
			for i in range(0, len(RunmedFull)):
				for j in range(0, len(RunmedFull[i])):
					print >> fRunMed, float(RunmedFull[i][j])	### RM writes at each step

		RunmedFull = []
		Runmed = []
		files_loc.wordsPerLine = []
		comm.Barrier()


	if WC_or_RM == "wc":						#####################################
		Counter_loc = wc(files_loc.lines)		#### This does the word counting for 
		comm.Barrier()							#### the loaded data
		CounterIter = comm.gather(Counter_loc, root=0)
		if rank == 0:
			for iRank in range(0, nprocs):
				MasterCounter += CounterIter[iRank]
		comm.Barrier()
    
	FirstIter = False
	if WC_or_RM == "rm":
		if rank == nprocs -1:
			comm.send(files_loc.wordsPerLine[-nTail:], dest = 0, tag = 999)
		
	files_loc.filenames = []	## Clear classes for both WC and RM, otherwise
	files_loc.byteStart = []	## class would grow during the next step
	files_loc.lines = []
	files_loc.filesize = []
	
if rank == 0:

	if WC_or_RM == "wc":					# WC writes only at the very end of all steps
		keys = sorted(MasterCounter)
		for key in keys:
			###Below gives exact tab in between, above adds a space before the tab
			print >> fWordCount, '\t'.join([key, str(MasterCounter[key])	])
		print "DONE WITH WORD COUNT!"
		fWordCount.close()

	elif WC_or_RM == "rm":
		print "DONE WITH RUNNING MEDIAN!"
		fRunMed.close()	

comm.Abort()		#sys.exit() wasn't working, nor comm.Disconnect(), this works
					# but MPI gives a warning message
