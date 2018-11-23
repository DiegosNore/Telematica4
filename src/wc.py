
"""
Routine to do the word count
Inputs a list of lines in some file(s) and
stores key,values in a Counter for easy reductions
"""

import string
import collections

def wc(inlines):
	OutCounter = collections.Counter()	
	trimmer = string.maketrans(string.punctuation, ' ' * len(string.punctuation))
    
	for line in inlines:
		line = line.translate(trimmer) # remove punctuation
		for word in line.split():
			word = word.lower()			# make lower-case
			OutCounter[word] +=1
	return OutCounter
