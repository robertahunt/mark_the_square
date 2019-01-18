#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  2 19:27:30 2018

@author: robertahunt
"""
import sys
import time
import warnings
import subprocess

from PyQt5 import QtGui, QtWidgets, QtCore

class ClickableIMG(QtWidgets.QLabel):
    clicked = QtCore.pyqtSignal(str)
    
    def mousePressEvent(self, event):
        self.clicked.emit(self.objectName())

class basicGUI(QtWidgets.QWidget):
    def __init__(self):
        super(basicGUI, self).__init__()
        self.grid = QtWidgets.QGridLayout()
        self.grid.setSpacing(10)

    def headerLabel(self, text):
        headerLabel = QtWidgets.QLabel(text)
        headerFont = QtGui.QFont("Times", 20, QtGui.QFont.Bold) 
        headerLabel.setFont(headerFont)
        return headerLabel
        
    def warn(self, msg, _exit=False):
        warnings.warn(msg)
        warning = QtWidgets.QMessageBox()
        warning.setWindowTitle('Warning Encountered')
        warning.setText(msg)
        warning.exec_()
        if _exit: 
            sys.exit()
        
    
    #def closeEvent(self, event):
        #reply = QtGui.QMessageBox.question(self, 'Message',
        #    "Are you sure to quit?", QtGui.QMessageBox.Yes | 
        #    QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        #if reply == QtGui.QMessageBox.Yes:
        #    event.accept()
        #else:
        #    event.ignore()
        