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
from Tkinter import *
from tkFileDialog import *

def menuMaker(win, menus=[]):
    topMenu = Menu(win)
    win.config(menu=topMenu)
    for (name, key, items) in menus:
        pullDown = Menu(topMenu, tearoff=0)
        addMenuItems(pullDown, items)
        topMenu.add_cascade(label = name,
                            underline = key,
                            menu = pullDown)
                            
def addMenuItems(menu, items):
    for item in items:
            if item == 'separator':
                menu.add_separator({})
            elif isinstance(item[2], list):
                pullOver = Menu(menu, tearoff=0)
                addMenuItems(pullOver, item[2])
                menu.add_cascade(label = item[0],
                                 underline = item[1],
                                 menu = pullOver)
            else:
                menu.add_command(label = item[0],
                                   underline = item[1],
                                   command = item[2])

class InputFrame(Frame):
    def __init__(self, parent=None, label=None, button=True, chk=False):
        Frame.__init__(self, parent)
        #self.pack(expand=YES, fill=BOTH)
        self.textVar = StringVar()
        self.label = label
        if chk:
            self.chk = IntVar()
            self.chk.set(1)
            Checkbutton(self, 
                        variable=self.chk, 
                        command=self.setState).pack(side=LEFT)
        Label(self, text=self.label).pack(side=LEFT)
        self.Entry = Entry(self, textvariable=self.textVar)
        self.Entry.pack(side=LEFT, expand=YES, fill=X)
        if button:
            self.Button = Button(self, text='...', command=self.callback)
            self.Button.pack(side=LEFT)
    def callback(self):
        pass
    def getInput(self):
        return self.textVar.get()
    def setState(self):
        if self.chk.get(): self.enable()
        else:
            self.clear()
            self.disable()
    def disable(self):
        self.Entry.config(state=DISABLED)
        self.Button.config(state=DISABLED)
    def enable(self):
        self.Entry.config(state=NORMAL)
        self.Button.config(state=NORMAL)
    def clear(self):
        self.Entry.delete(0,END)
        
class FindFile(InputFrame):
    def __init__(self, parent=None, label=None, chk=False):
        InputFrame.__init__(self, parent=parent, label=label, chk=chk)
    def callback(self):
        self.textVar.set(askopenfilename(title=self.label))
        
class SaveFile(InputFrame):
    def __init__(self, parent=None, label=None):
        InputFrame.__init__(self, parent=parent, label=label)
    def callback(self):
        self.textVar.set(asksaveasfilename())
    
class FindDir(InputFrame):
    def __init__(self, parent=None, label=None):
        InputFrame.__init__(self, parent=parent, label=label)
    def callback(self):
        self.textVar.set(askdirectory())

class ScrollListbox(Frame):
    def __init__(self,parent=None):
        Frame.__init__(self,parent)
        scroll = Scrollbar(self,orient=VERTICAL)
        self.Listbox = Listbox(self,
                               selectmode=EXTENDED,
                               yscrollcommand=scroll.set)
        scroll.config(command=self.Listbox.yview)
        scroll.pack(side=RIGHT,fill=Y)
        self.Listbox.pack(expand=YES, fill=BOTH)
        Button(self, text='CLEAR', 
               command=self.clear).pack(side=RIGHT, expand=YES, fill=X)
        Button(self, text='SELECT ALL', 
               command=self.selectAll).pack(side=RIGHT, expand=YES, fill=X)
    def fill(self,lineList):
        for string in lineList:
            self.Listbox.insert(END,string)
    def selection(self):
        return (self.Listbox.get(x) for x in self.Listbox.curselection())
    def clear(self):
        self.Listbox.delete(0,END)
    def selectAll(self):
        self.Listbox.select_set(0,END)
        
class helpWindow(Frame):
    def __init__(self, parent=None, text=None):
        Frame.__init__(self, parent)
        sbar = Scrollbar(self)
        txt = Text(self)
        sbar.config(command=txt.yview)
        txt.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        txt.pack(side=TOP ,expand=YES, fill=BOTH, padx=5, pady=5)
        self.pack(expand=YES, fill=BOTH)
        txt.insert('1.0', text)
        txt.config(bg='gray94')
        txt.config(state=DISABLED)
