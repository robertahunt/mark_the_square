#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 24 20:43:32 2018

@author: robertahunt
"""

from PyQt5 import QtWidgets, QtCore, QtGui

from guis.basicGUI import basicGUI

class progressDialog(basicGUI, QtWidgets.QMainWindow):
    def __init__(self, initial_msg = "Working."):
        super(progressDialog, self).__init__()
        self.initial_msg = initial_msg
        self.resize(len(initial_msg)*10,48)
        self.initUI()
        
    def initUI(self):
        self.text = QtWidgets.QLabel(self.initial_msg)
        self.progressBar = QtWidgets.QProgressBar(self)
        self.progressBar.setRange(0,100)
        self.grid.addWidget(self.text)
        self.grid.addWidget(self.progressBar)
        self.setLayout(self.grid)
        
    def _open(self):
        QtWidgets.QApplication.processEvents()
        self.raise_()
        self.show()
        QtWidgets.QApplication.processEvents()
        
    def update(self, value, text = None):
        if text is not None:
            self.text.setText(text)
            self.resize(len(text)*10,48)
        else:
            newText = self.text.text() + '.'
            self.text.setText(newText)
            self.resize(len(newText)*10,48)
            
        self.progressBar.setValue(value)
        
        QtWidgets.QApplication.processEvents()
    
    def _close(self):
        self.update(100)
        self.progressBar.close()
        self.close()
        