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
import pandas as pd
from glob import glob
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import QCheckBox, QFileDialog, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QComboBox, QPlainTextEdit, QMessageBox

from guis.progressDialog import progressDialog
from guis.basicGUI import basicGUI


class imageGUI(basicGUI):
    def __init__(self, initial_msg = "Working."):
        super(imageGUI, self).__init__()
        self.NEW_HEIGHT = 680#1024
        self.NEW_WIDTH = 1024#680
        self.autoSwitch = True
        self.radius = 50
        self.columns = ['category','x','y']
        self.log = pd.DataFrame(columns=self.columns)
        self.path = os.getcwd()
        self.imgsPath = os.path.join(self.path,'imgs')
        if not os.path.exists(self.imgsPath):
            os.mkdir(self.imgsPath)
        self.img_formats = ['CR2','arw','jpg','tif','tiff']
        self.img_fps = self.get_img_fps()
        self.img_fp = self.get_next_img_fp()
        self.img_format = self.img_fp.split('.')[-1]
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        self.progress = progressDialog()
        
        self.ORIG_HEIGHT, self.ORIG_WIDTH = self.img.shape[:2]
        self.csv_fps = glob(os.path.join(self.imgsPath,'*.csv'))
        self.preview = QLabel(self)
        self.preview.setMinimumSize(self.NEW_WIDTH,self.NEW_HEIGHT)
        self.preview.setMaximumSize(self.NEW_WIDTH,self.NEW_HEIGHT)
        self.make_preview_img(self.canvas)
        self.preview.setObjectName("image")
        self.preview.mousePressEvent = self.getPos
        
        self.pathField = QLineEdit()
        self.categories = self.get_categories()
        self.addCategoryField = QLineEdit()
        self.addCategoryButton = QPushButton("Add Category")
        self.addCategoryButton.clicked.connect(self.add_category)
        
        self.categoriesDropdown = QComboBox()
        self.categoriesDropdown.addItems(self.categories)
        
        self.rmCategoryButton = QPushButton("Remove Category")
        self.rmCategoryButton.clicked.connect(self.remove_category)
        
        self.autoSwitchCategoryCheckbox = QCheckBox('Auto Switch Category')
        self.autoSwitchCategoryCheckbox.toggle()
        self.autoSwitchCategoryCheckbox.stateChanged.connect(self.toggleAutoSwitchCategory)
        
        self.logPreview = QPlainTextEdit()
        self.logPreview.setDisabled(True)
        self.logPreviewSaveButton = QPushButton("Save Log after manual edits")
        self.logPreviewSaveButton.clicked.connect(self.save_log)
        self.logEditToggleButton = QPushButton("Toggle Allow Manual Edits")
        self.logEditToggleButton.clicked.connect(self.toggle_log_edit)
        
        self.log = pd.DataFrame(columns=self.columns)
        
        self.toNextButton = QPushButton("Done, go to next butterfly")
        self.toNextButton.clicked.connect(self.next_butterfly)
        
        self.toPrevButton = QPushButton("Back to previous butterfly")
        self.toPrevButton.clicked.connect(self.prev_butterfly)
        
        self.toCustomButton = QPushButton("Choose butterfly")
        self.toCustomButton.clicked.connect(self.selectFile)
        
        self.initUI()
        
    def initUI(self):
        self.grid.addWidget(self.preview,0,0,10,1)
        self.grid.addWidget(self.addCategoryField,0,1,1,1)
        self.grid.addWidget(self.addCategoryButton,0,2,1,1)
        self.grid.addWidget(self.categoriesDropdown,1,1,1,2)
        self.grid.addWidget(self.rmCategoryButton,2,1,1,2)
        self.grid.addWidget(self.autoSwitchCategoryCheckbox,3,1,1,2)
        self.grid.addWidget(self.logPreview,4,1,2,2)
        self.grid.addWidget(self.logEditToggleButton,6,1,1,2)
        self.grid.addWidget(self.logPreviewSaveButton,7,1,1,2)
        self.grid.addWidget(self.toPrevButton,8,1,1,2)
        self.grid.addWidget(self.toCustomButton,9,1,1,2)
        self.grid.addWidget(self.toNextButton,10,1,1,2)
        self.setLayout(self.grid)
    
    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Alt:
                self.next_butterfly()
            
    def wheelEvent(self,event):
        amount = np.abs(event.angleDelta().y()//120)
        direction = np.sign(event.angleDelta().y())
        for i in range(amount):
            self.switchCategory(direction=direction)
    
    def toggleAutoSwitchCategory(self):
        if self.autoSwitch == True:
            self.autoSwitch = False
        else:
            self.autoSwitch = True
    
    def next_butterfly(self):
        #msg = "Are you sure you want to move to the next one?"
        #reply = QMessageBox.question(self, 'Message', 
        #                 msg, QMessageBox.Yes, QMessageBox.No)
    
        #if reply == QMessageBox.No:
        #    return None
        self.progress._open()
        self.progress.update(30,'Loading Butterfly..')
    
        if len(self.log):
            self.save_log()
        self.logPreview.clear()
        
        self.img_fps = self.get_img_fps()
        self.img_fp = self.get_next_img_fp()
        self.img_format = self.img_fp.split('.')[-1]        
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        self.make_preview_img(self.canvas)
        
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        
        self.categoriesDropdown.setCurrentIndex(0)   
        if os.path.exists(self.csv_fp):
            self.log = pd.read_csv(self.csv_fp, names=self.columns)
            self.redraw_circles(self.log)
            self.logPreview.setPlainText(open(self.csv_fp).read())
        else:
            self.log = pd.DataFrame(columns=self.columns)
            #self.log.sort_index(ascending=False).to_csv(self.csv_fp, header=False)
            #self.logPreview.setPlainText(open(self.csv_fp).read())
        #self.log.sort_index(ascending=False).to_csv(self.csv_fp, header=False)
        #self.logPreview.setPlainText(open(self.csv_fp).read())
        
        self.progress._close()
        
    def prev_butterfly(self):
        #msg = "Are you sure you want to move to the next one?"
        #reply = QMessageBox.question(self, 'Message', 
        #                 msg, QMessageBox.Yes, QMessageBox.No)
    
        #if reply == QMessageBox.No:
        #    return None
        self.progress._open()
        self.progress.update(30,'Loading Butterfly..')
        
        if len(self.log):
            self.save_log()
        self.logPreview.clear()
        
        self.img_fps = self.get_img_fps()
        self.img_fp = self.get_prev_img_fp()
        self.img_format = self.img_fp.split('.')[-1]        
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        self.make_preview_img(self.canvas)
        self.categoriesDropdown.setCurrentIndex(0)
        
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        if os.path.exists(self.csv_fp):
            self.log = pd.read_csv(self.csv_fp, names=self.columns)
            self.redraw_circles(self.log)
            self.logPreview.setPlainText(open(self.csv_fp).read())
        else:
            self.log = pd.DataFrame(columns=self.columns)
            #self.log.sort_index(ascending=False).to_csv(self.csv_fp, header=False)
            #self.logPreview.setPlainText(open(self.csv_fp).read())
        
        self.progress._close()
    
    def selectFile(self):
        self.img_fps = self.get_img_fps()
        self.img_fp = QFileDialog.getOpenFileName()[0]
        self.progress._open()
        self.progress.update(30,'Loading Butterfly..')
        
        if len(self.log):
            self.save_log()
        self.logPreview.clear()
        
        self.img_format = self.img_fp.split('.')[-1]        
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        self.make_preview_img(self.canvas)
        self.categoriesDropdown.setCurrentIndex(0)
        
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        if os.path.exists(self.csv_fp):
            self.log = pd.read_csv(self.csv_fp, names=self.columns)
            self.redraw_circles(self.log)
            self.logPreview.setPlainText(open(self.csv_fp).read())
        else:
            self.log = pd.DataFrame(columns=self.columns)
            #self.log.sort_index(ascending=False).to_csv(self.csv_fp, header=False)
            #self.logPreview.setPlainText(open(self.csv_fp).read())
        
        self.progress._close()
        
    
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
            np.savetxt(os.path.join(self.path,"categories.csv"),np.array(self.categories),fmt='%s',delimiter=",")
            self.categoriesDropdown.clear()
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
        preview_img = QtGui.QPixmap.fromImage(preview_img).scaled(self.NEW_WIDTH,self.NEW_HEIGHT)
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
        if event.button() == QtCore.Qt.LeftButton:
            log_entry = pd.Series([category, orig_x, orig_y],index=self.columns)
            self.log = self.log.append(log_entry, ignore_index=True)
            self.update_log_file()
            self.draw_circle(orig_x, orig_y)
            self.draw_index(orig_x, orig_y, len(self.log)-1)
        elif event.button() == QtCore.Qt.RightButton:
            nearby_circle = self.check_if_nearby_point(orig_x,orig_y)
            if nearby_circle == None:
                self.switchCategory()
            else:
                self.log = self.log[self.log.index != nearby_circle]
                self.update_log_file()
                self.redraw_circles(self.log)                
        else:
            self.warn('Button not understood.')
        
        if self.autoSwitch:
            self.switchCategory()
        
    def switchCategory(self,direction=1):
        category_idx = self.categoriesDropdown.currentIndex()
        if direction >= 0:
            if (category_idx + 1) == len(self.categories):
                next_category_idx = 0
            else:
                next_category_idx = category_idx + 1
        elif direction < 0:
            if (category_idx - 1) < 0:
                next_category_idx = (len(self.categories) - 1)
            else:
                next_category_idx = category_idx - 1
        self.categoriesDropdown.setCurrentIndex(next_category_idx)
        
    def update_log_file(self):
        self.log = self.log.reset_index(drop=True)
        self.log.sort_index(ascending=False).to_csv(self.csv_fp, header=False)
        self.logPreview.setPlainText(open(self.csv_fp).read())
        
    def check_if_nearby_point(self, x, y):
        for name, row in self.log.sort_index(ascending=False).iterrows():
            _x = row['x']
            _y = row['y']
            dist = np.sqrt((_x-x)**2 + (_y-y)**2)
            if dist < self.radius:
                return name
        return None
        
    def redraw_circles(self, log):
        self.canvas = self.img.copy()
        for name,row in log.iterrows():
            self.draw_circle(row['x'],row['y'],redraw=False)
            self.draw_index(row['x'],row['y'],name)
        self.make_preview_img(self.canvas)
        
    def draw_circle(self,x,y,redraw=True):
        cv2.circle(self.canvas,(x,y),self.radius,(255,50,50), 10)
        if redraw:
            self.make_preview_img(self.canvas)
        
    def draw_index(self,x,y,idx,redraw=True):
        cv2.putText(self.canvas,str(idx),(x+self.radius+10,y),cv2.FONT_HERSHEY_SIMPLEX,2,(0,0,0), 5)
        if redraw:
            self.make_preview_img(self.canvas)
        
    def save_log(self):
        with open(self.csv_fp, 'w') as f:
            f.write(self.logPreview.toPlainText())    
    
    def get_img_fps(self):
        img_fps = []
        for _format in self.img_formats:
            img_fps += glob(os.path.join(self.imgsPath,'*.%s'%_format))
        if len(img_fps) == 0:
            self.warn('No images found in folder %s of types %s'%(self.imgsPath, self.img_formats))
        return sorted(img_fps)
        
    def get_next_img_fp(self):  
        self.csv_fps = glob(os.path.join(self.imgsPath,'*.csv'))
        for img_fp in self.img_fps:
            img_format = img_fp.split('.')[-1]
            csv_fp = img_fp.replace(img_format, 'csv')
            if csv_fp not in self.csv_fps:
                return img_fp
        self.warn('No images without csv files found')
        
    
    def get_prev_img_fp(self):
        curr_index = self.img_fps.index(self.img_fp)
        prev_index = max(0,curr_index-1)
        return self.img_fps[prev_index]
        
        
    def load_img(self, img_fp):
        img_format = img_fp.split('.')[-1]
        if img_format.lower() in ['cr2','arw']:
            with rawpy.imread(img_fp) as raw:
                return raw.postprocess(use_camera_wb=True)
        else:
            return cv2.cvtColor(cv2.imread(img_fp), cv2.COLOR_BGR2RGB)
            
