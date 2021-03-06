# -*- coding: utf-8 -*-
"""
GUI to import photos from the card to the hard drive.
"""

import tkinter
import datetime
from shutil import copyfile
import json
import appdirs     # Manage configuration file path
import os.path
import os
import pathlib
import shutil

import photodump

base31 = 'TE8CA6ZNFGXBLWU79YHV3R4KS5MPJ2D'

def copyFile(src, tgt):
    tgtDir = os.path.dirname(tgt)
    if not os.path.isdir(tgtDir):
        pathlib.Path(tgtDir).mkdir(parents=True)
    shutil.copyfile(src, tgt)
    
def getFilesList(sourceDir):
    return photodump.listFiles(sourceDir)

def renameFile(fileName):
    imageParameters = photodump.getImageParameters(fileName)
    # cameraID
    camerasList = {'Canon EOS 20D':10,
                       'Canon EOS 1200D':20,
                       'Canon EOS 1D Mark IV': 30,
                       'Canon EOS 1D Mark III:': 40}
    cameraID = camerasList[imageParameters['Camera']]
    datePhoto = datetime.datetime.strptime(imageParameters['Date Time Original'], '%Y:%m:%d %H:%M:%S')
    # year
    year = datePhoto.strftime('%y')
    # month
    month = datePhoto.strftime('%m')
    # imageID in four digit
    imageNumber = imageParameters['Image Number']

    _, fileExtension = os.path.splitext(fileName)

    newFileName = str(cameraID) + year + month + imageNumber
    base10='0123456789'
    #base31='23456789ABCDEFGHJKLMNPRSTUVWXYZ'
    base31 = 'TE8CA6ZNFGXBLWU79YHV3R4KS5MPJ2D'

    newFileName = photodump.convertBaseNtoM(newFileName, base10, base31)
    
    return newFileName[0:3] + '_' + newFileName[3:] + fileExtension

def setDestinationDirectory(tgtDir):
    today= datetime.dateTime.now()
    

class importPhotosGUI:
    def __init__(self, master):
        
        self.getActualDate()
        self.projectName = ''
        
        self.readConfigurationFile()
        self.master = master
        self.master.title("Importing Photos")
        self.master.resizable(0, 0)

        # Create the menu bar
        self.menubar = tkinter.Menu(master)
        
        # File menu
        self.filemenu = tkinter.Menu(self.menubar, tearoff=0)
        #menubar.add_command(label="Hello!", command=self.importPhotos)
        self.filemenu.add_command(label="Quit!", command=self.master.destroy)
        self.menubar.add_cascade(label="File", menu=self.filemenu)

        #configuration menu
        self.configmenu = tkinter.Menu(self.menubar, tearoff=0)
        #menubar.add_command(label="Hello!", command=self.importPhotos)
        self.configmenu.add_command(label="Configuration...", command=self.displayConfig)
        self.menubar.add_cascade(label="Edit", menu=self.configmenu)
        
        # About Menu
        self.menubar.add_command(label="About", command=self.displayAbout)

        # display the menu
        self.master.config(menu=self.menubar)


        # Main window
        self.Label1 = tkinter.Label(self.master, text='Project:')
        #self.Label1.pack(side = tkinter.LEFT)

        self.EntryProjectName = tkinter.Entry(self.master, bd = 5 )
        self.EntryProjectName.delete(0, tkinter.END)
        self.EntryProjectName.insert(0, self.projectName)
        #self.EntryProjectName.pack(side = tkinter.RIGHT)

        self.ButtonImport = tkinter.Button(self.master, text="Import", command=self.importPhotos)
        #self.ButtonImport.pack(side = tkinter.BOTTOM)

        self.ButtonReset = tkinter.Button(self.master, text="Erase Name", command=self.resetProjectName)
        #self.ButtonReset.pack(side = tkinter.BOTTOM)
        
        self.ButtonCancel = tkinter.Button(self.master, text = "Cancel", command=self.quit)

        self.labelProgress = tkinter.Label(text = "0%")

        # Place the widget on a grid
        self.Label1.grid(row = 1, column = 1, sticky=tkinter.W, padx=10, pady=10)
        self.EntryProjectName.grid(row = 1, column = 2, columnspan=3, sticky=tkinter.W + tkinter.E)
        self.ButtonImport.grid(row=2, column=1, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        self.ButtonReset.grid(row=2, column=2, padx=10, pady=10, sticky=tkinter.W + tkinter.E)
        self.ButtonCancel.grid(row=2, column=3, ipadx= 20, padx=10, pady=10)
        self.labelProgress.grid(row=4, column=1, columnspan=4)
        
        self.centerWindow(master)

    def centerWindow(self, win):
        """
        centers a tkinter window
        :param win: the root or Toplevel window to center
        """
        win.update_idletasks()
        width = win.winfo_width()
        frm_width = win.winfo_rootx() - win.winfo_x()
        win_width = width + 2 * frm_width
        height = win.winfo_height()
        titlebar_height = win.winfo_rooty() - win.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = win.winfo_screenwidth() // 2 - win_width // 2
        y = win.winfo_screenheight() // 2 - win_height // 2
        win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        win.deiconify()

    def displayConfig(self):
        
        def validateConfig(win, newSrcDir, newTgtDir):
            self.sourceDir = newSrcDir
            self.targetDir = newTgtDir
            win.destroy()
        
        top = tkinter.Toplevel()
        top.title("About this application...")
        
        labelSrcDir = tkinter.Label(top, text='Source Directory')
        entrySrcDir = tkinter.Entry(top, bd = 5 )
        tgtDirLabel = tkinter.Label(top, text='Destination Directory')
        entryDirTgt = tkinter.Entry(top, bd = 5 )

        buttonOK = tkinter.Button(top, text="OK", command=lambda: validateConfig(top, entrySrcDir.get(), entryDirTgt.get()))
        buttonCancel = tkinter.Button(top, text="Cancel", command=top.destroy)

        entrySrcDir.delete(0, tkinter.END)
        entrySrcDir.insert(0, self.sourceDir)
        entryDirTgt.delete(0, tkinter.END)
        entryDirTgt.insert(0, self.targetDir)
        
        labelSrcDir.grid(row = 1, column = 1, sticky=tkinter.W, padx=10, pady=10)
        entrySrcDir.grid(row = 1, column = 2, columnspan=3, sticky=tkinter.W + tkinter.E)
        tgtDirLabel.grid(row = 2, column = 1, sticky=tkinter.W, padx=10, pady=10)
        entryDirTgt.grid(row = 2, column = 2, columnspan=3, sticky=tkinter.W + tkinter.E)

        buttonOK.grid(row=3, column=1)
        buttonCancel.grid(row=3, column=3)
        
        self.centerWindow(top)

    def getActualDate(self):
        today = datetime.datetime.now() 
        self.actualMonth = '{:%m}'.format(today)
        self.actualYear =  '{:%Y}'.format(today)

    def displayAbout(self):
        aboutMessage = 'Application under GPL'
        top = tkinter.Toplevel()
        top.title("About this application...")

        msg = tkinter.Message(top, text=aboutMessage)
        msg.pack()

        button = tkinter.Button(top, text="Dismiss", command=top.destroy)
        button.pack()
        self.centerWindow(top)

    def readConfigurationFile(self):
        # get conf file name and path
        configFileName = appdirs.user_config_dir(appname='DumpPhotoGUI', appauthor='Hansastro') + '/' + 'config.json'
        data = {'project name': 'XX-Test',
 'source directory': 'C:\\Users\\TH51B4\\Documents\\Python\\Source',
 'target directory': 'C:\\Users\\TH51B4\\Documents\\Python\\Target'}
        #check if the file exist, if not create it.
        if not os.path.isfile(configFileName):
            if not os.path.exists(appdirs.user_config_dir(appname='DumpPhotoGUI', appauthor='Hansastro')):
                os.makedirs(appdirs.user_config_dir(appname='DumpPhotoGUI', appauthor='Hansastro'))
            with open(configFileName, 'w+') as configFile:
                json.dump(data, configFile)
        else:
            with open(configFileName) as configFile:
                data = json.load(configFile)
        
        self.projectName = data['project name']
        self.sourceDir = data['source directory']
        self.targetDir = data['target directory']
        
    def updateConfigurationFile(self):
        self.projectName = self.EntryProjectName.get()
        data = {'project name': self.projectName,
                'source directory': self.sourceDir,
                'target directory': self.targetDir}
        confFileName = appdirs.user_config_dir(appname='DumpPhotoGUI', appauthor='Hansastro') + '/' + 'config.json'
        with open(confFileName, 'w') as configFile:
                json.dump(data, configFile, indent=4)
                
    def resetProjectName(self):
        self.EntryProjectName.delete(0, tkinter.END)
        self.EntryProjectName.insert(0, self.actualMonth + '-')
        
    def importPhotos(self):
        self.projectName = self.EntryProjectName.get()
        self.updateConfigurationFile()
        filesList = getFilesList(self.sourceDir)
        amountOfFile = len(filesList)
        cpt = 0
        for f in filesList:
            newFileName = renameFile(f)
            cpt += 1
            percentStr = '{:.0f}% - {}/{}'.format(cpt/amountOfFile*100, cpt, amountOfFile)
            self.labelProgress['text'] = percentStr
            self.master.update_idletasks()
            copyFile(f, self.targetDir + '/' + self.actualYear + '/' + self.projectName + '/to_be_sorted/' + newFileName)
        self.master.destroy()
    
    def quit(self):
        self.updateConfigurationFile()
        self.master.destroy()


top = tkinter.Tk()
app = importPhotosGUI(top)
top.mainloop()
