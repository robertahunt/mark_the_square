# -*- coding: utf-8 -*-
"""
Created on Tue Jan  8 18:15:32 2019

@author: ngw861
"""
import os
import cv2
import time
import rawpy
import numpy as np
from glob import glob
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QPlainTextEdit, QMessageBox

from guis.progressDialog import progressDialog
from guis.basicGUI import basicGUI


class imageGUI(basicGUI):
    def __init__(self, initial_msg = "Working."):
        super(imageGUI, self).__init__()
        self.NEW_HEIGHT = 1024
        self.NEW_WIDTH = 680
        self.path = 'C:/Users/ngw861/Desktop/imgs/'
        self.img_formats = ['CR2','ARW','jpg','tif','tiff']
        self.img_fps = self.get_img_fps()
        self.img_fp = self.get_next_img_fp()
        self.img_format = self.img_fp.split('.')[-1]
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        self.img = self.load_img(self.img_fp)
        
        self.ORIG_HEIGHT, self.ORIG_WIDTH = self.img.shape[:2]
        self.csv_fps = glob(os.path.join(self.path,'*.csv'))
        self.preview = QLabel(self)
        self.preview.setMinimumSize(self.NEW_HEIGHT,self.NEW_WIDTH)
        self.make_preview_img(self.img)
        self.preview.setObjectName("image")
        self.preview.mousePressEvent = self.getPos
        
        self.categories = self.get_categories()
        self.addCategoryField = QLineEdit()
        self.addCategoryButton = QPushButton("Add Category")
        self.addCategoryButton.clicked.connect(self.add_category)
        
        self.categoriesDropdown = QComboBox()
        self.categoriesDropdown.addItems(self.categories)
        
        self.rmCategoryButton = QPushButton("Remove Category")
        self.rmCategoryButton.clicked.connect(self.remove_category)
        
        self.logPreview = QPlainTextEdit()
        self.logPreview.setDisabled(True)
        self.logPreviewSaveButton = QPushButton("Save Log after manual edits")
        self.logPreviewSaveButton.clicked.connect(self.save_log)
        self.logEditToggleButton = QPushButton("Toggle Allow Manual Edits")
        self.logEditToggleButton.clicked.connect(self.toggle_log_edit)
        
        self.log = []
        
        self.toNextButton = QPushButton("Done, go to next butterfly")
        self.toNextButton.clicked.connect(self.next_butterfly)
        
        
        self.initUI()
        
    def initUI(self):
        self.grid.addWidget(self.preview,0,0,10,1)
        self.grid.addWidget(self.addCategoryField,0,1,1,1)
        self.grid.addWidget(self.addCategoryButton,0,2,1,1)
        self.grid.addWidget(self.categoriesDropdown,1,1,1,2)
        self.grid.addWidget(self.rmCategoryButton,2,1,1,2)
        self.grid.addWidget(self.logPreview,3,1,3,2)
        self.grid.addWidget(self.logEditToggleButton,7,1,1,2)
        self.grid.addWidget(self.logPreviewSaveButton,8,1,1,2)
        self.grid.addWidget(self.toNextButton,9,1,1,2)
        
        
        
        
        self.setLayout(self.grid)
    
    def next_butterfly(self):
        msg = "Are you sure you want to move to the next one?"
        reply = QMessageBox.question(self, 'Message', 
                         msg, QMessageBox.Yes, QMessageBox.No)
    
        if reply == QMessageBox.No:
            return None
        
        self.save_log()
        self.logPreview.clear()
        self.log = []
        self.img_fps = self.get_img_fps()
        self.img_fp = self.get_next_img_fp()
        self.img_format = self.img_fp.split('.')[-1]
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        self.img = self.load_img(self.img_fp)
        self.make_preview_img(self.img)
    
    def toggle_log_edit(self):
        if self.logPreview.isEnabled():
            self.logPreview.setDisabled(True)
        else:
            self.logPreview.setEnabled(True)
        
    def remove_category(self):
        category = self.categoriesDropdown.currentText()
        self.categories.remove(category)
        np.savetxt(os.path.join(self.path,"categories.csv"),np.array(self.categories),fmt='%s',delimiter=",")
        self.categoriesDropdown.clear()
        self.categoriesDropdown.addItems(self.categories)
    
    def add_category(self):
        category = self.addCategoryField.text()
        if len(category.strip()):
            print(self.categories)
            self.categories += [category.strip()]
            self.categories = sorted(self.categories)
            np.savetxt(os.path.join(self.path,"categories.csv"),np.array(self.categories),fmt='%s',delimiter=",")
            self.categoriesDropdown.addItems(self.categories)
            self.addCategoryField.clear()
        else:
            self.warn('No category found to add.')
    
    def get_categories(self):
        fp = os.path.join(self.path,'categories.csv')
        if os.path.exists(fp):
            categories = np.loadtxt(fp, dtype='str',delimiter=',')
            if categories.size == 1:
                return [str(categories)]
            elif len(categories) > 1:
                return list(categories)
            else:
                return []
        else:
            return []
    
    def make_preview_img(self, img):
        preview_img = QtGui.QImage(img.data, img.shape[1], img.shape[0],
                               img.shape[1]*3, QtGui.QImage.Format_RGB888)
        preview_img = QtGui.QPixmap.fromImage(preview_img).scaled(self.NEW_HEIGHT,self.NEW_WIDTH)
        self.preview.setPixmap(preview_img)
    
    def getPos(self, event):
        
        category = self.categoriesDropdown.currentText()
        if len(category) == 0:
            self.warn('No category selected')
            return None

        x = event.pos().x()
        y = event.pos().y() 
        orig_x = int(self.ORIG_WIDTH*x/self.NEW_WIDTH)
        orig_y = int(self.ORIG_HEIGHT*y/self.NEW_HEIGHT)
        self.log = [[category, orig_x, orig_y]] + self.log
        np.savetxt(self.csv_fp,np.array(self.log),fmt='%s',delimiter=",")
        self.logPreview.setPlainText(open(self.csv_fp).read())
        
    def save_log(self):
        with open(self.csv_fp, 'w') as f:
            f.write(self.logPreview.toPlainText())    
    
    def get_img_fps(self):
        img_fps = []
        for _format in self.img_formats:
            img_fps += glob(os.path.join(self.path,'*.%s'%_format))
        if len(img_fps) == 0:
            self.warn('No images found in folder %s of types %s'%(path, img_formats))
        return img_fps
        
    def get_next_img_fp(self):
        self.csv_fps = glob(os.path.join(self.path,'*.csv'))
        for img_fp in self.img_fps:
            img_format = img_fp.split('.')[-1]
            csv_fp = img_fp.replace(img_format, 'csv')
            if csv_fp not in self.csv_fps:
                return img_fp
        self.warn('No images without csv files found')
        
    def load_img(self, img_fp):
        img_format = img_fp.split('.')[-1]
        if img_format in ['CR2','ARW']:
            with rawpy.imread(img_fp) as raw:
                return raw.postprocess()
        else:
            return cv2.cvtColor(cv2.imread(img_fp), cv2.COLOR_BGR2RGB)
            
            