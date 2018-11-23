### This is the class that stores the meta-data, and uses the meta-data to load
### the actual data into the class using the 2 functions below

###  If, for example, rank0 sees a fileszie larger than 10MB, it only read the first 10MB
###  rank1, starts 10MB into the file 

import string
import os

class fileClass:
    def __init__(self):

        ##File meta-data
        self.filenames = []
        self.byteStart = []
        self.filesize = []
		
        ## Use meta-data to later load lines and wordsPerLine
        self.lines = []
        self.wordsPerLine = []

    def loadLines(self, dir, maxReadSize):         
        counter = 0
        for file in self.filenames:   # for each filename, start at byteStart, and
        	with open(dir + file, 'r') as lf:	#read 10MB or until end
        		lf.seek(self.byteStart[counter])
        		lines = lf.read(maxReadSize).split('\n')
        		if self.byteStart[counter] + maxReadSize > self.filesize[counter]:
        			self.lines.extend(lines[0:-1])	#fixes bug:  w/o this, will add
        		else:								# blank line at end of file
        			self.lines.extend(lines)
        		counter +=1
            	
    def loadWordsPerLine(self):    #load words/line (used for running median)
		trimmer = string.maketrans(string.punctuation, ' ' * len(string.punctuation))
		for line in self.lines:
			line = line.translate(trimmer)
			self.wordsPerLine.append( len(line.split() ))
