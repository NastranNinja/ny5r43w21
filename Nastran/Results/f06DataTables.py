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
import numpy as np
from Nastran.Results import BaseClasses
# f06 results page data for each type

#==============================================================================
# page start lines {'type': dataStartLine}
#==============================================================================
startLines = {
    'QUAD4_FORCES': 9,
    'TRIA3_FORCES': 8,
    'CBUSH_FORCES': 7,
    'CBAR_FORCES': 7,
    'CBEAM_FORCES': 7}

#==============================================================================   
# general function tools
#==============================================================================
def formatLine(line, offset=0):
    # formats lines for line-by-line result tables
    data = line[offset:].strip().split()
    ID = int(data.pop(0))
    data = map(lambda x: float(x), data)
    return ID, data
    
def groupLines(page, count, stride):
    # extracts 'count' number of lines at each 'stride'
    # if 'stride' is greater than 'count', lines are skipped
    pageLineGroups = []
    for i in range(count):
        pageLineGroups.append(page[i::stride])
    groups = []
    while pageLineGroups[0]:
        groups.append(
            [lineGroup.pop(0) for lineGroup in pageLineGroups])
    return groups

#==============================================================================
# parser functions create results objects from BaseClasses
#==============================================================================
def parseQuad4Forces(page):
    results = {}
    for line in page:      
        ID, data = formatLine(line)
        forces = np.array(data[:3])
        moments = np.array(data[3:6])
        shears = np.array(data[6:8])
        results[ID] = BaseClasses.Element2D(ID, forces, moments, shears)
    return results
    
def parseTria3Forces(page):
    return parseQuad4Forces(page)
    
def parseCbushForces(page):
    results = {}
    for line in page:
        ID, data = formatLine(line,offset=1)
        forces = np.array(data[0:3])
        moments = np.array(data[3:6])
        results[ID] = BaseClasses.Element0D(ID, forces, moments)
    return results

def parseCbarForces(page):
    results = {}
    for line in page:
        ID, data = formatLine(line)
        forces = np.array([data[6]]+data[4:6])
        momentsA = np.array([data[7]]+data[0:2])
        momentsB = np.array([data[7]]+data[2:4])
        results[ID] = BaseClasses.Element1D(ID, forces, momentsA, momentsB)
    return results
        
def parseCbeamForces(page):
    results = {}
    groups = groupLines(page, 3, 3)
    for group in groups:
        ID = int(group[0][1:].strip())
        g1, data1 = formatLine(group[1])
        g2, data2 = formatLine(group[2])
        forces = np.array([data1[5]]+data1[3:5])
        momentsA = np.array([data1[6]]+data1[1:3])
        momentsB = np.array([data2[6]]+data2[1:3])
        results[ID] = BaseClasses.Element1D(ID, forces, momentsA, momentsB)
    return results
        
#==============================================================================
# parser tools for each results title
#==============================================================================
parserTools = {
    'QUAD4_FORCES': lambda page: parseQuad4Forces(page),
    'TRIA3_FORCES': lambda page: parseTria3Forces(page),
    'CBUSH_FORCES': lambda page: parseCbushForces(page),
    'CBAR_FORCES': lambda page: parseCbarForces(page),
    'CBEAM_FORCES': lambda page: parseCbeamForces(page)}