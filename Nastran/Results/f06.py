"""
======================================================================
http://opensource.org/licenses/BSD-2-Clause

Copyright (c) 2014, Benjamin E. Taylor
 All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:
 - Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
 - Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
======================================================================
"""
from itertools import ifilter
from StrEngL.Nastran.Results import Collections
from StrEngL.Nastran.Results import f06DataTables

class f06File():
    
    def __init__(self, filename):
        # instance variables
        self.filename = filename
        self.lines = open(filename,'r').readlines()
        self.pages = []
        #self._scanFile()
        
    #def __getattr__(self, name):
        # for list attribute calls
        #return getattr(self.lines, name)
    
    def __getitem__(self, key):
        # for slicing operations
        return self.lines[key]
            
    def getPage(self, pageNum):
        return self.pages[pageNum]
       
    def getTitles(self):
        titles = []
        for page in self.pages:
            if page.title != None and page.title not in titles:
                titles.append(page.title)
        return titles
        
    def getElementResults(self, title):
        """        
        Accepts: title = result title
        Returns: Dictionary tuple (header, results)
           header[ subcase ]  
           results[ subcase ][ elementID ]
        """
        import time
        assert title in self.getTitles()
        # initialize results collection object
        results = Collections.ElementResults()
        # initialize dictionaries to contain all data and headers 
        data = {}
        header = {}
        # grab parser function from f06DataTables module
        parserFunction = f06DataTables.parserTools[title]
        startTime = time.time()
        # filter the file for pages with indicated result title and 
        # iterate through each page storing the data
        for page in self._filterPages(title):
            # check if subcase has been found yet, if not add subcase key
            # to dictionaries
            subcase = page.subcase
            if subcase not in data: 
                data[subcase] = []
                header[subcase] = page.getHeader()
            # collect the page data
            data[subcase].extend(page.getDataList())
        for subcase in data:
            results[subcase] = parserFunction(data[subcase])
        print "%s : %s\nloaded in %.2f seconds" % \
              (self.filename, title, time.time() - startTime)
        return header, results
        
    def getHash(self):
        # generates a hash ID for future new file checks
        import hashlib
        fileObj = open(self.filename, 'rb')
        hashType = hashlib.sha256()
        hashType.update(fileObj.read(1000*128)) # approx. 1st 1000 lines
        fileObj.close()
        return hashType.digest()
        
    def scanHeaders(self):
        # scan the file and create f06Page objects
        import time
        startTime = time.time()
        print "scanning %s..." % self.filename
        # generate pages
        self._generatePages()
        for page in self.pages:
            page.scanHeader()
        print "took %.2f seconds" % (time.time() - startTime,)
        
    def openFile(self):
        self.lines = open(self.filename, 'r').readlines()
    
    def closeFile(self):
        self.lines = []
        
    def _generatePages(self):
        # generates f06Page objects, stores each instance in self.pages
        startLines = self._getStartLines()
        for i in range(len(startLines) - 1):
            startLine = startLines[i]
            endLine = startLines[i+1]
            self.pages.append(f06Page(i, startLine, endLine, self))
        
    def _getStartLines(self):
        # returns line numbers for all start lines in f06 file
        # ends with last line in file
        lineNumbers = range(len(self.lines))
        linesDict = dict(zip(self.lines, lineNumbers))
        startLines = []
        filterFunc = lambda line: line.startswith('1') 
        for line in ifilter(filterFunc, self):
            lineNum = linesDict[line]
            startLines.append(lineNum)
        startLines.append(len(self.lines))
        return startLines
                
    def _filterPages(self, title):
        # accepts 'title', returns pages of type 'title'
        filterFunc = lambda page: page.title==title
        return ifilter(filterFunc, self.pages)

        
class f06Page():
    # class variables
    READ_HEADER_LENGTH = 10 # number of lines read during header scan
    
    def __init__(self, number, start, end, f06FileObj):
        # instance variables
        self.number = number
        self.start = start
        self.end = end
        self.f06File = f06FileObj
        self.title = None
        self.subcase = None
       
    def __len__(self):
        # returns page length in bytes
        return int(self.end - self.start)
    
    def __iter__(self):
        # for iteration (may be redundant)
        return iter(self.getDataList())
        
    def __getitem__(self, key):
        # for slicing operations
        return self.getDataList()[key]
    
    def scanHeader(self):
        import re
        endLine = self.start + self.READ_HEADER_LENGTH
        scanLines = self.f06File[ self.start:endLine ]
        for line in scanLines:
            if 'SUBCASE ' in line: # found subcase
                # capture the subcase and add it to current page
                subcase = self._captureSubCase(line)
                self.subcase = subcase
            elif re.search(r'\w\s\w\s\w\s.*\(.*\)',line): # found title
                # parse and capture the title, then add it to current page
                self.title = self._parseTitle(line)
    
    def getDataList(self):
        # returns: list of data lines from f06 page (excluding header)
        return self.f06File[ self.getDataStartLine() : self.end ]

    def getHeader(self):
        # returns header of f06 page
        return self.f06File[ self.start : self.getDataStartLine() ]
        
    def getDataStartLine(self):
        # sets data start line for page
        return self.start + f06DataTables.startLines[self.title]
        
    def _parseTitle(self, line):
        # converts f06 title to key variable format,
        # '<ElementTYPE>_<resultsTYPE>'
        resTitle = [string.replace(' ','')
                    for string in line.strip().split('  ')]
        if any([')' in word for word in resTitle]):
            resTitle = resTitle[-1]+resTitle[0]
            resTitle = resTitle.strip('(').replace(')','_')
        else: resTitle = '_'.join(resTitle)
        return resTitle
        
    def _captureSubCase(self, line):
        # strips subcase ID
        return int(line.strip().split('SUBCASE ')[-1])
    
    # future method to capture load steps in dynamic analyses    
    #def _captureLoadStep(self, line):
    #    return float(line.strip().split('=')[-1])