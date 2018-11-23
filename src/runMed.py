
"""
Computes the running median for a set of integers

In many cases, doing an exact line-by-line through the whole data in
not feasible, so rank i gets the tail of rank (i - 1), computes the 
running median for the tail to get a better starting sequence for what
rank i is supposed to compute.  
"""

from heapq import heappush, heappushpop
 ## smedian is, with minor adjustments, from: http://programmingpraxis.com/2012/05/29/streaming-median/
 ## This is a  quick, heap-based algorithm and the use of a generator bypasses any 'if' statements
def smedian():
    def gen():
        left, right = [], [(yield)]
        while True:
            heappush(left,  -heappushpop(right, (yield right[0])))
            heappush(right, -heappushpop(left, -(yield ((right[0] - left[0])/2.0))))
    g = gen()
    next(g)
    return g
 
def runMed(wordsPerLine, nTail):			#### Inputs a list of integers and gets the running
	runMed = []						#### median using smedian
	meds = smedian()				#### 
	for n in wordsPerLine:
		runMed.append(meds.send(n))
	return runMed[nTail:]
		
