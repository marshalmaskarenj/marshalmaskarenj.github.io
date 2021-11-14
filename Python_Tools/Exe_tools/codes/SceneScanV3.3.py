# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 16:38:48 2019
https://www.youtube.com/watch?v=z5yLiBTyIZ4
@author: marshal.maskarenj
"""
import cv2
import cmapy
import numpy as np
import exifread
from fractions import Fraction
import ctypes
from imutils import contours
from skimage import measure
import imutils
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0)/1, user32.GetSystemMetrics(1)/1
from PyQt5 import QtCore, QtGui, QtWidgets
#from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QDialog, QVBoxLayout#, QTextEdit
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
#from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import sys
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import datetime
#import random
#from PIL import Image
#from PyQt5.QtGui import QPainter, QColor, QPen


def openFileDialog():
    global imgs, tms, filename1
    qfd = QFileDialog()
    fname=QFileDialog.getOpenFileNames(qfd, "Marshal Files"," ","All Files (*);; JPEG Files(*.jpg);; Python Files(*.py)")
    filename1=fname[0]
    imgs, tms = readImagesAndTimes(filename1)
    return imgs, tms

def readImagesAndTimes(fn1):
    global images, times
    images = []
    times = []
    for fn in fn1:
        f = open(fn, 'rb')
        tags = exifread.process_file(f)
        shutterspeed = tags['EXIF ExposureTime']
        ssval=str(shutterspeed)
        ssval=Fraction(ssval)
        ssval=float(ssval)
        times.append(ssval)
        im = cv2.imread(fn)
        images.append(im)
    times=np.array(times,dtype=np.float32)
    return images, times

def rgb2gray(rgb):
    return np.dot(rgb[...,:3], [0.2989, 0.5870, 0.1140])

def sqar_gen(hdrfile):
    lenHDR= len(hdrfile)
    print(lenHDR)
    widHDR= len(hdrfile[1])
    print(widHDR)
    if lenHDR>widHDR:
        minsize=widHDR
        maxsize=lenHDR
    else:
        minsize=lenHDR
        maxsize=widHDR
    sq_ar=np.zeros(shape=(minsize,minsize,3))
    startval=int((maxsize-minsize)/2)
    for hdrnum in range (0,minsize,1):
        if lenHDR>widHDR:  
            sq_ar[hdrnum,:,:]=hdrfile[startval+hdrnum,:,:]
        else:
            sq_ar[:,hdrnum,:]=hdrfile[:,startval+hdrnum,:]
    return sq_ar, minsize

def vignette(min_size):
    dimval=min_size
    aval=dimval
    bval=dimval
    val = np.zeros(shape=(aval, bval))  # array to store the value of Ldes
    for alpha in range(0, bval, 1):
        for Z in range(0, aval, 1):
            Ldes=(-0.0000000001*(float(Z/aval)**6))+(0.00000002*(float(Z/aval)**5))+(-0.000001*(float(Z/aval)**4))+(0.00005*(float(Z/aval)**3))+(-0.0006*(float(Z/aval)**2))+(-0.0012*(float(Z/aval)**1))+1.011
            val[Z,alpha]=Ldes
    val=np.rot90(val)
    img = val.astype(np.float32)
    value = np.sqrt(((img.shape[0]/2.0)**2.0)+((img.shape[1]/2.0)**2.0))
    polar_image = cv2.linearPolar(img,(img.shape[0]/2, img.shape[1]/2), value*0.7085, cv2.WARP_INVERSE_MAP)
#    polar_imagemid=polar_image*1
#    polar_imageshow = (polar_imagemid).astype(np.uint8)
    vig_corrRGB=np.zeros(shape=(minsize,minsize,3))
    polar_image[polar_image < 0.01] = 0.01
    mask=np.reciprocal(polar_image)
    mask[mask == 100] = 0
#    vig_corr=np.multiply(gray_ar,mask)
    vig_corrRGB[:,:,0]=np.multiply(sq_ar[:,:,0],mask)
    vig_corrRGB[:,:,1]=np.multiply(sq_ar[:,:,1],mask)
    vig_corrRGB[:,:,2]=np.multiply(sq_ar[:,:,2],mask)
    vig_corrRGB = vig_corrRGB.astype(np.float32)
    return vig_corrRGB

def gen_tonemap(hdr_data):
    print("Tonemaping using Drago's method ... ")
    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
    tonemap = tonemapDrago.process(hdr_data)
    tonemap = 3 * tonemap
    print("saved tonemapped as JPG")
#    print("Tonemaping using Drago's method ... ")
#    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
#    ldrDrago = tonemapDrago.process(hdrDebevec)
#    ldrDrago = 3 * ldrDrago
#    print("saved ldr-Drago.jpg")
    return tonemap

def onTrackbarChange(trackbarValue):
    pass

def mouse_drawing(event, x, y, flags, params):
    global point1, point2, drawing, move, complt, ix, iy, dst, img, threshval, header, header_t        
    if complt is False:
        if event == cv2.EVENT_LBUTTONDOWN:
            if drawing is False:
                drawing = True
                point1 = (x, y)
                ix, iy = x, y
            else:
                drawing = False
        if event == cv2.EVENT_MOUSEMOVE:
            move = True  # 10May
            if drawing is True:
                rect = cv2.rectangle(img,(ix,iy),(x,y),(1,1,0),-1)
                dst= cv2.addWeighted(img,0.995,rect,0.000001,0)
                img=dst
        elif event == cv2.EVENT_LBUTTONUP:
            complt = True
            if drawing is True:
                if move is True: # 10May
                    drawing = False
                    point2 = (x, y)
                    img=ldrDrago.copy()
#                    cv2.createTrackbar('Luminance', 'Frame', 10, 3000, onTrackbarChange )
#                    cv2.createTrackbar('Accept', 'Frame', 0, 5, onTrackbarChange )
#                    cv2.createTrackbar('Threshold', 'Frame', 1000, 1500, onTrackbarChange )
                    rect = cv2.rectangle(img,(ix,iy),(x,y),(0,0,0),1)
                    dst= cv2.addWeighted(img,0.1,rect,0.01,0)
    elif event == cv2.EVENT_MBUTTONDOWN:
        global point3, re
        complt = False
        if re is False:
            img=ldrDrago.copy()

def dmnsns():
    dimn1 = screensize[1]/1.5 #IMPORTANT
    dimn2 = ldrDrago.shape[0]
    dimn3=ldrDrago.shape[1]
    newdimn=(int(dimn1), int(dimn1*dimn3/(dimn2)))
    return newdimn


def initls(ldr_im):
    dim1 = screensize[0]/2
    dim2 = ldr_im.shape[1]
    dim3=ldr_im.shape[0]
    linthickval=int(screensize[0]/160)
    newdim=(int(dim1), int(dim1*dim3/(dim2)))
    print(newdim[0],newdim[1])
#    ldr_im=cv2.resize(ldr_im,(newdim[0],newdim[1]))
    spacer = np.ones((100,100,3))
    spacer=spacer.astype(np.uint8)
    spacer*=255
    img=ldr_im.copy()
    hdrDebevec_rs = hdrDebevec.copy()
    hdrDebevec_rs=cv2.resize(hdrDebevec_rs,(newdimn[0],newdimn[1]))
    drawing = False
    rectangle_bgr = (255, 255, 255)
    rectangle_bgr_header = (0, 0, 0)
    point1 = ()
    point2 = ()
    point3 = ()
    re = False
    move = False # 10May
    font = cv2.FONT_HERSHEY_TRIPLEX
    complt = False
    return linthickval,img, drawing, rectangle_bgr, rectangle_bgr_header, point1, point2, point3, re, move, font, complt, newdim, spacer, hdrDebevec_rs 

#def cvbox_bg():
#    if complt is False:
#        header_t = 'SELECT AREA OF INTEREST: CLICK MOUSE LEFT BUTTON AND DRAG'
#    else:
#        header_t = 'AREA SELECTED, MOVE SLIDER TO CALIBRATE WITH LUMINANCE VALUE'
#    threshval = cv2.getTrackbarPos('Luminance','Frame')+0.0000001
#    acceptval = cv2.getTrackbarPos('Accept','Frame')
#    header = '' + str(header_t)
#    (header_width, header_height) = cv2.getTextSize(header, font, fontScale=0.5, thickness=1)[0]
#    header_offset_x = int(img.shape[1]/2)-int(header_width/2)
#    header_offset_y = 25
#    box_coords2 = ((header_offset_x-35, header_offset_y+5), (header_offset_x + header_width + 35, header_offset_y - header_height - 5))
#    return header, threshval, acceptval, box_coords2, header_offset_x, header_offset_y

def cvbox_bg():
    if complt is False:
        header_t = 'SELECT AREA OF INTEREST: CLICK MOUSE LEFT BUTTON AND DRAG'
    else:
        header_t = 'AREA SELECTED, MOVE SLIDER TO CALIBRATE WITH LUMINANCE VALUE'
    luminval_data=ui.luminval_widget.text()
    if luminval_data == '':
        threshval=0.000001
    else:
        threshval=float(luminval_data)+0.000001
#    print (threshval)
#    threshval = cv2.getTrackbarPos('Luminance','Frame')+0.0000001
    acceptval = calibdone_val
#    acceptval = cv2.getTrackbarPos('Accept','Frame')
    header = '' + str(header_t)
    (header_width, header_height) = cv2.getTextSize(header, font, fontScale=0.35, thickness=1)[0]
    header_offset_x = int(img.shape[1]/2)-int(header_width/2)
    header_offset_y = 25
    box_coords2 = ((header_offset_x-35, header_offset_y+5), (header_offset_x + header_width + 35, header_offset_y - header_height - 5))
    return header, threshval, acceptval, box_coords2, header_offset_x, header_offset_y

def selection_box(selectionfile):
    valpoint = [0,0,0]
    valtotal = [0,0,0]
    valavg = [0,0,0]
    pavpoint1=[min(point1[0],point2[0]), min(point1[1],point2[1])]
    pavpoint2=[max(point1[0],point2[0]), max(point1[1],point2[1])]
    countvalavg=0.001
    for iavgg in range (pavpoint1[0], pavpoint2[0],1):
        for javgg in range (pavpoint1[1], pavpoint2[1],1):
            countvalavg=countvalavg+1
            for kavgg in range (0,3,1):
                valpoint[0]=hdrDebevec_rs[javgg,iavgg,0]
                valpoint[1]=hdrDebevec_rs[javgg,iavgg,1]
                valpoint[2]=hdrDebevec_rs[javgg,iavgg,2]
                # valpoint[kavgg]=hdrDebevec[iavgg,javgg,kavgg]
                valtotal[kavgg]=valtotal[kavgg]+valpoint[kavgg]
    valavg[0]=valtotal[0]/countvalavg
    valavg[1]=valtotal[1]/countvalavg
    valavg[2]=valtotal[2]/countvalavg
    vallum=0.2989*valavg[0]+ 0.5870*valavg[1]+ 0.1140*valavg[2]
    calibd=float(vallum/threshval+0.0000001)
    text = '[' + str(format(vallum, '.2f')) +']'+ '<'+ str(int(threshval))+ '> Lum Ratio is 1:'+str(format(calibd,'.3f'))
    (text_width, text_height) = cv2.getTextSize(text, font, fontScale=0.5, thickness=1)[0]
    text_offset_x = img.shape[1]-text_width-10
    text_offset_y = img.shape[0] - 10
    box_coords = ((text_offset_x-5, text_offset_y+5), (text_offset_x + text_width + 5, text_offset_y - text_height - 5))
    return box_coords, vallum, text, text_offset_x, text_offset_y

def lum_calib():
    calibd=float(vallum/(threshval+0.0001))
    hdr2lumin=np.divide(hdrDebevec,calibd)
    hdr2lumin4circ=hdr2lumin.copy()
    hdr2lumin4circ=cv2.resize(hdr2lumin4circ,(newdimn[0],newdimn[1]))
    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
    ldrDrago_mod=3*tonemapDrago.process(hdr2lumin)
    ldrDrago_mod=np.divide(ldrDrago_mod,calibd)
    ldrDrago_mod=cv2.resize(ldrDrago_mod,(newdimn[0],newdimn[1]))  # IMPORTANT
    ldrDrago_bal=ldrDrago_mod.copy()
    ldrDrago_bal2=ldrDrago_bal.copy()
    ldrDrago_bal *= 15  #IMPORTANT
    ldrDrago_bal2 *= 5
    ldrDrago_mod_uint8b = ldrDrago_bal2.astype(np.uint8)
    ldrDrago_mod_uint8 = ldrDrago_bal.astype(np.uint8)
    ldrDrago_show=ldrDrago_mod_uint8.copy()
    grayblur = cv2.cvtColor(ldrDrago_bal, cv2.COLOR_BGR2GRAY)
    grayblur = cv2.GaussianBlur(grayblur, (41, 41), 0)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(grayblur)
    cntimage = hdr2lumin4circ.copy() 
    cntgray1 = cv2.cvtColor(cntimage, cv2.COLOR_BGR2GRAY)
#    wval=np.amax(cntgray1)
    wratio= 1  #float(255/wval)
    cntgray = cntgray1*wratio
    cntblurred = cv2.GaussianBlur(cntgray, (11, 11), 0)
#    threshold_val = cv2.getTrackbarPos('Threshold','Frame')
    threshold_val=ui.threshval_widget.text()
    threshold_val=float(threshold_val)
#    threshold_val = float(ui.threshval_widget.text())
    cntthresh = cv2.threshold(cntblurred, threshold_val, 20000, cv2.THRESH_BINARY)[1]
    cntthresh = cv2.erode(cntthresh, None, iterations=2)
    cntthresh = cv2.dilate(cntthresh, None, iterations=4)
    cntlabels = measure.label(cntthresh, neighbors=8, background=0)
    cntmask = np.zeros(cntthresh.shape, dtype="uint8")
    for cntlabel in np.unique(cntlabels):
    	if cntlabel == 0:
    		continue
    	cntlabelMask = np.zeros(cntthresh.shape, dtype="uint8")
    	cntlabelMask[cntlabels == cntlabel] = 20000
    	cntnumPixels = cv2.countNonZero(cntlabelMask)
    	if cntnumPixels > 300:
    		cntmask = cv2.add(cntmask, cntlabelMask)
    cnts = cv2.findContours(cntmask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    if cnts!= []:
        cnts = contours.sort_contours(cnts)[0]
    ldrDrago_mod_c1 = cv2.applyColorMap(ldrDrago_mod_uint8, cmapy.cmap('Greys_r'))
    ldrDrago_mod_c2 = cv2.applyColorMap(ldrDrago_mod_uint8b, cmapy.cmap('seismic'))
    ldrDrago_mod_c3 = cv2.applyColorMap(ldrDrago_mod_uint8, cmapy.cmap('seismic'))
    return cnts, ldrDrago_mod_c1, ldrDrago_mod_c2, ldrDrago_mod_c3, ldrDrago_mod_uint8, ldrDrago_mod_uint8b, ldrDrago_show, hdr2lumin

class Window (QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Wizard Step 1: Select LDR Images"
        self.top=screensize[0]/2 - 200
        self.left=screensize[1]/2 - 75
        self.width=400
        self.height=150
        self.setStyleSheet("background-color: rgb(140,206,245)")
        self.InitWindow()
    
    def InitWindow(self):
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint,False)
        self.ldrselect=QPushButton("Select LDR Images",self)
        self.ldrselect.setGeometry(25,55,150,40)
        self.ldrselect.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.ldrselect.clicked.connect(openFileDialog)
        self.contbtn=QPushButton("Continue Program",self)
        self.contbtn.setGeometry(225,55,150,40)
        self.contbtn.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.contbtn.clicked.connect(self.close)
        self.contbtn.hide()
        self.ldrselect.clicked.connect(self.contbtn.show)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()
        
class Window_displaymsg (QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Calculating Camera Response Function..."
        self.top=screensize[0]/2 - 200
        self.left=screensize[1]/2 - 75
        self.width=400
        self.height=150
        self.setStyleSheet("background-color: rgb(140,206,245)")
        self.InitWindow()
    
    def InitWindow(self):
#        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
#        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint,False)
        self.msg_widget = QtWidgets.QLabel(self)
#        self.msg_widget.setMinimumSize(QtCore.QSize(200, 50))
        self.msg_widget.setGeometry(50,15,300,50)
        self.msg_widget.setStyleSheet("font-size:12px; font-family:Arial;background-color:rgb(162, 226, 255); color:rgb(0,0,0)")
        self.msg_widget.setObjectName("msg_widget")
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
#        font.setBold(True)
#        font.setWeight(75)
        self.msg_widget.setFont(font)
        self.msg_widget.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignHCenter)
#        self.msg_widget.setObjectName("msg_widget")

#        self.ldrselect=QPushButton("Select LDR Images",self)
#        self.ldrselect.setGeometry(25,55,150,40)
#        self.ldrselect.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
#        self.ldrselect.clicked.connect(openFileDialog)
        self.contbtn=QPushButton("Continue Program",self)
        self.contbtn.setGeometry(225,105,150,40)
        self.contbtn.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.contbtn.clicked.connect(self.close)
#        self.contbtn.hide()
#        self.ldrselect.clicked.connect(self.contbtn.show)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()
        

class Ui_MenuWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(665, 649)
        MainWindow.setStyleSheet("background-color: rgb(115, 168, 230)")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.luminvalslider_widget = QtWidgets.QSlider(self.centralwidget)
        self.luminvalslider_widget.setMaximum(4000)
        self.luminvalslider_widget.setOrientation(QtCore.Qt.Horizontal)
        self.luminvalslider_widget.setObjectName("luminvalslider_widget")
        self.verticalLayout.addWidget(self.luminvalslider_widget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.luminval_widget = QtWidgets.QSpinBox(self.centralwidget)
        self.luminval_widget.setMinimumSize(QtCore.QSize(120, 0))
        self.luminval_widget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(64, 94, 128); color:rgb(255,255,255)")
        self.luminval_widget.setMaximum(4000)
        self.luminval_widget.setObjectName("luminval_widget")
        self.horizontalLayout.addWidget(self.luminval_widget)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addLayout(self.verticalLayout)
        self.line_3 = QtWidgets.QFrame(self.centralwidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.horizontalLayout_3.addWidget(self.line_3)
        self.textdescription_widget = QtWidgets.QLabel(self.centralwidget)
        self.textdescription_widget.setMinimumSize(QtCore.QSize(150, 0))
        self.textdescription_widget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(64, 94, 128); color:rgb(255,255,255)")
        self.textdescription_widget.setFrameShape(QtWidgets.QFrame.Panel)
        self.textdescription_widget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.textdescription_widget.setLineWidth(2)
        self.textdescription_widget.setText("")
        self.textdescription_widget.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.textdescription_widget.setObjectName("textdescription_widget")
        self.horizontalLayout_3.addWidget(self.textdescription_widget)
        self.line = QtWidgets.QFrame(self.centralwidget)
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout_3.addWidget(self.line)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.pushButton_calib_widget = QtWidgets.QPushButton(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.pushButton_calib_widget.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(-1)
        self.pushButton_calib_widget.setFont(font)
        self.pushButton_calib_widget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.pushButton_calib_widget.setObjectName("pushButton_calib_widget")
        self.pushButton_calib_widget.clicked.connect(calib_done)
        self.verticalLayout_3.addWidget(self.pushButton_calib_widget)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.pushButton_launch_widget = QtWidgets.QPushButton(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(38, 56, 76))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.pushButton_launch_widget.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(-1)
        self.pushButton_launch_widget.setFont(font)
        self.pushButton_launch_widget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.pushButton_launch_widget.setObjectName("pushButton_launch_widget")
        self.pushButton_launch_widget.clicked.connect(launch_done)
        self.verticalLayout_3.addWidget(self.pushButton_launch_widget)
        self.horizontalLayout_3.addLayout(self.verticalLayout_3)
        self.line_2 = QtWidgets.QFrame(self.centralwidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.VLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.horizontalLayout_3.addWidget(self.line_2)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 247, 247))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 160, 160))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 247, 247))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 247, 247))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 160, 160))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 247, 247))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.ToolTipText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Button, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Light, brush)
        brush = QtGui.QBrush(QtGui.QColor(247, 247, 247))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Midlight, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Dark, brush)
        brush = QtGui.QBrush(QtGui.QColor(160, 160, 160))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Mid, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Text, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.BrightText, brush)
        brush = QtGui.QBrush(QtGui.QColor(120, 120, 120))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(115, 168, 230))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Shadow, brush)
        brush = QtGui.QBrush(QtGui.QColor(240, 240, 240))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.AlternateBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 220))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipBase, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.ToolTipText, brush)
        self.label_4.setPalette(palette)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setAutoFillBackground(False)
        self.label_4.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignHCenter)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_4.addWidget(self.label_4)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem3)
        self.threshdial_widget = QtWidgets.QDial(self.centralwidget)
        self.threshdial_widget.setMaximum(5000)
        self.threshdial_widget.setSingleStep(1)
        self.threshdial_widget.setProperty("value", 1000)
        self.threshdial_widget.setObjectName("threshdial_widget")
        self.horizontalLayout_2.addWidget(self.threshdial_widget)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.threshval_widget = QtWidgets.QSpinBox(self.centralwidget)
        self.threshval_widget.setMinimumSize(QtCore.QSize(60, 0))
        self.threshval_widget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(64, 94, 128); color:rgb(255,255,255)")
        self.threshval_widget.setMaximum(5000)
        self.threshval_widget.setProperty("value", 1000)
        self.threshval_widget.setObjectName("threshval_widget")
        self.verticalLayout_2.addWidget(self.threshval_widget)
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem4)
        self.horizontalLayout_2.addLayout(self.verticalLayout_2)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.addLayout(self.verticalLayout_4)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.cvimgholder_widget = QtWidgets.QLabel(self.centralwidget)
        self.cvimgholder_widget.setMinimumSize(QtCore.QSize(0, 500))
        self.cvimgholder_widget.setAutoFillBackground(False)
        self.cvimgholder_widget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(255,255,255); color:rgb(0,0,0)")
        self.cvimgholder_widget.setFrameShape(QtWidgets.QFrame.Panel)
        self.cvimgholder_widget.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.cvimgholder_widget.setText("")
        self.cvimgholder_widget.setAlignment(QtCore.Qt.AlignCenter)
        self.cvimgholder_widget.setObjectName("cvimgholder_widget")
        self.verticalLayout_5.addWidget(self.cvimgholder_widget)
        self.gridLayout.addLayout(self.verticalLayout_5, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 665, 21))
        self.menubar.setStyleSheet("background-color: rgb(125, 178, 240)")
        self.menubar.setObjectName("menubar")
        self.menuMenu1 = QtWidgets.QMenu(self.menubar)
        self.menuMenu1.setObjectName("menuMenu1")
        self.menuMenu2 = QtWidgets.QMenu(self.menubar)
        self.menuMenu2.setObjectName("menuMenu2")
        self.menuMenu3 = QtWidgets.QMenu(self.menubar)
        self.menuMenu3.setObjectName("menuMenu3")
        self.menuMenu4 = QtWidgets.QMenu(self.menubar)
        self.menuMenu4.setObjectName("menuMenu4")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionMenu1a = QtWidgets.QAction(MainWindow)
        self.actionMenu1a.setObjectName("actionMenu1a")
        self.actionMenu1a.triggered.connect(crf_plot)
        self.actionMenu1b = QtWidgets.QAction(MainWindow)
        self.actionMenu1b.setObjectName("actionMenu1b")
        self.actionMenu1b.triggered.connect(histogram_plot)
        self.actionMenu2a = QtWidgets.QAction(MainWindow)
        self.actionMenu2a.setObjectName("actionMenu2a")
        self.actionMenu3a = QtWidgets.QAction(MainWindow)
        self.actionMenu3a.triggered.connect(save_hdr)
        self.actionMenu3a.setObjectName("actionMenu3a")
        self.actionMenu3b = QtWidgets.QAction(MainWindow)
        self.actionMenu3b.triggered.connect(save_falsecolor)
        self.actionMenu3b.setObjectName("actionMenu3b")
        self.actionMenu3c = QtWidgets.QAction(MainWindow)
        self.actionMenu3c.triggered.connect(save_numeric_csv)
        self.actionMenu3c.setObjectName("actionMenu3c")
        self.actionMenu4a = QtWidgets.QAction(MainWindow)
        self.actionMenu4a.setObjectName("actionMenu4a")
        self.actionMenu4b = QtWidgets.QAction(MainWindow)
        self.actionMenu4b.setObjectName("actionMenu4b")
        self.menuMenu1.addSeparator()
        self.menuMenu1.addAction(self.actionMenu1a)
        self.menuMenu1.addSeparator()
        self.menuMenu1.addAction(self.actionMenu1b)
        self.menuMenu2.addSeparator()
        self.menuMenu2.addAction(self.actionMenu2a)
        self.menuMenu2.addSeparator()
        self.menuMenu3.addSeparator()
        self.menuMenu3.addAction(self.actionMenu3a)
        self.menuMenu3.addSeparator()
        self.menuMenu3.addAction(self.actionMenu3b)
        self.menuMenu3.addSeparator()
        self.menuMenu3.addAction(self.actionMenu3c)
        self.menuMenu4.addSeparator()
        self.menuMenu4.addAction(self.actionMenu4a)
        self.menuMenu4.addSeparator()
        self.menuMenu4.addAction(self.actionMenu4b)
        self.menubar.addAction(self.menuMenu1.menuAction())
        self.menubar.addAction(self.menuMenu2.menuAction())
        self.menubar.addAction(self.menuMenu3.menuAction())
        self.menubar.addAction(self.menuMenu4.menuAction())

        self.retranslateUi(MainWindow)
        self.luminvalslider_widget.valueChanged['int'].connect(self.luminval_widget.setValue)
        self.luminval_widget.valueChanged['int'].connect(self.luminvalslider_widget.setValue)
        self.threshdial_widget.valueChanged['int'].connect(self.threshval_widget.setValue)
        self.threshval_widget.valueChanged['int'].connect(self.threshdial_widget.setValue)
        self.luminvalslider_widget.valueChanged['int'].connect(calib_done)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Wizard Step 2: Make adjustments"))
        self.label_2.setText(_translate("MainWindow", "Enter Luminance Calibration"))
        self.label.setText(_translate("MainWindow", "Cd/m2"))
        self.pushButton_calib_widget.setText(_translate("MainWindow", "Calibration Complete"))
        self.pushButton_launch_widget.setText(_translate("MainWindow", "Save Falsecolor Image"))
        self.label_4.setText(_translate("MainWindow", "Adjust Threshold"))
        self.label_3.setText(_translate("MainWindow", "Cd/m2"))
        self.menuMenu1.setTitle(_translate("MainWindow", "Analysis"))
        self.menuMenu2.setTitle(_translate("MainWindow", "Unused"))
        self.menuMenu3.setTitle(_translate("MainWindow", "Save Output"))
        self.menuMenu4.setTitle(_translate("MainWindow", "Unused"))
        self.actionMenu1a.setText(_translate("MainWindow", "Show CRF"))
        self.actionMenu1b.setText(_translate("MainWindow", "Show Histogram"))
        self.actionMenu2a.setText(_translate("MainWindow", "Menu2a"))
        self.actionMenu3a.setText(_translate("MainWindow", "Save HDR"))
        self.actionMenu3b.setText(_translate("MainWindow", "Save Falsecolor"))
        self.actionMenu3c.setText(_translate("MainWindow", "Extract Numeric HDR Data"))
        self.actionMenu4a.setText(_translate("MainWindow", "Menu4a"))
        self.actionMenu4b.setText(_translate("MainWindow", "Menu4b"))


def calib_done():
    global calibdone_val
    calibdone_val = True
    return calibdone_val

def save_falsecolor():
#    cv2.imwrite("Image.hdr", hdrDebevec)
#    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
#    tonemap = tonemapDrago.process(hdrDebevec)
#    tonemap = 3 * tonemap
#    cv2.imwrite("ToneMap.jpg", tonemap * 255)
    plt.clf
    plt.axis('off')
    ldrDrago_show_gray=rgb2gray(ldrDrago_show)
    plt.imshow(ldrDrago_show_gray, cmap=plt.get_cmap('seismic'))
    plt.colorbar()
    plt.savefig('Falsecolor.jpg',dpi=1200)
    plt.close()
#    print ("ooh yeah")
#    launchdone_val = 1
#    return launchdone_val

def save_numeric_csv():
    hdrDebevec_gray=rgb2gray(hdrDebevec)
    hdrDebevec_gray2=cv2.resize(hdrDebevec_gray,(300,300))
    HDRfilename = datetime.datetime.now().strftime("HDR-%Y-%m-%d-%H-%M.csv")
    np.savetxt(HDRfilename, hdrDebevec_gray2, delimiter=",")

def save_hdr():
    cv2.imwrite("HDRImage.hdr", hdrDebevec)
#    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
#    tonemap = tonemapDrago.process(hdrDebevec)
#    tonemap = 3 * tonemap
#    cv2.imwrite("ToneMap.jpg", tonemap * 255)
#    plt.axis('off')
#    plt.imshow(vig_corrRGB[:,:,2], cmap=plt.get_cmap('plasma'))
#    plt.colorbar()
#    plt.savefig('legend_fc.jpg',dpi=1200)
#    print ("ooh yeah")
#    launchdone_val = 1
#    return launchdone_val

def launch_done():
    cv2.imwrite("Image.hdr", hdrDebevec)
    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
    tonemap = tonemapDrago.process(hdrDebevec)
    tonemap = 3 * tonemap
    cv2.imwrite("ToneMap.jpg", tonemap * 255)
    plt.axis('off')
    plt.imshow(vig_corrRGB[:,:,2], cmap=plt.get_cmap('plasma'))
    plt.colorbar()
    plt.savefig('legend_fc.jpg',dpi=1200)
    print ("ooh yeah")
#    launchdone_val = 1
#    return launchdone_val
    
def crf_plot(self):
    mplott = Canvas()
    mplott.show()
    
class Canvas(QDialog):
    def __init__(self, parent=None):
        super(Canvas, self).__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.button = QPushButton('Display Camera Response Function')
        self.button.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.button.clicked.connect(self.plot)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgb(140,206,245)")
        self.setWindowTitle("Camera Response Function")

    def plot(self):
        data_Blue = [Camera_response[i,0,0] for i in range(255)]
        data_Green = [Camera_response[i,0,1] for i in range(255)]
        data_Red = [Camera_response[i,0,2] for i in range(255)]
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.plot(data_Blue,c='b',marker="^",ls='--',label='Blue',fillstyle='none')
        ax.plot(data_Green,c='g',marker="^",ls='--',label='Green',fillstyle='none')
        ax.plot(data_Red, c='r',marker="^",ls='--',label='Red',fillstyle='none')
        plt.legend(loc=2)
        self.canvas.draw()
        
def histogram_plot(self):
    mplott = Canvas_histogram()
    mplott.show()
    
class Canvas_histogram(QDialog):
    def __init__(self, parent=None):
        global img_num
        super(Canvas_histogram, self).__init__(parent)
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.button = QPushButton('Display Histogram of Select Image')
        self.button.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(38,56,76); color:rgb(255,255,255)")
        self.imgnum_hist = QtWidgets.QSpinBox()
        self.imgnum_hist.setMinimum(0)
        self.imgnum_hist.setMaximum(14)
        self.imgnum_hist.setValue(7)
#        self.imgnum_hist.setOrientation(QtCore.Qt.Horizontal)
        self.imgnum_hist.setObjectName("imgnum_hist")
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.imgnum_hist)
        layout.addWidget(self.button)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setStyleSheet("background-color: rgb(140,206,245)")
        self.setWindowTitle("Histogram for Source Images")
        img_num=self.imgnum_hist.text()
        self.button.clicked.connect(self.plot_hist)
        self.imgnum_hist.valueChanged['int'].connect(self.plot_hist)

    def plot_hist(self):
        img_num=self.imgnum_hist.text()
        ival_hist=img_num
        if ival_hist=='':
            ival_hist=0
        else:
            ival_hist=int(ival_hist)
        self.figure.clear()
        data_Blue = cv2.calcHist([images[ival_hist]],[0],None,[256],[0,256])
        data_Green = cv2.calcHist([images[ival_hist]],[1],None,[256],[0,256])
        data_Red = cv2.calcHist([images[ival_hist]],[2],None,[256],[0,256])
        ax = self.figure.add_subplot(111)
        ax.plot(data_Blue,c='b',marker="o",ls='--',label='Blue',fillstyle='none')
        ax.plot(data_Green,c='g',marker="*",ls='--',label='Green',fillstyle='none')
        ax.plot(data_Red, c='r',marker="^",ls='--',label='Red',fillstyle='none')
        plt.legend(loc=2)
        self.canvas.draw()


#    def plot_hist(self):
#        img_num=self.imgnum_hist.text()
#        ival_hist=img_num
#        if ival_hist=='':
#            ival_hist=0
#        else:
#            ival_hist=int(ival_hist)
#        color = ('b','g','r')
#        for i,col in enumerate(color):
#            histr = cv2.calcHist([images[ival_hist]],[i],None,[256],[0,256])
#            plt.plot(histr,color = col)
#            plt.xlim([0,256])
#        plt.show()
#        self.canvas.draw()   


if __name__=='__main__':
#    global vconcat
    app=QApplication(sys.argv)
    window=Window()
    app.exec_()
    del app
    app_display=QApplication(sys.argv)
    window_msg=Window_displaymsg()
    window_msg.setWindowTitle("Aligning images ...")
    print("Aligning images ... ")
#    crop_ratio = int(input("Define Crop Area in Percentage (0-100) and press ENTER:   "))
    crop_ratio = 85
    len_imgs= int(len(images[0]))
    wid_imgs= int(len(images[0][1]))
    if len_imgs>wid_imgs:
        minsize_l=wid_imgs
        maxsize_l=len_imgs
    else:
        minsize_l=len_imgs
        maxsize_l=wid_imgs
    lenwid_imgs_new= int(minsize_l*crop_ratio/100)
#    print(lenwid_imgs_new)
    startval_long=int((maxsize_l-lenwid_imgs_new)/2)
    startval_short=int((minsize_l-lenwid_imgs_new)/2)
    images_new=images.copy()
    for imgn in range (0, len(images),1):
        images_new[imgn]=cv2.resize(images_new[imgn],(lenwid_imgs_new,lenwid_imgs_new))
        for pxl1 in range (0,lenwid_imgs_new,1):
            for pxl2 in range (0,lenwid_imgs_new,1):
                if len_imgs>wid_imgs:  
                    images_new[imgn][pxl1,pxl2,:]=images[imgn][startval_long+pxl1,startval_short+pxl2,:]
                else:
                    images_new[imgn][pxl2,pxl1,:]=images[imgn][startval_short+pxl2,startval_long+pxl1,:]
    images=images_new
        
    align = cv2.createAlignMTB()
    align.process(images, images)
    window_msg.setWindowTitle("Calculating Camera Response Function ...")
    print("Calculating Camera Response Function (CRF) ... ")
    calibrate = cv2.createCalibrateDebevec()
    Camera_response = calibrate.process(images, times)
    window_msg.setWindowTitle("Merging images into one HDR image ... ")
    print("Merging images into one HDR image ... ")
    mergeDebevec = cv2.createMergeDebevec()
    hdrDebevec = mergeDebevec.process(images, times, Camera_response)
    hdrDebevec2=hdrDebevec.copy()
    window_msg.msg_widget.setText("All good to go. \u00a9 Marshal Maskarenj, 2019")
    print("saved hdrDebevec.hdr ")
    window_msg.setWindowTitle("Images Aligned and HDR Generated... Proceed")
#    print(hdrDebevec.shape)
    app_display.exec_()
    del app_display 
    sq_ar, minsize=sqar_gen(hdrDebevec)
    gray_ar = rgb2gray(sq_ar)
    vig_corrRGB=vignette(minsize)
    ldrDrago_corr=gen_tonemap(vig_corrRGB)
    hdrDebevec=vig_corrRGB.copy()    # IMPORTANT
    hdrDebevec = np.float32(hdrDebevec)
    ldrDrago=gen_tonemap(hdrDebevec)
    newdimn=dmnsns()
    ldrDrago=cv2.resize(ldrDrago,(newdimn[0],newdimn[1]))
    linthickval,img, drawing, rectangle_bgr, rectangle_bgr_header, point1, point2, point3, re, move, font, complt, newdim, spacer, hdrDebevec_rs = initls(ldrDrago)
#    img=cv2.resize(img,(newdim[0],newdim[1]))
    cv2.namedWindow("Frame")
    cv2.setMouseCallback("Frame", mouse_drawing)
    app2 = QtWidgets.QApplication(sys.argv)
    MenuWindow = QtWidgets.QMainWindow()
    ui = Ui_MenuWindow()
    ui.setupUi(MenuWindow)
#    Form.show()
    calibdone_val=False 
    while True:
        header, threshval, acceptval, box_coords2, header_offset_x, header_offset_y = cvbox_bg()
        cv2.rectangle(img, box_coords2[0], box_coords2[1], rectangle_bgr_header, cv2.FILLED)
        cv2.putText(img, header, (header_offset_x, header_offset_y), font, 0.35, (0, 1, 1), 1, cv2.LINE_AA)
        if point1 and point2:
            MenuWindow.show()
            box_coords, vallum, text, text_offset_x, text_offset_y=selection_box(hdrDebevec)
            cv2.rectangle(img, box_coords[0], box_coords[1], rectangle_bgr, cv2.FILLED)
            cv2.putText(img, text, (text_offset_x, text_offset_y), font, 0.5, (1, 0, 0), 1, cv2.LINE_AA)
            ui.textdescription_widget.setText(text)
#        img=cv2.resize(img,(newdim[0],newdim[1]))
        cv2.imshow("Frame", img)
        if acceptval==True:
            cnts, ldrDrago_mod_c1, ldrDrago_mod_c2, ldrDrago_mod_c3, ldrDrago_mod_uint8, ldrDrago_mod_uint8b, ldrDrago_show, hdr2lumin = lum_calib()
            for (i, c) in enumerate(cnts):
            	(x, y, w, h) = cv2.boundingRect(c)
            	((cX, cY), radius) = cv2.minEnclosingCircle(c)
            	cv2.circle(ldrDrago_show, (int(cX), int(cY)), int(radius),(0, 0, 0), 1)
            	cv2.putText(ldrDrago_show, "{}".format(i + 1), (x+5, y+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
            spc1=spacer.copy()
            spc2=cv2.resize(spc1,(ldrDrago_mod_c1.shape[0],linthickval))
            hconcat = np.concatenate((ldrDrago_mod_c1, spc2, ldrDrago_mod_c2, spc2, ldrDrago_mod_c3), axis=0)
            hconcat=cv2.resize(hconcat,(int(hconcat.shape[1]/3),int((hconcat.shape[0]-2*spc2.shape[0])/3)))
            spc3=cv2.resize(spc1,(int(linthickval/3),ldrDrago_mod_c1.shape[1]))
            vconcat= np.concatenate((ldrDrago_show, spc3, hconcat), axis=1)
            vconcat=cv2.resize(vconcat,(int(vconcat.shape[1]/1.2),int(vconcat.shape[0]/1.2)))
#            hdr2lumval=0.2989*hdr2lumin[:,:,0]+ 0.5870*hdr2lumin[:,:,1]+ 0.1140*hdr2lumin[:,:,2]
            cv_height, cv_width, cv_channel = vconcat.shape
            bytesPerLine = 3 * cv_width
            vconcatimg = QtGui.QImage(vconcat.data, cv_width, cv_height, bytesPerLine, QtGui.QImage.Format_RGB888)
            ui.cvimgholder_widget.setPixmap(QtGui.QPixmap(vconcatimg))
#            return vconcat
            
        key = cv2.waitKey(1)
        if key == 27:
            break
    cv2.destroyAllWindows()
    app2.exec_()
    del app2
        