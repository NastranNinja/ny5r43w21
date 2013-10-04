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
class Results(dict):
    def __init__(self, *args):
        dict.__init__(self, *args)
    def sortXForces(self):
        raise NotImplementedError
    def sortYForces(self):
        raise NotImplementedError
    def sortZForces(self):
        raise NotImplementedError
    def sortXMoments(self):
        raise NotImplementedError
    def sortYMoments(self):
        raise NotImplementedError
    def sortZMoments(self):
        raise NotImplementedError

class ElementResults(Results):
    def __init__(self, *args):
        Results.__init__(self, *args)
    def sortStresses(self):
        raise NotImplementedError
    def sortStrains(self):
        raise NotImplementedError
        
class NodalResults(Results):
    def __init__(self, *args):
        Results.__init__(self, *args)
    def sortXDisplacements(self):
        raise NotImplementedError
    def sortYDisplacements(self):
        raise NotImplementedError
    def sortZDisplacements(self):
        raise NotImplementedError
    def sortXRotations(self):
        raise NotImplementedError
    def sortYRotations(self):
        raise NotImplementedError
    def sortZRotations(self):
        raise NotImplementedError