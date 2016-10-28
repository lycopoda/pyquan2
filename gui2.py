#!/usr/bin/python

import os, sys, calibrate, quantify, normalize, analyse
from tkinter import *
import matplotlib.pyplot as plt

class Pyquan(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        self.parent = parent
        self.initialize()
        self._projectname = None
        self.mainmenu()
        self.framework()
        return

    def initialize(self):
        self.grid()
        pass

    def mainmenu(self):
        w, h = self.maxsize()
        self.geometry('%dx%d' % (w,h))
        self.wm_title('Pyquan')
        self._menu = Menu(self)
        self.config(menu=self._menu)
        projectmenu = self.projectmenu()
        analysemenu = self.analysemenu()
        return

    def framework(self):
        ctextbox = Canvas(self).grid()
        self.textbox(ctextbox)
        cbuttons = Canvas(self).grid(column=0, row=1)
        self.buttons(cbuttons)
        cparam_project = Canvas(self).grid(column=0,row=2,rowspan=3)
        cparam_peak = Canvas(self).grid(column=0,row=5,rowspan=3)
        cgraphs = Canvas(self).grid(column=1, row=0, columnspan=2,rowspan=8)
        self.graphs(cgraphs)
        return

    def graphs(self, cgraphs):
        self.fig = plt.figure()

        return

    def textbox(self, ctextbox):
        self._textbox = Text(ctextbox, height=5, width=50, spacing3=5)
        self._textbox.pack()
        self._textbox.place(x=0, y=0)
        self._textbox.tag_configure('bold', font=('ubuntu', 12, 'bold'))
        self._textbox.tag_configure('normal', font=('ubuntu', 12))
        self._textbox.tag_configure('red', foreground='red', font=('ubuntu', 12))
        self._textbox.tag_configure('green', foreground='forest green', font=('ubuntu', 12))
        self._textbox.insert(1.0, '\nProject: No project selected\n', 'normal')
        return

    def buttons(self, cbuttons):
        cal=Button(cbuttons,text='Calibration')
        cal.grid(row=0, column=0)
        quant = Button(cbuttons, text='Quantification').grid(row=0,column=1)
        norm = Button(cbuttons, text='Normalization').grid(row=0,column=2)
        return
    def projectlist(self):
        projectdir = os.path.join('..', 'projects')
        projectset = set()
        for item in os.listdir(projectdir):
            if os.path.isdir(os.path.join(projectdir, item)):
                projectset.add(item)
            elif item.endswith('.txt'):
                projectset.add(item[:-4])
        return sorted(projectset)

    def projectmenu(self):
        projectmenu = Menu(self._menu)
        self._menu.add_cascade(label='Project', menu=projectmenu)
        chooseprojectmenu = Menu(self._menu)
        projectmenu.add_cascade(label='Choose project',
                                menu=chooseprojectmenu)
        projectlist = self.projectlist()
        projectname = 'Dummy'
        for name in projectlist:
            chooseprojectmenu.add_radiobutton(label=name, 
                        indicatoron=0,
                        value=name,
                        command=lambda arg0=name: self.projectname(arg0))
        projectmenu.add_command(label = 'Exit', command=self.quit)
        return projectmenu

    def projectname(self, name):
        self._projectname = name
        self._textbox.delete(2.0, END)
        self._textbox.insert(1.0, '\nProject: {0}\n'.format(name), 'normal')
        return
        
    def analysemenu(self):
        analysemenu = Menu(self._menu)
        self._menu.add_cascade(label='Analyse', menu=analysemenu)
        analysemenu.add_command(label='Complete', 
                                command=self.analyse)
        analysemenu.add_command(label='Calibrate',
                                command=Calibrate(self).process)
        analysemenu.add_command(label='Quantify',
                                command=self.quantify)
        analysemenu.add_command(label='Normalize',
                                command=self.normalize)
        return

    def analyse(self):
        self.calibrate()
        self.quantify()
        self.normalize()
        return

    def calibrate(self):
        Calibrate(self).process()
        self_button_cal.ACTIVE
        return

    def quantify(self):
        Quantify(self).process()
        return

    def normalize(self):
        if self._projectname:
            Normalize(self).process()
        return


class Calibrate(object):
    def __init__(self, root):
        self._r = root
        self._p = ("Calibrate", calibrate.main)

    def process(self):
        self._r._textbox.delete(3.0, END)
        self._r._textbox.insert(END, '\n{0}'.format(self._p[0]), 'normal')
        self._r._textbox.insert(END, '\tprocessing', 'red')
        self._r.config(cursor='circle')
        self._r.update()
        if self._r._projectname:
            self._p[1](self._r._projectname)
        self._r._textbox.delete(3.0, END)
        self._r._textbox.insert(END, '\n{0}'.format(self._p[0]), 'normal')
        self._r._textbox.insert(END, '\tfinished', 'green')
        #create window to check calibrations
        self.plots
        self._r.config(cursor='')
        self._r.update()
        return
        
    def plots(self):
        #create list of plot names
        calframe = Frame(height=2, bd=1)
        #create previous, next, save and close buttons
        #open first plot
        calframe.pack(fill=X, padx=5, pady=5)
        return

class Quantify(Calibrate):
    def __init__(self, root):
        self._r = root
        self._p = ('Quantify', quantify.main)

class Normalize(Calibrate):
    def __init__(self, root):
        self._r = root
        self._p = ('Normalize', normalize.main)



if __name__ == '__main__':
    app = Pyquan(None)
    app.title('Pyquan')
    app.mainloop()

