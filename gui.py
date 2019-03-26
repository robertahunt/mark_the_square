# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import os
import sys
import numpy as np
from glob import glob
from PyQt5.QtWidgets import QApplication, QWidget

from guis.progressDialog import progressDialog
from guis.imageGUI import imageGUI
from guis.basicGUI import basicGUI


class GUI(basicGUI):
    def __init__(self):
        super(GUI, self).__init__()
        
        self.progress = progressDialog()
        self.progress._open()

        self.progress.update(20,'Getting Coffee..')
        
        self.image = imageGUI()
        self.progress.update(30,'Checking Appendages..')
        self.initUI()
        
        
    def initUI(self):        
        self.setWindowTitle("Where in the world is the square?")  
        #self.setWindowIcon(QtGui.QIcon('icon.png')) 
  
        self.grid.addWidget(self.image, 0, 0)
        #self.grid.addWidget(self.config, 1, 0)
        
        self.setLayout(self.grid)
        self.show()
        self.progress._close()

        

if __name__ == '__main__':

    #QtCore.QCoreApplication.addLibraryPath(os.path.join(os.path.dirname(QtCore.__file__), "plugins"))
    
    app = QApplication(sys.argv)
    #app.setWindowIcon(QtGui.QIcon('icon.png'))
    gui = GUI()
    sys.exit(app.exec_()) 