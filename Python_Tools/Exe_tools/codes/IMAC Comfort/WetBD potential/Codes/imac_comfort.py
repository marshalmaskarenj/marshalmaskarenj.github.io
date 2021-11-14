# -*- coding: utf-8 -*-
"""
Created on Mon Sep 23 09:36:59 2019

@author: marshal.maskarenj

https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
RH=100%*(E/Es)  or RH = E/Es ; where
(E = E0 x exp[(L/Rv) x {(1/T0) - (1/Td)}]) and  (Es = E0 x exp[(L/Rv) x {(1/T0) - (1/T)}])
    T0=273K  =>  1/T0=0.00366300366
    T=Dry Bulb Temp (GIVEN);  Td=Dew Point Temp (GIVEN)
    L/Rv=5423K; E0=0.611 KPa
RH=(exp(5423*(0.003663 - Td^-1))/(exp(5423*(0.003663 - T^-1))

----------------------------
https://www.omnicalculator.com/physics/wet-bulb#what-is-the-wet-bulb-temperature
https://journals.ametsoc.org/doi/full/10.1175/JAMC-D-11-0143.1


Tw = T * arctan[0.151977 * (rh% + 8.313659)^(1/2)] + arctan(T + rh%) - arctan(rh% - 1.676331) + 0.00391838 *(rh%)^(3/2) * arctan(0.023101 * rh%) - 4.686035

"""
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import pandas as pd
from pathlib import Path
import math
import csv
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def imac(my_file):
    fileread = open(my_file, 'r')
    rawdata = fileread.readlines()
    fileread.close()
    refinedata=rawdata[8:8768] 
    mylist=[]
    for i in range (0,8760,1):
        my_list = refinedata[i].split(",")
        mylist.append(my_list)
    wdata=np.asarray(mylist)
    data_col=wdata[:,[1, 2, 3, 6]]
    data_col=data_col.astype(np.float)
    dated_cval=np.zeros(24)
    day_cval=np.zeros((365,4))
    for i in range (0,365,1):
        for j in range (0,24,1):
            dated_cval[j]=data_col[24*i+j][3]
            mintemp=min(dated_cval)
            maxtemp=max(dated_cval)
            day_cval[i][0]=mintemp
            day_cval[i][1]=maxtemp
            meantemp=(mintemp+maxtemp)/2
            day_cval[i][2]=meantemp
    mean_t=day_cval[:,2]
    mean_t395 = np.zeros((395))
    for i in range (0,30,1):
        mean_t395[i]=mean_t[i+335]
    for i in range (0,365,1):
        mean_t395[i+30]=mean_t[i]
    for i in range (0,365,1):
        j=i+30
        day_cval[i][3]=sum(mean_t395[j-30:j])/30
    data_col=np.append(data_col, data_col[:,[3]], axis=1)
    for i in range (0,365,1):
        for j in range (0,24,1):
            data_col[24*i+j][4]=day_cval[i][3]
    zeroarr=np.zeros((8760,20))
    data_col=np.append(data_col,zeroarr,axis=1)
    for i in range (0,8760,1):
        data_col[i][5]=(0.54*data_col[i][4])+12.83
        data_col[i][6]=data_col[i][5]+2.38
        data_col[i][7]=data_col[i][5]-2.38
        data_col[i][8]=(0.28*data_col[i][4])+17.87
        data_col[i][9]=data_col[i][8]+3.46
        data_col[i][10]=data_col[i][8]-3.46
        data_col[i][11]=(0.078*data_col[i][4])+23.25
        data_col[i][12]=data_col[i][11]+1.5
        data_col[i][13]=data_col[i][11]-1.5
    return data_col


def wbd_pot(my_file):
    global data_wbd, dated_wbd, dated_DBT, ec_potential
    fileread = open(my_file, 'r')
    rawdata = fileread.readlines()
    fileread.close()
    refinedata=rawdata[8:8768] 
    mylist=[]
    for i in range (0,8760,1):
        my_list = refinedata[i].split(",")
        mylist.append(my_list)
    wdata=np.asarray(mylist)
    data_wbd=wdata[:,[1, 2, 3, 6, 7, 8]]
    data_wbd=data_wbd.astype(np.float)
    zeroarr=np.zeros((8760,20))
    data_wbd=np.append(data_wbd,zeroarr,axis=1)

    for i in range (0,8760,1): # RH Calculated as per formula above
        data_wbd[i][6]=((math.exp(5423*(0.003663 - 1/(data_wbd[i][4]+273.15))))/(math.exp(5423*(0.003663 - 1/(data_wbd[i][3]+273.15)))))*100   # RH Calculated as per formula above

    for i in range (0,8760,1): # WBT calculated from DBT and RH as per formula 2 above
        data_wbd[i][7]= (data_wbd[i][3] * np.arctan(0.151977 * (data_wbd[i][5] + 8.313659)**(1/2))) + (np.arctan(data_wbd[i][3] + data_wbd[i][5])) - (np.arctan(data_wbd[i][5] - 1.676331)) + (0.00391838 *(data_wbd[i][5])**(3/2) * np.arctan(0.023101 * data_wbd[i][5])) - 4.686035
        data_wbd[i][8]=data_wbd[i][3]-data_wbd[i][7]  #wet bulb depression

    dated_wbd=np.zeros(shape=(24,365))
    dated_DBT=np.zeros(shape=(24,365))
    for i in range (0,365,1):
        for j in range (0,24,1):
            dated_wbd[j][i]=data_wbd[24*i+j][8]
            dated_DBT[j][i]=data_wbd[24*i+j][3]
    ec_potential=np.zeros(shape=(24,365))
    for i in range (0,365,1):
        for j in range (0,24,1):
            if dated_DBT[j][i] >= 25: #CHANGE
                if dated_wbd[j][i] >= 8: #CHANGE
                    ec_potential[j][i]=1
  
    plt.imshow(dated_DBT, interpolation="nearest", origin="upper", aspect='auto',cmap='plasma')
    plt.title('Dry Bulb Temperature')
    plt.colorbar()
    plt.show()
    plt.imshow(dated_wbd, interpolation="nearest", origin="upper", aspect='auto',cmap='plasma')
    plt.title('Evaporative Cooling Potential')
    plt.colorbar()
    plt.show()
    plt.imshow(ec_potential, interpolation="nearest", origin="upper", aspect='auto',cmap='plasma')
    plt.title('EC Applicability')
#    plt.colorbar()
    plt.show()
    return data_wbd


def comforthours(data_col):
    global nvmm_data
    bgdata=data_col
    nv_data=np.zeros((24,365))
    mm_data=np.zeros((24,365))
    ac_data=np.zeros((24,365))
    nvmm_data=np.zeros((24,365))
    for i in range (0,365,1):
        for j in range (0,24,1):
            k = 24*i+j
            if bgdata[k][7] <= bgdata[k][3] <= bgdata[k][6]:
                nv_data[j][i]=1
            else:
                nv_data[j][i]=0    
            if bgdata[k][10] <= bgdata[k][3] <= bgdata[k][9]:
                mm_data[j][i]=1
            else:
                mm_data[j][i]=0   
            if bgdata[k][13] <= bgdata[k][3] <= bgdata[k][12]:
                ac_data[j][i]=1
            else:
                ac_data[j][i]=0
            nvmm_data[j][i]=nv_data[j][i]-mm_data[j][i]                  
    plt.imshow(nv_data, interpolation="nearest", origin="upper", aspect='auto',cmap='winter')
    plt.title('Comfort Achieved naturally for Poor People')
#    plt.colorbar()
    plt.show()
    plt.imshow(mm_data, interpolation="nearest", origin="upper", aspect='auto',cmap='winter')
    plt.title('Comfort Achieved naturally for Middle Class People')
#    plt.colorbar()
    plt.show()
    plt.imshow(ac_data, interpolation="nearest", origin="upper", aspect='auto',cmap='winter')
    plt.title('Comfort Achieved naturally for Rich People')
#    plt.colorbar()
    plt.show()
    plt.imshow(nvmm_data, interpolation="nearest", origin="upper", aspect='auto',cmap='winter')
    plt.title('NV-MM')
#    plt.colorbar()
    plt.show()
    return nv_data, mm_data, ac_data



class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(420, 520)
        MainWindow.setMinimumSize(QtCore.QSize(420, 520))
        MainWindow.setStyleSheet("background-color: #5BC3D2")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(10, 0, 402, 472))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(self.widget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.groupBox.setFont(font)
        self.groupBox.setObjectName("groupBox")
        self.widget1 = QtWidgets.QWidget(self.groupBox)
        self.widget1.setGeometry(QtCore.QRect(10, 20, 381, 42))
        self.widget1.setObjectName("widget1")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget1)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.widget1)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.comboBox = QtWidgets.QComboBox(self.widget1)
        self.comboBox.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.comboBox.setObjectName("comboBox")
        self.gridLayout.addWidget(self.comboBox, 1, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.widget1)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        self.comboBox_2 = QtWidgets.QComboBox(self.widget1)
        self.comboBox_2.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.comboBox_2.setObjectName("comboBox_2")
        self.gridLayout_2.addWidget(self.comboBox_2, 1, 0, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.pushButton = QtWidgets.QPushButton(self.widget1)
        self.pushButton.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.groupBox)
        self.MPLwidget = MPLWidget(self.widget)
        self.MPLwidget.setMinimumSize(QtCore.QSize(400, 400))
        self.MPLwidget.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(32, 47, 64); color:rgb(255,255,255)")
        self.MPLwidget.setObjectName("MPLwidget")
        self.verticalLayout.addWidget(self.MPLwidget)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 420, 21))
        self.menubar.setObjectName("menubar")
        self.menuMarshal = QtWidgets.QMenu(self.menubar)
        self.menuMarshal.setObjectName("menuMarshal")
        self.menuHow_to_Use = QtWidgets.QMenu(self.menubar)
        self.menuHow_to_Use.setObjectName("menuHow_to_Use")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionMarshal_Maskarenj_CEPT_2020 = QtWidgets.QAction(MainWindow)
        self.actionMarshal_Maskarenj_CEPT_2020.setObjectName("actionMarshal_Maskarenj_CEPT_2020")
        self.actionTutorial = QtWidgets.QAction(MainWindow)
        self.actionTutorial.setObjectName("actionTutorial")
        self.menuMarshal.addAction(self.actionMarshal_Maskarenj_CEPT_2020)
        self.menuHow_to_Use.addAction(self.actionTutorial)
        self.menubar.addAction(self.menuMarshal.menuAction())
        self.menubar.addAction(self.menuHow_to_Use.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBox.setTitle(_translate("MainWindow", "POTENTIAL FOR STRATEGIES"))
        self.label.setText(_translate("MainWindow", "Location"))
        self.label_2.setText(_translate("MainWindow", "Plot"))
        self.pushButton.setText(_translate("MainWindow", "Run"))
        self.menuMarshal.setTitle(_translate("MainWindow", "Credits"))
        self.menuHow_to_Use.setTitle(_translate("MainWindow", "How to Use"))
        self.actionMarshal_Maskarenj_CEPT_2020.setText(_translate("MainWindow", "Marshal Maskarenj, CEPT 2020"))
        self.actionTutorial.setText(_translate("MainWindow", "Tutorial"))


from mplwidget import MPLWidget


if __name__ == "__main__":
    
    my_file = Path('../EPW/Chennai.epw')
    data_col=imac(my_file)
    data_wbd=wbd_pot(my_file)
    nv_data, mm_data, ac_data=comforthours(data_col)

    plt.plot(data_col[:,3])
    plt.plot(data_col[:,5])
    plt.plot(data_col[:,6])
    plt.plot(data_col[:,7])
    plt.title('IMAC Band for Natural Ventilation')
    plt.show()
    
    plt.plot(data_col[:,3]) 
    plt.plot(data_col[:,8])
    plt.plot(data_col[:,9])
    plt.plot(data_col[:,10])
    plt.title('IMAC Band for Mixed Mode')
    plt.show()

    plt.plot(data_col[:,3])    
    plt.plot(data_col[:,11])
    plt.plot(data_col[:,12])
    plt.plot(data_col[:,13])       
    plt.title('IMAC Band for AC')
    plt.show()
    
    imac_app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    imac_app.exec_()
    del imac_app
