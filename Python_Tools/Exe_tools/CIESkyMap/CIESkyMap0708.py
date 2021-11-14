# -*- coding: utf-8 -*-
"""
@author: marshal.maskarenj
"""

import math
#import csv
import sympy as sp
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from matplotlib.mlab import griddata
import scipy.interpolate as inter
import pandas as pd
import cv2
from pylab import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QTextEdit, QDialog, QVBoxLayout
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import ctypes
import sys
from PIL import Image
from mpl_toolkits.mplot3d import Axes3D

def initial_defs():
    global lcount, daynum, skytype, resolution
#    phideg=19
    phideg=skymodel.lat_val_skym.value()
    phi = math.radians(phideg)
    tt=float(lcount)  # tt=float(7 + 0.25*lcount)
    Dv=1
    Date='19 May'
    Date=str(daynum)
    tme=tt
    Header=str(Date)+'--'+str(tme)
    omega=(15*(tt-12.))
    omegarad = math.radians(omega)  # Hour Angle in Radians
    delta = 23.45 * math.sin(math.radians((360. / 365) * (284 + daynum)))  # declination angle in Degrees
    deltarad = math.radians(delta)  # declination angle in Radians
    thetaz = math.acos((math.sin(phi) * math.sin(deltarad)) + (math.cos(phi) * math.cos(deltarad) * math.cos(omegarad)))  # Solar Zenith Angle in Radians
    gammasvar = ((math.cos(thetaz) * math.sin(phi)) - (math.sin(deltarad))) / (math.sin(thetaz) * math.cos(phi))  # Solar Azimuth Angle in Radians
    if gammasvar > 1:
        gammasvar = 1
    if gammasvar < -1:
        gammasvar = -1
    gammas = math.acos(gammasvar)
    thetazdeg = math.degrees(thetaz)
    alphaAdeg = 90 - thetazdeg  # Solar Altitude
    gammasdeg = math.degrees(gammas)  # Solar Azimuth
    if omega<0:
        gammasdegmod = 180 - gammasdeg
    else:
        gammasdegmod = 180 + gammasdeg
    alpsdeg=gammasdegmod  # equalizing azimuth variables in two equations
    Zsdeg=90-alphaAdeg  # equalizing azimuth variables in two equations
    Zs = math.radians(Zsdeg)
    alps = math.radians(alpsdeg)
    return alps, Zs, skytype, Dv, Header, resolution

def zenval():
    alps, Zs, skytype, Dv, Header, resolution= initial_defs()
    a,b,c,d,e = coeff_map(skytype)
    stepcount=int(90/(resolution))
    val = np.zeros((90, 360))  # array to store the value of Ldes
    val_min = np.zeros((15, 20))
#    valpolar = np.zeros((181, 181))  # array to store the value of Ldes
    Lznet = np.zeros((90,360))
    for alpha in range(0, 360, stepcount):
        alp = math.radians(alpha)
        Az = abs(alp-alps)  # Azimuth difference
        for gamma in range(0, 90, stepcount):
            zen = 90-gamma
            Z = math.radians(zen)
            kappa = math.acos((math.cos(Zs)*math.cos(Z))+(math.sin(Zs)*math.sin(Z)*math.cos(Az)))  # Skypatch Sun Distance
            phyZ = 1+a*math.exp(b/math.cos(math.radians(Z)))
            phy0 = 1+a*math.exp(b)
            fkappa = 1+(c*(math.exp(d*kappa)-math.exp(d*(math.pi)/2)))+(e*(math.cos(kappa))**2)
            fZs = 1+(c*(math.exp(d*Zs)-math.exp(d*(math.pi)/2)))+(e*(math.cos(Zs))**2)
    
            Z, alp = sp.symbols("Z, alp")
            allpatch = sp.integrate((phyZ*sp.sin(Z)*sp.cos(Z)*fkappa), (Z,0,math.pi/2), (alp,0,2*math.pi))
            Lzinst=Dv*phy0*fZs/allpatch
            Lznet[gamma, alpha] = Lzinst
    Lzz=sum(Lznet) / float(len(Lznet))
    Lz = stepcount*stepcount*sum(Lzz)
#    print(Lz)
    Lztrunc=round(Lz, 2)
    if skymodel.timeday_val_skym.value()<5:
        skymodel.header_skym.setText(' ')
    elif skymodel.timeday_val_skym.value()>19:
        skymodel.header_skym.setText(' ')
    else:
        skymodel.header_skym.setText('Zenith Luminance is '+str(Lztrunc)+' cd/sqm')
    return val, val_min, Lz

def spread_arr():
    alps, Zs, skytype, Dv, Header, resolution = initial_defs()
    a,b,c,d,e = coeff_map(skytype)
    val, val_min, Lz = zenval()
    for alpha in range(0, 360, 1):
        alp = math.radians(alpha)
        Az = abs(alp-alps)  # Azimuth difference
        for gamma in range(0, 90, 1):
            zen = 90-gamma
            Z = math.radians(zen)
            kappa = math.acos((math.cos(Zs)*math.cos(Z))+(math.sin(Zs)*math.sin(Z)*math.cos(Az)))  # Skypatch Sun Distance
            phyZ = 1+a*math.exp(b/math.cos(math.radians(Z)))
            phy0 = 1+a*math.exp(b)
            fkappa = 1+(c*(math.exp(d*kappa)-math.exp(d*(math.pi)/2)))+(e*(math.cos(kappa))**2)
            fZs = 1+(c*(math.exp(d*Zs)-math.exp(d*(math.pi)/2)))+(e*(math.cos(Zs))**2)
            r_gradation = phyZ/phy0
            r_indicatrix = fkappa/fZs
            ratio = r_indicatrix*r_gradation
            Ldes = Lz * ratio
            val[gamma,alpha]=Ldes        
    Ldes = val
    return Ldes


def coeff_map(Set):
    if Set==1:
        a=4; b=-0.7; c=0; d=-1; e=0
    elif Set==2:
        a=4; b=-0.7; c=2; d=-1.5; e=0.15
    elif Set==3:
        a=1.1; b=-0.8; c=0; d=-1; e=0
    elif Set==4:
        a=1.1; b=-0.8; c=2; d=-1.5; e=0.15
    elif Set==5:
        a=0; b=-1; c=0; d=-1; e=0
    elif Set==6:
        a=0; b=-1; c=2; d=-1.5; e=0.15
    elif Set==7:
        a=0; b=-1; c=5; d=-2.5; e=0.3
    elif Set==8:
        a=0; b=-1; c=10; d=-3; e=0.45
    elif Set==9:
        a=-1; b=-0.55; c=2; d=-1.5; e=0.15
    elif Set==10:
        a=-1; b=-0.55; c=5; d=-2.5; e=0.3
    elif Set==11:
        a=-1; b=-0.55; c=10; d=-3; e=0.45
    elif Set==12:
        a=-1; b=-0.32; c=10; d=-3; e=0.45
    elif Set==13:
        a=-1; b=-0.32; c=16; d=-3; e=0.3
    elif Set==14:
        a=-1; b=-0.15; c=16; d=-3; e=0.3
    elif Set==15:
        a=-1; b=-0.15; c=24; d=-2.8; e=0.15
    else:
        a=0;b=0;c=0;d=0;e=0
    return a,b,c,d,e

def plot_skymap():
    global chdum, chosen_segment
    skymodel.ThreeDWin.hide()
    skymodel.plotter_skym.show()
    global lcount, daynum, skytype, resolution, corr_imgRGB, corr_img, corr_imgdum, corr_imgdum2, corr_imgdum3, corr_img_flat
    lcount2=skymodel.timeday_val_skym.value()
#    print (lcount2)
#        lcount2=4
    ival_hist=lcount2
    if ival_hist=='':
        ival_hist=0
    else:
        ival_hist=float(ival_hist)
    lcount=float(ival_hist)
    skymodel.plotter_skym.clear()
    daynum = skymodel.dayyear_val_skym.value()
    skytype = skymodel.skytype_val_skym.value()
    resolution = skymodel.res_val_skym.value()
    Ldes=spread_arr()
    img1 = Ldes.astype(np.float32)
    img2=cv2.resize(img1,(500,500))
    img3=np.rot90(img2)
    img4=np.rot90(img3)
    img=np.rot90(img4)
    value = np.sqrt(((img.shape[0]/2.0)**2.0)+((img.shape[1]/2.0)**2.0))   
    polar_image1 = cv2.linearPolar(img,(img.shape[0]/2, img.shape[1]/2), value, cv2.WARP_INVERSE_MAP)   
    polar_image2 = polar_image1.clip(min=0)
    polar_image3=np.rot90(polar_image2)
    polar_image4=np.fliplr(polar_image3)
    polar_image = np.where(polar_image4>1000, 0, polar_image4) 
    dimval=500
    val = np.zeros(shape=(dimval, dimval))  # array to store the value of Ldes
    for alpha in range(0, dimval, 1):
        for Z in range(0, dimval, 1):
            Ldes=1
            val[Z,alpha]=Ldes
    val=np.rot90(val)
    flat_mask = val.astype(np.float32)
    value_mask = np.sqrt(((flat_mask.shape[0]/2.0)**2.0)+((flat_mask.shape[1]/2.0)**2.0))
    polar_mask1 = cv2.linearPolar(flat_mask,(flat_mask.shape[0]/2, flat_mask.shape[1]/2), value_mask*0.7085, cv2.WARP_INVERSE_MAP)
    polar_mask2 = polar_mask1.clip(min=0)
    polar_mask = np.where(polar_mask2>3000, 0, polar_mask2)
    corr_img1=np.multiply(polar_image,polar_mask)
    corr_img=np.where(corr_img1>3000, 0, corr_img1)
#    corr_img=corr_img.astype(int)
#    CS = plt.imshow(corr_img, cmap='viridis')
#    CS.axes.get_xaxis().set_ticks([])
#    CS.axes.get_yaxis().set_ticks([])
#        CB = plt.colorbar(CS, shrink=0.8, extend='both')
    alps, Zs, skytype, Dv, Header, resolution = initial_defs()
#    plt.tight_layout()
#    plt.pad_inches = 0
    where_are_NaNs = np.isnan(corr_img)
    corr_img[where_are_NaNs] = 0
#    corr_img = corr_img.astype(np.uint8)
    corr_img=cv2.resize(corr_img,(400,400))
    corr_imgRGB=np.zeros((400, 400, 3))
    corr_imgRGB[:,:,0]=corr_img #cv2.cvtColor(corr_img,cv2.COLOR_GRAY2RGB)
    corr_imgRGB[:,:,1]=corr_img
    corr_imgRGB[:,:,2]=corr_img
    corr_imgRGB= corr_imgRGB.astype(np.uint16) # 25June IMPORTANT Identify how to limit to 255
    corr_imgdum=corr_imgRGB.copy()
#    tonemapDrago = cv2.createTonemapDrago(1.0, 0.7)
#    corr_imgRGB = np.float32(corr_imgRGB) 
#    corr_imgRGB=300*tonemapDrago.process(corr_imgRGB)
#    
#    info = np.iinfo(corr_imgRGB.dtype) # Get the information of the incoming image type
#    corr_imgRGB = corr_imgRGB.astype(np.float64) / info.max # normalize the data to 0 - 1
#    corr_imgRGB = 255 * corr_imgRGB # Now scale by 255
    
    maxdat=np.max(corr_imgRGB)
    corr_imgRGB=corr_imgRGB/(maxdat)
    corr_imgRGB= 255*corr_imgRGB
    
    corr_imgdum2=corr_imgRGB.copy()
    corr_imgRGB = corr_imgRGB.astype(np.uint8)  
    corr_imgdum3=corr_imgRGB.copy()
    import cmapy
    fcolor_index=skymodel.falsecolor_slide_skym.value()
    if fcolor_index==2:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('magma'))
        skymodel.falsecolor_label_skym.setText('Magma')
    elif fcolor_index==3:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('cividis'))
        skymodel.falsecolor_label_skym.setText('Cividis')
    elif fcolor_index==4:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('copper'))
        skymodel.falsecolor_label_skym.setText('Copper')
    elif fcolor_index==5:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('twilight_shifted'))
        skymodel.falsecolor_label_skym.setText('Twilight')
    elif fcolor_index==6:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('seismic'))
        skymodel.falsecolor_label_skym.setText('Seismic')
    elif fcolor_index==7:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('hsv'))
        skymodel.falsecolor_label_skym.setText('HSV')
    elif fcolor_index==8:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('Pastel1'))
        skymodel.falsecolor_label_skym.setText('Pastel1')
    else:
        corr_imgRGB=cv2.applyColorMap(corr_imgRGB, cmapy.cmap('viridis'))
        skymodel.falsecolor_label_skym.setText('False Color')
        
    corr_imgRGB=cv2.cvtColor(corr_imgRGB,cv2.COLOR_RGB2BGR)
#    corr_imgRGB_uint = corr_imgRGB.astype(np.uint8)
#    corr_imgRGB_uint=cv2.resize(corr_imgRGB_uint,(400,400))
    cv_height, cv_width, cv_channel = corr_imgRGB.shape
    bytesPerLine = 3*cv_width
    corr_imgRGBimg = QtGui.QImage(corr_imgRGB.data, cv_width, cv_height, bytesPerLine, QtGui.QImage.Format_RGB888)
    skymodel.plotter_skym.setPixmap(QtGui.QPixmap(corr_imgRGBimg))
    if skymodel.hselect_spot_skym.value()<2:
        selectY=16
    elif skymodel.hselect_spot_skym.value()>38:
        selectY=384
    else:
        selectY=10*skymodel.hselect_spot_skym.value()
    if skymodel.vselect_spot_skym.value()<2:
        selectX=16
    elif skymodel.vselect_spot_skym.value()>38:
        selectX=384
    else:
        selectX=10*skymodel.vselect_spot_skym.value()

#        selectY=10*skymodel.vselect_spot_skym.value()


#    selminX=selectX-10
#    selmaxX=selectX+10
#    selminY=selectY-10
#    selmaxY=selectY+10
    chosen_segment = np.zeros((30,30,3))
    for i in range (0,30,1):
        for j in range (0, 30, 1):
            for k in range (0,3,1):
                chosen_segment[i,j,k]=corr_imgRGB[selectX+i-15,selectY+j-15,k]
    chdum=chosen_segment.copy()
    chosen_segment=cv2.resize(chosen_segment,(31,31))
    chosen_segment=chosen_segment.astype(np.uint8)
    cvs_height, cvs_width, cvs_channel = chosen_segment.shape
    bytesPerLine_s = 3*cvs_width
    chosen_segment_img = QtGui.QImage(chosen_segment.data, cvs_width, cvs_height, bytesPerLine_s, QtGui.QImage.Format_RGB888)
    skymodel.spot_skym.setPixmap(QtGui.QPixmap(chosen_segment_img))

    
def plot_sky3d():
    skymodel.header_skym.setText('Try rotating the 3D plot!')
    skymodel.plotter_skym.hide()
    skymodel.ThreeDWin.show()
    corr_img_flat=cv2.cvtColor(corr_imgdum3,cv2.COLOR_RGB2GRAY)
    corr_img_flat=cv2.resize(corr_img_flat,(100,100))
    x=np.arange(0,corr_img_flat.shape[0],1)
    y=np.arange(0,corr_img_flat.shape[1],1)
    xs,ys=np.meshgrid(x,y)
#    fig=plt.figure()
#    ax=Axes3D(fig)
#    ax.plot_surface(xs,ys,corr_imgdum3,rstride=1, cstride=1, cmap='viridis')
#    ax.imshow(corr_img)
    skymodel.ThreeDWin.DrawGraph(xs,ys,corr_img_flat)
    skymodel.res_val_skym.setValue(1)


class ThreeDSurface_GraphWindow(FigureCanvas): #Class for 3D window
    def __init__(self):
        self.fig =plt.figure(figsize=(7,7))
        FigureCanvas.__init__(self, self.fig) #creating FigureCanvas
        self.axes = self.fig.gca(projection='3d')#generates 3D Axes object
        self.setWindowTitle("Main") # sets Window title
        self.fig.subplots_adjust(top=1.25, bottom=-0.25, left=-0.25, right=1.25, wspace=0)


    def DrawGraph(self, x, y, z):#Fun for Graph plotting
        self.axes.clear()
        fcolor_index=skymodel.falsecolor_slide_skym.value()
        if fcolor_index==2:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='magma') #plots the 3D surface plot
        elif fcolor_index==3:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='cividis') #plots the 3D surface plot
        elif fcolor_index==4:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='copper') #plots the 3D surface plot
        elif fcolor_index==5:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='twilight_shifted') #plots the 3D surface plot
        elif fcolor_index==6:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='seismic') #plots the 3D surface plot
        elif fcolor_index==7:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='hsv') #plots the 3D surface plot
        elif fcolor_index==8:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='Pastel1') #plots the 3D surface plot
        else:
            self.axes.plot_surface(x, y, z, rstride=1, cstride=1, cmap='viridis') #plots the 3D surface plot
        self.axes.xaxis.set_ticklabels([])
        self.axes.yaxis.set_ticklabels([])
        self.axes.zaxis.set_ticklabels([])
        self.axes.set_xticks([]) 
        self.axes.set_yticks([]) 
        self.axes.set_zticks([])
        self.axes.axis('off')
#        self.axes.w_xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
#        self.axes.w_yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
#        self.axes.w_zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        self.draw()



class skymodel_widget(object):
    def setupUi(self, widget):
        widget.setObjectName("widget")
        widget.resize(586, 466)
        widget.setStyleSheet("background-color: rgb(128, 187, 255)")
        self.gridLayout = QtWidgets.QGridLayout(widget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.line_14 = QtWidgets.QFrame(widget)
        self.line_14.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_14.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_14.setObjectName("line_14")
        self.verticalLayout_7.addWidget(self.line_14)
        self.falsecolor_label_skym = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.falsecolor_label_skym.setFont(font)
        self.falsecolor_label_skym.setObjectName("falsecolor_label_skym")
        self.verticalLayout_7.addWidget(self.falsecolor_label_skym)
        self.falsecolor_slide_skym = QtWidgets.QSlider(widget)
        self.falsecolor_slide_skym.setOrientation(QtCore.Qt.Horizontal)
        self.falsecolor_slide_skym.setObjectName("falsecolor_slide_skym")
        self.falsecolor_slide_skym.setMinimum(1)
        self.falsecolor_slide_skym.setMaximum(8)
        self.falsecolor_slide_skym.setSingleStep(1)
        self.falsecolor_slide_skym.setStyleSheet("QSlider::groove:horizontal {\n border: 1px solid #999999;\n height: 8px;\n background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A2533, stop:1 #405E80);\n margin: 1px 0;\n}\n\n"
                                        "QSlider::handle:horizontal {\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);\n border: 1px solid #403618;\n width: 18px;\n margin: -2px 0; \n border-radius: 3px;\n}")
        self.verticalLayout_7.addWidget(self.falsecolor_slide_skym)
        self.line_15 = QtWidgets.QFrame(widget)
        self.line_15.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_15.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_15.setObjectName("line_15")
        self.verticalLayout_7.addWidget(self.line_15)
        self.verticalLayout_3.addLayout(self.verticalLayout_7)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.line_13 = QtWidgets.QFrame(widget)
        self.line_13.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_13.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_13.setObjectName("line_13")
        self.verticalLayout_4.addWidget(self.line_13)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_2 = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("")
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.lat_val_skym = QtWidgets.QSpinBox(widget)
        self.lat_val_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.lat_val_skym.setMinimum(-85)
        self.lat_val_skym.setMaximum(85)
        self.lat_val_skym.setSingleStep(5)
        self.lat_val_skym.setProperty("value", 20)
        self.lat_val_skym.setObjectName("lat_val_skym")
        self.verticalLayout_5.addWidget(self.lat_val_skym)
        self.horizontalLayout_2.addLayout(self.verticalLayout_5)
        self.line_4 = QtWidgets.QFrame(widget)
        self.line_4.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_4.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_4.setObjectName("line_4")
        self.horizontalLayout_2.addWidget(self.line_4)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.line_11 = QtWidgets.QFrame(widget)
        self.line_11.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_11.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_11.setObjectName("line_11")
        self.horizontalLayout_2.addWidget(self.line_11)
        self.lat_slide_skym = QtWidgets.QSlider(widget)
        self.lat_slide_skym.setMinimum(-85)
        self.lat_slide_skym.setMaximum(85)
        self.lat_slide_skym.setSingleStep(5)
        self.lat_slide_skym.setProperty("value", 20)
        self.lat_slide_skym.setOrientation(QtCore.Qt.Vertical)
        self.lat_slide_skym.setObjectName("lat_slide_skym")
        self.horizontalLayout_2.addWidget(self.lat_slide_skym)
        self.verticalLayout_4.addLayout(self.horizontalLayout_2)
        self.line_12 = QtWidgets.QFrame(widget)
        self.line_12.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_12.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_12.setObjectName("line_12")
        self.verticalLayout_4.addWidget(self.line_12)
        self.verticalLayout_3.addLayout(self.verticalLayout_4)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem2)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.line_10 = QtWidgets.QFrame(widget)
        self.line_10.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_10.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_10.setObjectName("line_10")
        self.verticalLayout_2.addWidget(self.line_10)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setStyleSheet("")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.skytype_val_skym = QtWidgets.QSpinBox(widget)
        self.skytype_val_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.skytype_val_skym.setMinimum(1)
        self.skytype_val_skym.setMaximum(15)
        self.skytype_val_skym.setProperty("value", 8)
        self.skytype_val_skym.setObjectName("skytype_val_skym")
        self.verticalLayout.addWidget(self.skytype_val_skym)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.line = QtWidgets.QFrame(widget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.horizontalLayout.addWidget(self.line)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.skytype_slide_skym = QtWidgets.QSlider(widget)
        self.skytype_slide_skym.setMinimum(1)
        self.skytype_slide_skym.setMaximum(15)
        self.skytype_slide_skym.setProperty("value", 8)
        self.skytype_slide_skym.setOrientation(QtCore.Qt.Vertical)
        self.skytype_slide_skym.setObjectName("skytype_slide_skym")
        self.horizontalLayout.addWidget(self.skytype_slide_skym)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.line_2 = QtWidgets.QFrame(widget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.verticalLayout_2.addWidget(self.line_2)
        self.verticalLayout_3.addLayout(self.verticalLayout_2)
        spacerItem4 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem4)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.line_9 = QtWidgets.QFrame(widget)
        self.line_9.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_9.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_9.setObjectName("line_9")
        self.verticalLayout_8.addWidget(self.line_9)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_5 = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setStyleSheet("")
        self.label_5.setAlignment(QtCore.Qt.AlignCenter)
        self.label_5.setObjectName("label_5")
        self.verticalLayout_9.addWidget(self.label_5)
        self.dayyear_val_skym = QtWidgets.QSpinBox(widget)
        self.dayyear_val_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.dayyear_val_skym.setMinimum(1)
        self.dayyear_val_skym.setMaximum(365)
        self.dayyear_val_skym.setProperty("value", 90)
        self.dayyear_val_skym.setObjectName("dayyear_val_skym")
        self.verticalLayout_9.addWidget(self.dayyear_val_skym)
        self.horizontalLayout_5.addLayout(self.verticalLayout_9)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem5)
        self.dayyear_slide_skym = QtWidgets.QSlider(widget)
        self.dayyear_slide_skym.setMinimum(1)
        self.dayyear_slide_skym.setMaximum(365)
        self.dayyear_slide_skym.setProperty("value", 90)
        self.dayyear_slide_skym.setOrientation(QtCore.Qt.Vertical)
        self.dayyear_slide_skym.setObjectName("dayyear_slide_skym")
        self.horizontalLayout_5.addWidget(self.dayyear_slide_skym)
        self.verticalLayout_8.addLayout(self.horizontalLayout_5)
        self.line_3 = QtWidgets.QFrame(widget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.verticalLayout_8.addWidget(self.line_3)
        self.verticalLayout_3.addLayout(self.verticalLayout_8)
        spacerItem6 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem6)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.line_8 = QtWidgets.QFrame(widget)
        self.line_8.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_8.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_8.setObjectName("line_8")
        self.verticalLayout_10.addWidget(self.line_8)
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.label_6 = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setStyleSheet("")
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.verticalLayout_11.addWidget(self.label_6)
        self.timeday_val_skym = QtWidgets.QSpinBox(widget)
        self.timeday_val_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.timeday_val_skym.setMinimum(1)
        self.timeday_val_skym.setMaximum(24)
        self.timeday_val_skym.setProperty("value", 12)
        self.timeday_val_skym.setObjectName("timeday_val_skym")
        self.verticalLayout_11.addWidget(self.timeday_val_skym)
        self.horizontalLayout_6.addLayout(self.verticalLayout_11)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem7)
        self.timeday_slide_skym = QtWidgets.QSlider(widget)
        self.timeday_slide_skym.setMinimum(1)
        self.timeday_slide_skym.setMaximum(24)
        self.timeday_slide_skym.setProperty("value", 12)
        self.timeday_slide_skym.setOrientation(QtCore.Qt.Vertical)
        self.timeday_slide_skym.setObjectName("timeday_slide_skym")
        self.horizontalLayout_6.addWidget(self.timeday_slide_skym)
        self.verticalLayout_10.addLayout(self.horizontalLayout_6)
        self.line_7 = QtWidgets.QFrame(widget)
        self.line_7.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_7.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_7.setObjectName("line_7")
        self.verticalLayout_10.addWidget(self.line_7)
        self.verticalLayout_3.addLayout(self.verticalLayout_10)
        spacerItem8 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem8)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.line_6 = QtWidgets.QFrame(widget)
        self.line_6.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_6.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_6.setObjectName("line_6")
        self.verticalLayout_12.addWidget(self.line_6)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.label_7 = QtWidgets.QLabel(widget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_7.setFont(font)
        self.label_7.setStyleSheet("")
        self.label_7.setAlignment(QtCore.Qt.AlignCenter)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_13.addWidget(self.label_7)
        self.res_val_skym = QtWidgets.QSpinBox(widget)
        self.res_val_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.res_val_skym.setMinimum(1)
        self.res_val_skym.setMaximum(6)
        self.res_val_skym.setProperty("value", 1)
        self.res_val_skym.setObjectName("res_val_skym")
        self.verticalLayout_13.addWidget(self.res_val_skym)
        self.horizontalLayout_7.addLayout(self.verticalLayout_13)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_7.addItem(spacerItem9)
        self.res_slide_skym = QtWidgets.QSlider(widget)
        self.res_slide_skym.setMinimum(1)
        self.res_slide_skym.setMaximum(6)
        self.res_slide_skym.setProperty("value", 1)
        self.res_slide_skym.setOrientation(QtCore.Qt.Vertical)
        self.res_slide_skym.setObjectName("res_slide_skym")
        self.horizontalLayout_7.addWidget(self.res_slide_skym)
        self.verticalLayout_12.addLayout(self.horizontalLayout_7)
        self.line_5 = QtWidgets.QFrame(widget)
        self.line_5.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_5.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_5.setObjectName("line_5")
        self.verticalLayout_12.addWidget(self.line_5)
        self.verticalLayout_3.addLayout(self.verticalLayout_12)
        spacerItem10 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem10)
        self.gridLayout.addLayout(self.verticalLayout_3, 0, 0, 2, 1)
        spacerItem11 = QtWidgets.QSpacerItem(1, 447, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem11, 0, 1, 2, 2)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.button2d_skym = QtWidgets.QPushButton(widget)
        self.button2d_skym.setMaximumSize(QtCore.QSize(25, 16777215))
        self.button2d_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.button2d_skym.setObjectName("button2d_skym")
        self.horizontalLayout_3.addWidget(self.button2d_skym)
        spacerItem12 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem12)
        self.header_skym = QtWidgets.QLabel(widget)
        self.header_skym.setMinimumSize(QtCore.QSize(270, 0))
        font = QtGui.QFont()
        font.setFamily("Times New Roman")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.header_skym.setFont(font)
        self.header_skym.setAlignment(QtCore.Qt.AlignCenter)
        self.header_skym.setObjectName("header_skym")
        self.horizontalLayout_3.addWidget(self.header_skym)
        spacerItem13 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem13)
        self.button3d_skym = QtWidgets.QPushButton(widget)
        self.button3d_skym.setMaximumSize(QtCore.QSize(25, 16777215))
        self.button3d_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.button3d_skym.setObjectName("button3d_skym")
        self.horizontalLayout_3.addWidget(self.button3d_skym)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        spacerItem14 = QtWidgets.QSpacerItem(397, 13, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem14)
        self.plotter_skym = QtWidgets.QLabel(widget)
        self.plotter_skym.setMinimumSize(QtCore.QSize(400, 400))
        self.plotter_skym.setAutoFillBackground(False)
        self.plotter_skym.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.plotter_skym.setFrameShape(QtWidgets.QFrame.Panel)
        self.plotter_skym.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.plotter_skym.setText("")
        self.plotter_skym.setObjectName("plotter_skym")
        self.verticalLayout_6.addWidget(self.plotter_skym)
        self.gridLayout.addLayout(self.verticalLayout_6, 1, 2, 1, 1)
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        spacerItem15 = QtWidgets.QSpacerItem(20, 258, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_15.addItem(spacerItem15)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.hselect_spot_skym = QtWidgets.QSlider(widget)
        self.hselect_spot_skym.setMinimumSize(QtCore.QSize(15, 15))
        self.hselect_spot_skym.setMaximumSize(QtCore.QSize(31, 31))
        self.hselect_spot_skym.setMaximum(40)
        self.hselect_spot_skym.setProperty("value", 20)
        self.hselect_spot_skym.setOrientation(QtCore.Qt.Horizontal)
        self.hselect_spot_skym.setObjectName("hselect_spot_skym")
        self.verticalLayout_14.addWidget(self.hselect_spot_skym)
        self.spot_skym = QtWidgets.QLabel(widget)
        self.spot_skym.setMinimumSize(QtCore.QSize(31, 31))
        self.spot_skym.setMaximumSize(QtCore.QSize(31, 31))
        self.spot_skym.setStyleSheet("border: 1px solid rgb(32, 47, 64)")
        self.spot_skym.setText("")
        self.spot_skym.setObjectName("spot_skym")
        self.verticalLayout_14.addWidget(self.spot_skym)
        self.vselect_spot_skym = QtWidgets.QSlider(widget)
        self.vselect_spot_skym.setMinimumSize(QtCore.QSize(31, 31))
        self.vselect_spot_skym.setMaximumSize(QtCore.QSize(31, 31))
        self.vselect_spot_skym.setMaximum(40)
        self.vselect_spot_skym.setProperty("value", 20)
        self.vselect_spot_skym.setOrientation(QtCore.Qt.Vertical)
        self.vselect_spot_skym.setObjectName("vselect_spot_skym")
        self.verticalLayout_14.addWidget(self.vselect_spot_skym)
        self.verticalLayout_15.addLayout(self.verticalLayout_14)
        self.gridLayout.addLayout(self.verticalLayout_15, 1, 3, 1, 1)
        
        self.lat_slide_skym.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; width: 5px;\n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #777777;\n margin: 0px -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #405E80;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #202F40;\n}")
        self.skytype_slide_skym.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; width: 5px;\n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #777777;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #405E80;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #202F40;\n}")
        self.dayyear_slide_skym.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; width: 5px;\n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #777777;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #405E80;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #202F40;\n}")
        self.timeday_slide_skym.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; width: 5px;\n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #777777;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #405E80;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #202F40;\n}")  
        self.res_slide_skym.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; width: 5px;\n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #777777;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #405E80;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #202F40;\n}")
        self.vselect_spot_skym.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; width: 5px; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 5px;\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);border: 1px solid #777777;\n margin: 0 -10px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #405E80;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #202F40;\n}")
        self.hselect_spot_skym.setStyleSheet("QSlider::groove:horizontal {\n border: 1px solid #999999;\n height: 5px;\n background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1A2533, stop:1 #405E80);\n margin: 1px 0;\n}\n\n"
                                        "QSlider::handle:horizontal {\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f); height: 5px; \n border: 1px solid #403618;\n width: 5px;\n margin: -10px 0; \n border-radius: 3px;\n}")
                                            
        self.ThreeDWin = ThreeDSurface_GraphWindow()
        self.ThreeDWin.setMinimumSize(QtCore.QSize(400, 400))
        self.verticalLayout_6.addWidget(self.ThreeDWin)
        self.ThreeDWin.hide()

        self.retranslateUi(widget)
        self.skytype_slide_skym.valueChanged['int'].connect(self.skytype_val_skym.setValue)
        self.skytype_val_skym.valueChanged['int'].connect(self.skytype_slide_skym.setValue)
        self.dayyear_val_skym.valueChanged['int'].connect(self.dayyear_slide_skym.setValue)
        self.dayyear_slide_skym.valueChanged['int'].connect(self.dayyear_val_skym.setValue)
        self.timeday_val_skym.valueChanged['int'].connect(self.timeday_slide_skym.setValue)
        self.timeday_slide_skym.valueChanged['int'].connect(self.timeday_val_skym.setValue)
        self.res_val_skym.valueChanged['int'].connect(self.res_slide_skym.setValue)
        self.res_slide_skym.valueChanged['int'].connect(self.res_val_skym.setValue)
        self.lat_val_skym.valueChanged['int'].connect(self.lat_slide_skym.setValue)
        self.lat_slide_skym.valueChanged['int'].connect(self.lat_val_skym.setValue)
        QtCore.QMetaObject.connectSlotsByName(widget)
        
        self.falsecolor_slide_skym.valueChanged['int'].connect(plot_skymap)
        self.lat_val_skym.valueChanged['int'].connect(plot_skymap)
        self.skytype_val_skym.valueChanged['int'].connect(plot_skymap)
        self.dayyear_val_skym.valueChanged['int'].connect(plot_skymap)
        self.timeday_val_skym.valueChanged['int'].connect(plot_skymap)
        self.res_val_skym.valueChanged['int'].connect(plot_skymap)
        self.hselect_spot_skym.valueChanged['int'].connect(plot_skymap)
        self.vselect_spot_skym.valueChanged['int'].connect(plot_skymap)
        self.button2d_skym.clicked.connect(plot_skymap)
        self.button3d_skym.clicked.connect(plot_sky3d)
        QtCore.QMetaObject.connectSlotsByName(widget)

    def retranslateUi(self, widget):
        _translate = QtCore.QCoreApplication.translate
        widget.setWindowTitle(_translate("widget", "CIE Sky Model Simulator V2.3  \u00a9 Marshal Maskarenj, 2019"))
        self.falsecolor_label_skym.setText(_translate("widget", "False Color"))
        self.label_2.setText(_translate("widget", "Latitude"))
        self.label.setText(_translate("widget", "CIE Sky"))
        self.label_5.setText(_translate("widget", "Day of Year"))
        self.label_6.setText(_translate("widget", "Time of Day"))
        self.label_7.setText(_translate("widget", "Resolution"))
        self.button2d_skym.setText(_translate("widget", "2D"))
        self.header_skym.setText(_translate("widget", "Sky Plot"))
        self.button3d_skym.setText(_translate("widget", "3D"))




if __name__ == "__main__":
#    import sys
    skymodel_app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    skymodel = skymodel_widget()
    skymodel.setupUi(widget)
    widget.show()
    skymodel_app.exec_()
    del skymodel_app
