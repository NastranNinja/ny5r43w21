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
#import numpy as np

class Result():
    # Common attributes:
    #   self.subcase = subcase
    #   self.ID = ID
    #   self.source = source
    def __add__(self, other):
        raise NotImplementedError
    def __sub__(self, other):
        raise NotImplementedError
    def __mul__(self, other):
        raise NotImplementedError
    def getType(self):
        return type(self)
    
class Linear(Result):
    # Interface requirements:
    #   self.forces = np.array([Px, Py, Pz])
    #   self.moments = np.array([Mx, My, Mz])      
    def rotate(self,dirCosines):
        raise NotImplementedError
        
class Element(Linear):
    # Interface requirements:
    #   self.stresses = np.array([[s11, s12, s13],
    #                             [s21, s22, s23],
    #                             [s31, s32, s33]])
    #   self.strains = np.array([[e11, e12, e13],
    #                            [e21, e22, e23],
    #                            [e31, e32, e33]])
    def rotateStress(self,dirCosines):
        # Tensor rotation
        raise NotImplementedError
    def rotateStrain(self,dirCosines):
        # Tensor rotation
        raise NotImplementedError
    
class Node(Linear):
    def __init__(self, ID, translations, rotations):
        # self.translations = np.array([dx, dy, dz])
        self.translations = translations
        # self.rotations = np.array([rx, ry, rz])
        self.rotations = rotations
    def interpolate(self):
        raise NotImplementedError
    def extrapolate(self):
        raise NotImplementedError
    def fitData(self):
        raise NotImplementedError
        
class Element0D(Linear):
    def __init__(self, ID, forces, moments):
        self.ID = ID
        # self.forces = np.array([Px, Py, Pz])  
        self.forces = forces
        # self.moments = np.array([Mx, My, Mz])
        self.moments = moments
    def flipSigns(self):
        self.forces = self.forces * -1.
        self.moments = self.moments * -1.
        
class Element1D(Element):
    def __init__(self, ID, forces, momentsA, momentsB):
        self.ID = ID
        # self.forces = np.array([Px, Vy, Vz])        
        self.forces = forces
        # self.momentsA = np.array([T, Mya, Mza])
        self.momentsA = momentsA
        # self.momentsB = np.array([T, Myb, Mzb])
        self.momentsB = momentsB
    def maxMoment(self):
        # compare 3D moment vector on each side
        # return highest side
        raise NotImplementedError
    
class Element2D(Element):
    def __init__(self, ID, forces, moments, shears):
        self.ID = ID        
        # self.forces = np.array([Nx, Ny, Nxy])
        self.forces = forces
        # self.moments = np.array([Mx, My, Mxy])
        self.moments = moments
        # self.shears = np.array([Qx, Qy])
        self.shears = shears
    def rotate(self, angle):
        # In-plane rotation
        raise NotImplementedError
    def shrinkThickness(self, t_old, t_new):
        raise NotImplementedError
    def growThickness(self, t_old, t_new):
        raise NotImplementedError
    def minThickness(self, t_old, MS):
        raise NotImplementedError
    def getUpperStress(self):
        raise NotImplementedError
    def getLowerStress(self):
        raise NotImplementedError
    
