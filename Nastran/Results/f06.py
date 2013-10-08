"""
======================================================================
http://opensource.org/licenses/BSD-2-Clause

Copyright (c) 2013, Benjamin E. Taylor
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
import itertools
from Nastran.Results import Collections
from Nastran.Results import f06DataTables

class f06File():
    
    def __init__(self, filename):
        # instance variables
        import os
        self.file = filename
        self.mode = 'rb'
        self._pages = []
        #self._scanFile()
            
    def getPage(self, pageNum):
        return self._pages[pageNum]
       
    def getTitles(self):
        titles = []
        for page in self._pages:
            if page.title != None and page.title not in titles:
                titles.append(page.title)
        return titles
        
    def getElementResults(self, title):
        # accepts: result title (title)
        # returns: Dictionary tuple (header, results),
        #   header[ subcase ]  
        #   results[ subcase ][ elementID ]
        import time
        assert title in self.getTitles()
        # initialize results collection object
        results = Collections.ElementResults()
        # initialize dictionaries to contain all data and headers 
        data = {}
        header = {}
        # grab parser function from f06DataTables module
        parseFunction = f06DataTables.parserTools[title]
        startTime = time.time()
        # filter the file for pages with indicated result title and 
        # iterate through each page storing the data
        for page in self._filterFile(title):
            # check if subcase has been found yet, if not add it
            # to dictionaries
            subcase = page.subcase
            if subcase not in data: 
                data[subcase] = []
                header[subcase] = page.getHeader()
            # collect the page data
            data[subcase].extend(page.getDataList())
        for subcase in data:
            results[subcase] = parseFunction(data[subcase])
        print "%.2f seconds" % (time.time() - startTime,)
        return header, results
        
    def getHash(self):
        # generates a hash ID for future new file checks
        import hashlib
        fileObj = open(self.file, self.mode)
        hashType = hashlib.sha256()
        hashType.update(fileObj.read(256))
        fileObj.close()
        return hashType.digest()
        
    def scanFile(self):
        # scan the file and create f06Page objects
        import time
        import re
        startTime = time.time()
        # open file
        fileObj = open(self.file, self.mode)
        # read line-by-line in binary mode, page information is stored
        # as byte locations
        line = fileObj.readline()
        while line:
            # capture byte location for beginning of each line
            beginLine = fileObj.tell() - len(line)
            if line.startswith('1'): # found a new page
                pageNum = len(self._pages)
                # if this is not the first page, save end location of 
                # previous page
                if pageNum > 0: self._pages[-1].end = beginLine
                # create the f06Page object and append it
                self._pages.append(f06Page(pageNum,beginLine,self.file))
            elif 'SUBCASE ' in line: # found the subcase
                # capture the subcase and add it to current page
                subcase = self._captureSubCase(line)
                self._pages[-1].subcase = subcase
            elif re.search(r'\w\s\w\s\w\s.*\(.*\)',line): # found the title
                # parse and capture the title, then add it to current page
                resultTitle = self._parseTitle(line)
                self._pages[-1].title = resultTitle
            # go to next line
            line = fileObj.readline()
        self._pages[-1].end = beginLine
        fileObj.close()
        print "%.2f seconds" % (time.time() - startTime,)
                
    def _filterFile(self, title):
        # accepts 'title', returns pages of type 'title'
        filterFunc = lambda page: page.title==title
        return itertools.ifilter(filterFunc, self._pages)
        
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

        
class f06Page():
    
    def __init__(self, number, lineNum, f06File):
        # instance variables
        self.number = number
        self.start = lineNum
        self.file = f06File
        self.mode = 'rb'
        self.end = None
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
    
    def getDataList(self):
        # returns: list of data lines from f06 page (excluding header)
        if not hasattr(self,'dataStartLine'): self._setDataStartLine()
        fileObj = open(self.file, self.mode)        
        fileObj.seek(self.start)
        numBytes = len(self)
        pageLines = fileObj.read(numBytes).splitlines()
        fileObj.close()
        return pageLines[self.dataStartLine:]

    def getHeader(self):
        # returns header of f06 page
        if not hasattr(self,'dataStartLine'): self._setDataStartLine() 
        fileObj = open(self.file, self.mode)
        fileObj.seek(self.start)
        header =  [fileObj.readline() for i in range(self.dataStartLine)]
        fileObj.close()
        return header
        
    def _setDataStartLine(self):
        # sets data start line for page
        self.dataStartLine = f06DataTables.startLines[self.title]