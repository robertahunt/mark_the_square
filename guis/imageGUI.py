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

from skimage.segmentation import mark_boundaries
from guis.progressDialog import progressDialog
from guis.basicGUI import basicGUI

global start_time
def start_timer():
    global start_time
    start_time = pd.Timestamp.now()

class imageGUI(basicGUI):
    def __init__(self, initial_msg = "Working."):
        super(imageGUI, self).__init__()
        print('a')
        self.NEW_HEIGHT_I = int(680*1.3)
        self.NEW_WIDTH_I = int(1024*1.3)
        self.NEW_HEIGHT_M = 680//2
        self.NEW_WIDTH_M = 1024//2
        self.radius = 5
        self.columns = ['category',1,2,3,4]
        self.log = pd.DataFrame(columns=self.columns)
        self.path = os.getcwd()
        self.imgsPath = "\\\\io.erda.dk@SSL\\DavWWWRoot\\alcon image analysis\\robertas_thesis\\datasets\\resamples\\1_lowres"
        if not os.path.exists(self.imgsPath):
            os.mkdir(self.imgsPath)
        self.img_formats = ['jpg']
        print('b')
        self.img_fps = self.get_img_fps()
        self.img_fp = self.get_next_img_fp()
        print('c')
        self.img_format = self.img_fp.split('.')[-1]
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        self.mask_fp = self.img_fp.replace('lowres','_masks')
        self.mask_csv_fp = self.mask_fp.replace(self.img_format,'csv')
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        self.mask = self.load_img(self.mask_fp)
        self.progress = progressDialog()
        print('d')
        
        self.ORIG_HEIGHT, self.ORIG_WIDTH = self.img.shape[:2]
        self.csv_fps = glob(os.path.join(self.imgsPath,'*.csv'))
        self.preview = QLabel(self)
        self.preview.setMinimumSize(self.NEW_WIDTH_I,self.NEW_HEIGHT_I)
        self.preview.setMaximumSize(self.NEW_WIDTH_I,self.NEW_HEIGHT_I)
        self.make_preview_img(self.canvas)
        self.preview.setObjectName("image")
        print('e')
        
        self.mask_preview = QLabel(self)
        self.mask_preview.setMinimumSize(self.NEW_WIDTH_M,self.NEW_HEIGHT_M)
        self.mask_preview.setMaximumSize(self.NEW_WIDTH_M,self.NEW_HEIGHT_M)
        self.make_mask_preview_img(self.mask)
        self.mask_preview.setObjectName("image")
        self.mask_preview.mousePressEvent = self.getMaskPos
        print('f')
        
        self.pathField = QLineEdit()
        
        self.logPreview = QPlainTextEdit()
        self.logPreview.setDisabled(True)
        self.logPreviewSaveButton = QPushButton("Save Log after manual edits")
        self.logPreviewSaveButton.clicked.connect(self.save_log)
        self.logEditToggleButton = QPushButton("Toggle Allow Manual Edits")
        self.logEditToggleButton.clicked.connect(self.toggle_log_edit)
        print('g')
        
        self.getAvgColor = False
        self.toggleGetAvgColorBox = QCheckBox('Toggle Get Avg Color')
        self.toggleGetAvgColorBox.stateChanged.connect(self.toggleGetAvgColor)
        
        self.preview.mousePressEvent = self.getPos
        self.preview.mouseReleaseEvent = self.getImgxy
        
        self.log = pd.DataFrame(columns=self.columns)
        
        if os.path.exists(self.mask_csv_fp):
            self.log = pd.read_csv(self.mask_csv_fp, names=self.columns, sep=' ')
            self.redraw_corners(self.log)
            self.logPreview.setPlainText(open(self.mask_csv_fp).read())
            
        self.missing_sections = []
        self.update_missing_sections()
        
        self.toNextButton = QPushButton("Done, go to next butterfly")
        self.toNextButton.clicked.connect(self.next_butterfly)
        
        self.toPrevButton = QPushButton("Back to previous butterfly")
        self.toPrevButton.clicked.connect(self.prev_butterfly)
        
        self.toCustomButton = QPushButton("Choose butterfly")
        self.toCustomButton.clicked.connect(self.selectFile)
        
        self.initUI()
        print('h')
        
    def toggleGetAvgColor(self):
        if self.getAvgColor == False:
            self.getAvgColor = True
        else:
            self.getAvgColor = False
        
    def initUI(self):
        self.grid.addWidget(self.preview,0,0,10,1)
        self.grid.addWidget(self.mask_preview,0,1,10,1)
        self.grid.addWidget(self.toggleGetAvgColorBox,0,2,1,2)
        self.grid.addWidget(self.logPreview,1,2,5,2)
        self.grid.addWidget(self.logEditToggleButton,6,2,1,2)
        self.grid.addWidget(self.logPreviewSaveButton,7,2,1,2)
        self.grid.addWidget(self.toPrevButton,8,2,1,2)
        self.grid.addWidget(self.toCustomButton,9,2,1,2)
        self.grid.addWidget(self.toNextButton,10,2,1,2)
        self.setLayout(self.grid)
    
    def keyPressEvent(self, event):
        if type(event) == QtGui.QKeyEvent:
            if event.key() == QtCore.Qt.Key_Alt:
                self.next_butterfly()
    
    def next_butterfly(self):
        self.progress._open()
        self.progress.update(30,'Loading Butterfly..')
        print(1)
        if len(self.log):
            self.save_log()
        self.logPreview.clear()
        print(2)
        
        #self.img_fps = self.get_img_fps()
        self.img_fp = self.get_next_img_fp()
        print(3)
        self.img_format = self.img_fp.split('.')[-1]        
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        print(4)
        self.make_preview_img(self.canvas)
        print(5)
        
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        self.mask_fp = self.img_fp.replace('lowres','_masks')
        self.mask_csv_fp = self.mask_fp.replace(self.img_format,'csv')
        self.mask = self.load_img(self.mask_fp)
        self.make_mask_preview_img(self.mask)
        print(6)
        
        if os.path.exists(self.mask_csv_fp):
            self.log = pd.read_csv(self.mask_csv_fp, names=self.columns, sep=' ')
            self.redraw_corners(self.log)
            self.logPreview.setPlainText(open(self.mask_csv_fp).read())
        else:
            self.log = pd.DataFrame(columns=self.columns)
        
        print(7)
        self.progress._close()
        
    def prev_butterfly(self):
        self.progress._open()
        self.progress.update(30,'Loading Butterfly..')
        
        if len(self.log):
            self.save_log()
        self.logPreview.clear()
        
        #self.img_fps = self.get_img_fps()
        self.img_fp = self.get_prev_img_fp()
        self.img_format = self.img_fp.split('.')[-1]        
        self.img = self.load_img(self.img_fp)
        self.canvas = self.img.copy()
        self.make_preview_img(self.canvas)
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        self.mask_fp = self.img_fp.replace('lowres','_masks')
        self.mask_csv_fp = self.mask_fp.replace(self.img_format,'csv')
        self.mask = self.load_img(self.mask_fp)
        self.make_mask_preview_img(self.mask)
        
        
        self.csv_fp = self.img_fp.replace(self.img_format,'csv')
        if os.path.exists(self.csv_fp):
            self.log = pd.read_csv(self.csv_fp, names=self.columns, sep=' ')
            self.redraw_corners(self.log)
            self.logPreview.setPlainText(open(self.csv_fp).read())
        else:
            self.log = pd.DataFrame(columns=self.columns)
        
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
            self.log = pd.read_csv(self.csv_fp, names=self.columns, sep=' ')
            self.redraw_circles(self.log)
            self.logPreview.setPlainText(open(self.mask_csv_fp).read())
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
        
    
    def make_preview_img(self, img):
        img = img + self.mask*5
        preview_img = QtGui.QImage(img.data, img.shape[1], img.shape[0],
                               img.shape[1]*3, QtGui.QImage.Format_RGB888)
        preview_img = QtGui.QPixmap.fromImage(preview_img).scaled(self.NEW_WIDTH_I,self.NEW_HEIGHT_I)
        self.preview.setPixmap(preview_img)
    
    def make_mask_preview_img(self, img):
        
        preview_img = QtGui.QImage((img*30).data, img.shape[1], img.shape[0],
                               img.shape[1]*3, QtGui.QImage.Format_RGB888)
        preview_img = QtGui.QPixmap.fromImage(preview_img).scaled(self.NEW_WIDTH_M,self.NEW_HEIGHT_M)
        self.mask_preview.setPixmap(preview_img)
    
    def getPos(self, event):     
        x = event.pos().x()
        y = event.pos().y() 
        orig_x = int(self.ORIG_WIDTH*x/self.NEW_WIDTH_I)
        orig_y = int(self.ORIG_HEIGHT*y/self.NEW_HEIGHT_I)
        if event.button() == QtCore.Qt.LeftButton:
            if self.getAvgColor:
                self.pos1 = [orig_y, orig_x]
            else:
                log_entry = pd.Series(['corner',orig_x, orig_y, np.nan, np.nan],index=self.columns)
                self.log = self.log.append(log_entry, ignore_index=True)
                self.update_log_file()
                self.draw_circle(orig_x, orig_y)
        elif event.button() == QtCore.Qt.RightButton:
            nearby_circle = self.check_if_nearby_point(orig_x,orig_y)
            if nearby_circle != None:
                self.log = self.log[self.log.index != nearby_circle]
                self.update_log_file()
                self.redraw_corners(self.log)                
        else:
            self.warn('Button not understood.')
        
    def getMaskPos(self, event):    
        x = event.pos().x()
        y = event.pos().y() 
        orig_x = int(self.ORIG_WIDTH*x/self.NEW_WIDTH_M)
        orig_y = int(self.ORIG_HEIGHT*y/self.NEW_HEIGHT_M)
        if event.button() == QtCore.Qt.RightButton:
            section = self.get_mask_section(orig_x,orig_y)
            if section != 0:
                self.mask[self.mask == section] = 0
                self.log = self.log[(self.log['category'] == 'corner') | (self.log[1] != section)]
                self.update_log_file()
                self.make_mask_preview_img(self.mask)   
                self.update_missing_sections()
        else:
            self.warn('Button not understood.')
    
    def getImgxy(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.getAvgColor:
                x = event.pos().x()
                y = event.pos().y() 
                orig_x = int(self.ORIG_WIDTH*x/self.NEW_WIDTH_I)
                orig_y = int(self.ORIG_HEIGHT*y/self.NEW_HEIGHT_I)
                self.pos2 = [orig_y, orig_x]
                section = self.get_missing_section()
                if section != None:
                    self.mask[self.pos1[0]:self.pos2[0],self.pos1[1]:self.pos2[1]] = [section,section,section]
                    new_avg_color = self.img[self.pos1[0]:self.pos2[0],self.pos1[1]:self.pos2[1]].mean(axis=(0,1))
                    log_entry = pd.Series(['color',int(section),new_avg_color[0],new_avg_color[1],new_avg_color[2]],index=self.columns)
                    self.log = self.log.append(log_entry, ignore_index=True)
                    self.update_log_file()
                    self.make_mask_preview_img(self.mask)   
                    self.missing_sections = []
                    self.update_missing_sections()
                    self.save_mask(self.mask)
    
    def save_mask(self,mask):
        cv2.imwrite(self.mask_fp,mask)
    
    def update_missing_sections(self):
        sections = self.log[self.log['category'] == 'color'][1].map(int)
        for i in range(1,9):
            if i not in sections.values:
                self.missing_sections += [i]
                
    def get_missing_section(self):
        if len(self.missing_sections):
            return sorted(self.missing_sections)[0]
        else:
            return None
    
    def get_mask_section(self, orig_x,orig_y):
        return self.mask[orig_y,orig_x].mean()
    
    def update_log_file(self):
        self.log = self.log.reset_index(drop=True)
        self.log.loc[self.log['category'] == 'color',1] = self.log.loc[self.log['category'] == 'color',1].map(int)
        self.log.sort_index(ascending=False).to_csv(self.csv_fp, header=False, index=False, sep=' ')
        self.logPreview.setPlainText(open(self.csv_fp).read())
        
    def check_if_nearby_point(self, x, y):
        for name, row in self.log.sort_index(ascending=False).iterrows():
            if row['category']=='corner':
                _x = row[1]
                _y = row[2]
                dist = np.sqrt((_x-x)**2 + (_y-y)**2)
                if dist < self.radius:
                    return name
        return None
        
    def redraw_corners(self, log):
        self.canvas = self.img.copy()
        for name,row in log[log['category']=='corner'].iterrows():
            self.draw_circle(int(row[1]),int(row[2]),redraw=False)
        self.make_preview_img(self.canvas)
        
    def draw_circle(self,x,y,redraw=True):
        cv2.circle(self.canvas,(x,y),self.radius,(50,50,255), 2)
        if redraw:
            self.make_preview_img(self.canvas)

        
    def save_log(self):
        with open(self.csv_fp, 'w') as f:
            f.write(self.logPreview.toPlainText())    
    
    def get_img_fps(self):
        print(1)
        img_fps = []
        for _format in self.img_formats:
            img_fps += glob(os.path.join(self.imgsPath,'*.%s'%_format))
        print(2)
            
        #mask_fps = []
        #for _format in self.img_formats:
        #    mask_fps += glob(os.path.join('\\\\io.erda.dk@SSL\\DavWWWRoot\\thesis\\datasets\\copenhagen\\1__masks\\','*.%s'%_format))
            
        #new_img_fps = []
        #print(len(new_img_fps))
        #for img_fp in img_fps:
        #    fn = os.path.basename(img_fp)
        #    mask_fp = '\\\\io.erda.dk@SSL\\DavWWWRoot\\thesis\\datasets\\copenhagen\\1__masks\\'+fn
        #    if mask_fp in mask_fps:
        #        new_img_fps += [img_fp]
        #print(len(new_img_fps))
        csv_fps = glob(os.path.join(self.imgsPath,'*.csv'))
        print(3)
        img_fps_from_csv_fps = map(lambda x: x.replace('csv','jpg'),csv_fps)
        print(4)
        img_fps = set(img_fps).difference(img_fps_from_csv_fps)
        print(5)
        #for img_fp in img_fps:
        #    img_format = img_fp.split('.')[-1]
        #    csv_fp = img_fp.replace(img_format, 'csv')
        #    if csv_fp not in self.csv_fps:
        #        new_img_fps += [img_fp]
                
                
            
        if len(img_fps) == 0:
            self.warn('No images found in folder %s of types %s without csv files'%(self.imgsPath, self.img_formats))
        return sorted(img_fps)
        
    def get_next_img_fp(self):  
        if hasattr(self, 'img_fp'):
            current_img_index = self.img_fps.index(self.img_fp)
        else:
            current_img_index = -1
        next_img_index = current_img_index + 1
        if next_img_index < len(self.img_fps):
            return self.img_fps[next_img_index]

        self.warn('No images without csv files found')

    
    def get_prev_img_fp(self):
        curr_index = self.img_fps.index(self.img_fp)
        prev_index = max(0,curr_index-1)
        return self.img_fps[prev_index]
        
        
    def load_img(self, img_fp):
        print(img_fp)
        img_format = img_fp.split('.')[-1]

        if img_format.lower() in ['cr2','arw']:
            with rawpy.imread(img_fp) as raw:
                return raw.postprocess(use_camera_wb=True)
        else:
            return cv2.cvtColor(cv2.imread(img_fp), cv2.COLOR_BGR2RGB)
            
