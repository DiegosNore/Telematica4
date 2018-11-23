
"""
This gets the meta-data containing filenames, location in MB on where to start
and the filesize

This is embedded in an iterative loop over process rank to decide which files
and or chunks of files to send to each process

Initial plan was to include the MPI send/recv here.
Kept this part wrapped to make more modular/easier to read
"""

import os
from mpi4py import MPI

def partitionMetaData(maxReadSize, input_dir, input_files, fCount_init, chunk, AddedFiles):
	
	runningFileSize = 0.0
	fCount = fCount_init
	Nfiles = len(input_files)

	filesnames_tmp = []
	byteStart_tmp = []
	filesize_tmp = []
	
	while runningFileSize < maxReadSize:
		currentFileSize = os.path.getsize(input_dir + input_files[fCount])
		
		if  chunk*maxReadSize < currentFileSize:		### starts from chunk*maxReadSize and reads next
			filesnames_tmp.append(input_files[fCount])	### 10 MB for large files
			byteStart_tmp.append((chunk - 1)*maxReadSize)
			filesize_tmp.append(currentFileSize)
			
			chunk += 1
			AddedFiles = True
			
			if chunk*maxReadSize > currentFileSize:  # dump rest of file here if there is < 10MB remaining
				filesnames_tmp.append(input_files[fCount])
				byteStart_tmp.append((chunk -1)*maxReadSize)
				filesize_tmp.append(currentFileSize)
	
				fCount += 1
				AddedFiles = True
				if fCount >= Nfiles:
					break
				chunk = 1
			break
		else:
			filesnames_tmp.append(input_files[fCount])	## File is < 10 MB in size, add whole file
			byteStart_tmp.append((chunk-1)*maxReadSize)
			filesize_tmp.append(currentFileSize)
			fCount += 1
			runningFileSize += currentFileSize
			Addedfiles = True
			if fCount >= Nfiles:
				break
									
	return filesnames_tmp, byteStart_tmp, filesize_tmp, fCount, chunk, AddedFiles
