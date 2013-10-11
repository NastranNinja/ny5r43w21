"""
===============================================================================
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
===============================================================================
"""
from Nastran.Results.f06 import f06File

class f06Db():
    """
    This class creates objects that will control and monitor groups of f06
    files. Its attributes contain information about the files it monitors.
    Its methods run checks on those files, remove them, add them, and update 
    them if necessary. Moreover, some methods automate the action of 
    performing the same task on all files in the database. The database
    object can also save itself to disk.
    """
    def __init__(self, f06FilePaths=[]):
        # instance variables
        self._files = {}
        # f06FilePaths is List of f06 file paths
        self._buildCollection(f06FilePaths)
        
    def _buildCollection(self, f06FilePaths):
        # collects f06File objects in self
        # keyed by hash ID
        for filePath in f06FilePaths:
            f06 = f06File(filePath)
            f06.scanFile()
            self._files[f06.getHash()] = f06
            
    def getFileList(self):
        # returns a list with all the filenames in the database
        return [self._files[hashID].filename for hashID in self._files]
            
    def removeFile(self, filename):
        # removes item based on value
        for (hashKey, f06) in self._files.items():
            if f06.filename == filename:
                del self._files[hashKey]
                break
            
    def addFile(self, filename):
        # adds filename with associated hash ID as key
        f06 = f06File(filename)
        f06.scanFile()
        self._files[f06.getHash()] = f06
                    
    def checkForUpdates(self):
        # checks each file for same hash ID
        # if hash ID is different, the file is updated
        badFiles = []
        newFiles = []
        for (hashKey, f06) in self._files.items():
            try: f06Temp = f06File(f06.filename)
            except: 
                print "could not find: %s" % f06.filename
                badFiles.append(hashKey)
                continue
            if f06Temp.getHash() == hashKey: pass
            else: 
                f06Temp.scanFile()
                self._files[f06Temp.getHash()] = f06Temp
                newFiles.append(f06Temp.file)
                badFiles.append(hashKey)
        for hashKey in badFiles:
            del self._files[hashKey]
        for filename in newFiles:
            print "updated: %s" % filename
            
    def getAllElementResults(self, title):
        # returns (header, results) found in all files of self
        allHeaders = {}
        allResults = {}
        for f06 in self._files.values():
            headers, results = f06.getElementResults(title)
            allHeaders.update(headers)
            allResults.update(results)
        return allHeaders, allResults
        
    def save(self, filename):
        # saves self to disk at filename
        import shelve
        db = shelve.open(filename)
        db.update(self._files)
        db.close()
        
    def loadDb(self, filename):
        import shelve
        self._files.update(shelve.open(filename))