#!/usr/bin/python

import os, sys, calibrate, quantify, normalize, analyse
from tkinter import *
import matplotlib.pyplot as plt

class MakeButton(object):
    def __init__(self, root):
        self._root = root

    def button(self, name, command):
        b = Button(self._root, text=name, state='disabled', command=command)
        b.pack(side='left')
        return b

class Pyquan(Tk):
    def __init__(self, parent):
        Tk.__init__(self, parent)
        w, h = self.maxsize()
        self.geometry('%dx%d' % (w,h))
        self.mainmenu()
        
    def mainmenu(self):
        self._menu = Menu(self)
        self.config(menu=self._menu)
        projectmenu = self.projectmenu()
        self.mainframe()
        return

    def projectmenu(self):
        projectmenu = Menu(self._menu)
        self._menu.add_cascade(label='Project', menu=projectmenu)
        chooseprojectmenu = Menu(self._menu)
        projectmenu.add_cascade(label='Choose project',
                                menu=chooseprojectmenu)
        projectlist = self.projectlist()
        for name in projectlist:
            chooseprojectmenu.add_radiobutton(label=name, 
                        indicatoron=0,
                        value=name,
                        command=lambda arg0=name: self.projectname(arg0))
        projectmenu.add_command(label = 'Exit', command=self.quit)
        return projectmenu

    def projectname(self, name):
        self._projectname = name
        self.infotext.delete(2.0, END)
        self.infotext.insert(1.0, '\nProject: {0}\n'.format(name), 'normal')
        self.check_buttons([self._analyse, self._calibrate, self._quantify,
        self._normalize])
        return

    def check_buttons(self, buttonlist):
        for item in buttonlist:
            item['state'] = 'normal'
        return

    def mainframe(self):
        self.leftframe =  Frame(self, background='bisque')
        self.leftframe.pack(side='left', fill='both', expand=True)
        self.leftbuttons = Frame(self.leftframe, background='yellow')
        self.leftbuttons.pack(side='top', fill='x', expand=False)
        self.analysis_buttons()
        self.infoframe = Frame(self.leftframe, background='blue')
        self.infoframe.pack(side='top', fill='x', expand=False)
        self.textbox()
        self.leftbottom =  Frame(self.leftframe, background='green')
        self.leftbottom.pack(side='bottom', fill='both', expand=True)
        self.rightframe = Frame(self, background='blue')
        self.rightframe.pack(side='right', fill='both', expand=True)
        self.rightbuttons = Frame(self.rightframe, background='yellow')
        self.rightbuttons.pack(side='top', fill='x', expand=False)
        self.graphics_buttons()
        self._projectname = None
        return

    def analysis_buttons(self):
        b = MakeButton(self.leftbuttons)
        self._analyse =  b.button('analyse all', self.analyse)
        self._calibrate = b.button('calibrate', self.calibrate)
        self._quantify = b.button('quantify', self.quantify)
        self._normalize = b.button('normalize', self.normalize)

    def show_projects(self):
        return


    def graphics_buttons(self):
        b = MakeButton(self.rightbuttons)
        self._show_cal = b.button('calibration', self.calibration)
        self._show_quant =  b.button('quantification', self.quantification)
        self._show_norm = b.button('normalization', self.normalization)

    def calibration(self):
        
        return

    def quantification(self):
        return

    def normalization(self):
        return

    def graphs(self, cgraphs):
        self.fig = plt.figure()

        return

    def textbox(self):
        self.infotext = Text(self.infoframe, width=50, height=5, spacing3=5)
        self.infotext.pack(side='top', fill='both', expand=False)
        self.infotext.tag_configure('bold', font=('ubuntu', 12, 'bold'))
        self.infotext.tag_configure('normal', font=('ubuntu', 12))
        self.infotext.tag_configure('red', foreground='red', font=('ubuntu',
        12))
        self.infotext.tag_configure('green', foreground='forest green',
        font=('ubuntu', 12))
        self.infotext.insert(1.0, '\nProject: No project selected\n', 'normal')
        return

    def showcal(self):
        '''Show callibration graphs'''
        return

    def showquant(self):
        '''Show callibration graphs'''
        return

    def shownorm(self):
        '''Show callibration graphs'''
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
        self.check_buttons([self._show_cal])
        return

    def quantify(self):
        Quantify(self).process()
        self.check_buttons([self._show_quant])
        return

    def normalize(self):
        Normalize(self).process()
        self.check_buttons([self._show_norm])
        return


class Calibrate(object):
    def __init__(self, root):
        self._r = root
        self._p = ("Calibrate", calibrate.main)

    def process(self):
        self._r.infotext.delete(3.0, END)
        self._r.infotext.insert(END, '\n{0}'.format(self._p[0]), 'normal')
        self._r.infotext.insert(END, '\tprocessing', 'red')
        self._r.config(cursor='circle')
        self._r.update()
        if self._r._projectname:
            self._p[1](self._r._projectname)
        self._r.infotext.delete(3.0, END)
        self._r.infotext.insert(END, '\n{0}'.format(self._p[0]), 'normal')
        self._r.infotext.insert(END, '\tfinished', 'green')
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

