# -*- coding: utf-8 -*-
"""
Created on Tue Jul 2 10:38:48 2019

@author: marshal.maskarenj
"""
from PyQt5 import QtCore, QtGui, QtWidgets
#import numpy as np
#import matplotlib.pyplot as plt
#import matplotlib.ticker as ticker
import pyqtgraph as pg
import pandas as pd
#from numpy import genfromtxt
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton #, QTextEdit, QDialog, QVBoxLayout
#import os
pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')
pg.setConfigOption('leftButtonPan', False)
import ctypes
user32 = ctypes.windll.user32
screensize = user32.GetSystemMetrics(0)/1, user32.GetSystemMetrics(1)/1



def hex2QColor(c):
    """Convert Hex color to QColor"""
    r=int(c[0:2],16)
    g=int(c[2:4],16)
    b=int(c[4:6],16)
    return QtGui.QColor(r,g,b)

class file_select_Window (QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = "Wizard Step 1: Select CSV File with Data"
        self.top=screensize[0]/2 - 200
        self.left=screensize[1]/2 - 75
        self.width=400
        self.height=150
        self.setStyleSheet("background-color:rgb(230, 194, 87)")
        self.setWindowOpacity(0.95)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.borderRadius = 15
        self.foregroundColor = hex2QColor("333333")
        self.backgroundColor = hex2QColor("e6c257")
        self.InitWindow()
        
    def paintEvent(self, event):
        s = self.size()
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHint(QtGui.QPainter.Antialiasing, True)
        qp.setPen(self.foregroundColor)
        qp.setBrush(self.backgroundColor)
        qp.drawRoundedRect(0, 0, s.width(), s.height(),
                           self.borderRadius, self.borderRadius)
        qp.end()
    
    def InitWindow(self):
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)
        self.setWindowFlag(QtCore.Qt.WindowMaximizeButtonHint,False)
        self.csvselect=QPushButton("Select CSV File",self)
        self.csvselect.setGeometry(25,55,150,40)
        self.csvselect.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(128, 108, 48); color:rgb(255,255,255); border:1px solid #555; border-radius: 7px")  # border:1px solid #555; border-radius: 15px
        self.csvselect.setFont(font)
        self.csvselect.clicked.connect(openFileDialog)
        self.contbtn=QPushButton("Continue Program",self)
        self.contbtn.setFont(font)
        self.contbtn.setGeometry(225,55,150,40)
        self.contbtn.setStyleSheet("font-size:12px; font-family:Arial; background-color:rgb(128, 108, 48); color:rgb(255,255,255); border:1px solid #555; border-radius: 7px")
        self.contbtn.clicked.connect(self.close)
        self.contbtn.hide()
        self.csvselect.clicked.connect(self.contbtn.show)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.top, self.left, self.width, self.height)
        self.show()


def openFileDialog():
    global filename1, fname, luxdata, a_data_val, a_data_val2, a_data_val3, a_data_val4
    qfd = QFileDialog()
    fname=QFileDialog.getOpenFileName(qfd, "Marshal Files"," ","All Files (*);; CSV Files(*.csv);; Python Files(*.py)")
    filename1=fname[0]
    a_data_val, a_data_val2, a_data_val3, a_data_val4 = pullData(filename1)


def pullData(filename1):
    global luxdata, headval
    luxdata=pd.read_csv(filename1, delimiter=',', dtype=object)
    a_data_val = luxdata[luxdata.columns[0]]
    a_data_val2 = luxdata[luxdata.columns[1]]
    a_data_val3 = luxdata[luxdata.columns[2]]
    a_data_val4 = luxdata[luxdata.columns[3]]
    headval=luxdata.head()
    return a_data_val, a_data_val2, a_data_val3, a_data_val4

def file_case_range(caselen):
    paraplot.best_case_slide_par.setMaximum(caselen)
    paraplot.best_case_val_par.setMaximum(caselen)
    
def on_case_changed(self):
    global sortedluxdata
    file_case_range(len(a_data_val))
    select_case = paraplot.op_select_par.currentText()
    luxdata_quant=luxdata.astype(float)
    sortedluxdata=luxdata_quant.sort_values(by=[select_case])
    paraplot.best_case_slide_par.valueChanged['int'].connect(implotter_sorted)
    
def implotter_sorted():
    global a_data_parameter_lst, index_select
#    paraplot.best_case_slide_par.setValue=0
#    paraplot.best_case_val_par.setValue(0)
    paraplot.best_case_slide_par.setMaximum(300)
    paraplot.best_case_val_par.setMaximum(300)
    index_select=paraplot.best_case_slide_par.value()
    pos1_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[0]
    pos2_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[1]
    pos3_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[2]
    pos4_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[3]
    pos5_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[4]
    pos6_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[5]
    pos7_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[6]
    pos8_select=str(int(sortedluxdata.iloc[index_select,0])).zfill(8)[7]
    if len(a_data_val[0])==8:
        pass
    elif len(a_data_val[0])==7:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
    elif len(a_data_val[0])==6:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
    elif len(a_data_val[0])==5:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
    elif len(a_data_val[0])==4:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
    elif len(a_data_val[0])==3:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
        paraplot.p5_slide_par.setMaximum(0)
        paraplot.p5_slide_par.setMinimum(0)
        paraplot.p5_slide_par.setValue=0
    elif len(a_data_val[0])==2:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
        paraplot.p5_slide_par.setMaximum(0)
        paraplot.p5_slide_par.setMinimum(0)
        paraplot.p5_slide_par.setValue=0
        paraplot.p6_slide_par.setMaximum(0)
        paraplot.p6_slide_par.setMinimum(0)
        paraplot.p6_slide_par.setValue=0
    elif len(a_data_val[0])==1:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
        paraplot.p5_slide_par.setMaximum(0)
        paraplot.p5_slide_par.setMinimum(0)
        paraplot.p5_slide_par.setValue=0
        paraplot.p6_slide_par.setMaximum(0)
        paraplot.p6_slide_par.setMinimum(0)
        paraplot.p6_slide_par.setValue=0
        paraplot.p7_slide_par.setMaximum(0)
        paraplot.p7_slide_par.setMinimum(0)
        paraplot.p7_slide_par.setValue=0
        pass
    
    y1val=int(pos1_select)
    y2val=int(pos2_select)
    y3val=int(pos3_select)
    y4val=int(pos4_select)
    y5val=int(pos5_select)
    y6val=int(pos6_select)
    y7val=int(pos7_select)
    y8val=int(pos8_select)
    
    paraplot.p1_slide_par.setValue(y1val)
    paraplot.p2_slide_par.setValue(y2val)
    paraplot.p3_slide_par.setValue(y3val)
    paraplot.p4_slide_par.setValue(y4val)
    paraplot.p5_slide_par.setValue(y5val)
    paraplot.p6_slide_par.setValue(y6val)
    paraplot.p7_slide_par.setValue(y7val)
    paraplot.p8_slide_par.setValue(y8val)

    paraplot.p1p2_map_par.clear()
    paraplot.p2p3_map_par.clear()
    paraplot.p3p4_map_par.clear()
    paraplot.p4p5_map_par.clear()
    paraplot.p5p6_map_par.clear()
    paraplot.p6p7_map_par.clear()
    paraplot.p7p8_map_par.clear()
    
    
    p12pltt= paraplot.p1p2_map_par.plot(y=[y1val,y2val])
    p23pltt= paraplot.p2p3_map_par.plot(y=[y2val,y3val])
    p34pltt= paraplot.p3p4_map_par.plot(y=[y3val,y4val])
    p45pltt= paraplot.p4p5_map_par.plot(y=[y4val,y5val])
    p56pltt= paraplot.p5p6_map_par.plot(y=[y5val,y6val])
    p67pltt= paraplot.p6p7_map_par.plot(y=[y6val,y7val])
    p78pltt= paraplot.p7p8_map_par.plot(y=[y7val,y8val])
    
    p12pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p23pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p34pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p45pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p56pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p67pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p78pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    
    paraplot.opt1_par.setText(str(y1val))
    paraplot.opt2_par.setText(str(y2val))
    paraplot.opt3_par.setText(str(y3val))
    paraplot.opt4_par.setText(str(y4val))
    paraplot.opt5_par.setText(str(y5val))
    paraplot.opt6_par.setText(str(y6val))
    paraplot.opt7_par.setText(str(y7val))
    paraplot.opt8_par.setText(str(y8val))
    
    par_string=int(str(y1val)+str(y2val)+str(y3val)+str(y4val)+str(y5val)+str(y6val)+str(y7val)+str(y8val))
    a_data_parameter_x = a_data_val 
    a_data_parameter_lst = [int(i) for i in a_data_parameter_x]
    ind_par=a_data_parameter_lst.index(par_string)
    out_val_str=a_data_val2[ind_par]
    out_val2_str=a_data_val3[ind_par]
    out_val3_str=a_data_val4[ind_par]
    out_val_str=float(out_val_str)
    out_val_str=round(out_val_str,2)
    out_val2_str=float(out_val2_str)
    out_val2_str=round(out_val2_str,2)
    out_val3_str=float(out_val3_str)
    out_val3_str=round(out_val3_str,2)
    paraplot.op1val_par.setText(str(out_val_str))
    paraplot.op2val_par.setText(str(out_val2_str))
    paraplot.op3val_par.setText(str(out_val3_str))


def implotter():
    global a_data_parameter_lst
    if len(a_data_val[0])==8:
        pass
    elif len(a_data_val[0])==7:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
    elif len(a_data_val[0])==6:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
    elif len(a_data_val[0])==5:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
    elif len(a_data_val[0])==4:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
    elif len(a_data_val[0])==3:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
        paraplot.p5_slide_par.setMaximum(0)
        paraplot.p5_slide_par.setMinimum(0)
        paraplot.p5_slide_par.setValue=0
    elif len(a_data_val[0])==2:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
        paraplot.p5_slide_par.setMaximum(0)
        paraplot.p5_slide_par.setMinimum(0)
        paraplot.p5_slide_par.setValue=0
        paraplot.p6_slide_par.setMaximum(0)
        paraplot.p6_slide_par.setMinimum(0)
        paraplot.p6_slide_par.setValue=0
    elif len(a_data_val[0])==1:
        paraplot.p1_slide_par.setMaximum(0)
        paraplot.p1_slide_par.setMinimum(0)
        paraplot.p1_slide_par.setValue=0
        paraplot.p2_slide_par.setMaximum(0)
        paraplot.p2_slide_par.setMinimum(0)
        paraplot.p2_slide_par.setValue=0
        paraplot.p3_slide_par.setMaximum(0)
        paraplot.p3_slide_par.setMinimum(0)
        paraplot.p3_slide_par.setValue=0
        paraplot.p4_slide_par.setMaximum(0)
        paraplot.p4_slide_par.setMinimum(0)
        paraplot.p4_slide_par.setValue=0
        paraplot.p5_slide_par.setMaximum(0)
        paraplot.p5_slide_par.setMinimum(0)
        paraplot.p5_slide_par.setValue=0
        paraplot.p6_slide_par.setMaximum(0)
        paraplot.p6_slide_par.setMinimum(0)
        paraplot.p6_slide_par.setValue=0
        paraplot.p7_slide_par.setMaximum(0)
        paraplot.p7_slide_par.setMinimum(0)
        paraplot.p7_slide_par.setValue=0
        pass
    
    y1val=paraplot.p1_slide_par.value()
    y2val=paraplot.p2_slide_par.value()
    y3val=paraplot.p3_slide_par.value()
    y4val=paraplot.p4_slide_par.value()
    y5val=paraplot.p5_slide_par.value()
    y6val=paraplot.p6_slide_par.value()
    y7val=paraplot.p7_slide_par.value()
    y8val=paraplot.p8_slide_par.value()

    paraplot.p1p2_map_par.clear()
    paraplot.p2p3_map_par.clear()
    paraplot.p3p4_map_par.clear()
    paraplot.p4p5_map_par.clear()
    paraplot.p5p6_map_par.clear()
    paraplot.p6p7_map_par.clear()
    paraplot.p7p8_map_par.clear()
    
    
    p12pltt= paraplot.p1p2_map_par.plot(y=[y1val,y2val])
    p23pltt= paraplot.p2p3_map_par.plot(y=[y2val,y3val])
    p34pltt= paraplot.p3p4_map_par.plot(y=[y3val,y4val])
    p45pltt= paraplot.p4p5_map_par.plot(y=[y4val,y5val])
    p56pltt= paraplot.p5p6_map_par.plot(y=[y5val,y6val])
    p67pltt= paraplot.p6p7_map_par.plot(y=[y6val,y7val])
    p78pltt= paraplot.p7p8_map_par.plot(y=[y7val,y8val])
    
    p12pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p23pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p34pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p45pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p56pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p67pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    p78pltt.setPen(color=(128, 108, 48), width=3, style=QtCore.Qt.DotLine)
    
    paraplot.opt1_par.setText(str(y1val))
    paraplot.opt2_par.setText(str(y2val))
    paraplot.opt3_par.setText(str(y3val))
    paraplot.opt4_par.setText(str(y4val))
    paraplot.opt5_par.setText(str(y5val))
    paraplot.opt6_par.setText(str(y6val))
    paraplot.opt7_par.setText(str(y7val))
    paraplot.opt8_par.setText(str(y8val))
    
    par_string=int(str(y1val)+str(y2val)+str(y3val)+str(y4val)+str(y5val)+str(y6val)+str(y7val)+str(y8val))
    a_data_parameter_x = a_data_val 
    a_data_parameter_lst = [int(i) for i in a_data_parameter_x]
    ind_par=a_data_parameter_lst.index(par_string)
    out_val_str=a_data_val2[ind_par]
    out_val2_str=a_data_val3[ind_par]
    out_val3_str=a_data_val4[ind_par]
    out_val_str=float(out_val_str)
    out_val_str=round(out_val_str,2)
    out_val2_str=float(out_val2_str)
    out_val2_str=round(out_val2_str,2)
    out_val3_str=float(out_val3_str)
    out_val3_str=round(out_val3_str,2)
    paraplot.op1val_par.setText(str(out_val_str))
    paraplot.op2val_par.setText(str(out_val2_str))
    paraplot.op3val_par.setText(str(out_val3_str))


class plotter_parametric(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(882, 364)
        MainWindow.setStyleSheet("background-color: rgb(254, 215, 96)")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_15 = QtWidgets.QVBoxLayout()
        self.verticalLayout_15.setObjectName("verticalLayout_15")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setFamily("MS Shell Dlg 2")
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.horizontalLayout_3.addWidget(self.label)
        self.op_select_par = QtWidgets.QComboBox(self.centralwidget)
        self.op_select_par.setMinimumSize(QtCore.QSize(100, 0))
        self.op_select_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255);")
        self.op_select_par.setCurrentText("")
        self.op_select_par.setObjectName("op_select_par")
        self.horizontalLayout_3.addWidget(self.op_select_par)
        self.best_case_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.best_case_slide_par.setMinimumSize(QtCore.QSize(200, 0))
        self.best_case_slide_par.setMaximumSize(QtCore.QSize(300, 16777215))
        self.best_case_slide_par.setToolTip("")
        self.best_case_slide_par.setStyleSheet("QSlider::groove:horizontal {\n border: 1px solid #999999;\n height: 8px;\n background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #806C30, stop:1 #403618);\n margin: 1px 0;\n}\n\n"
                                                "QSlider::handle:horizontal {\n background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);\n border: 1px solid #403618;\n width: 18px;\n margin: -2px 0; \n border-radius: 3px;\n}")
        self.best_case_slide_par.setMinimum(1)
        self.best_case_slide_par.setMaximum(30)
        self.best_case_slide_par.setOrientation(QtCore.Qt.Horizontal)
        self.best_case_slide_par.setObjectName("best_case_slide_par")
        self.horizontalLayout_3.addWidget(self.best_case_slide_par)
        self.best_case_val_par = QtWidgets.QSpinBox(self.centralwidget)
        self.best_case_val_par.setMinimumSize(QtCore.QSize(100, 0))
        self.best_case_val_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255);")
        self.best_case_val_par.setMinimum(1)
        self.best_case_val_par.setMaximum(10000)
        self.best_case_val_par.setObjectName("best_case_val_par")
        self.horizontalLayout_3.addWidget(self.best_case_val_par)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.verticalLayout_15.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.p1_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p1_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p1_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p1_slide_par.setMaximum(3)
        self.p1_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p1_slide_par.setObjectName("p1_slide_par")
        self.horizontalLayout.addWidget(self.p1_slide_par)
        self.p1p2_map_par = pg.PlotWidget(self.centralwidget)
        self.p1p2_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p1p2_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p1p2_map_par.setObjectName("p1p2_map_par")
        self.horizontalLayout.addWidget(self.p1p2_map_par)
        self.p2_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p2_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p2_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p2_slide_par.setMaximum(3)
        self.p2_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p2_slide_par.setObjectName("p2_slide_par")
        self.horizontalLayout.addWidget(self.p2_slide_par)
        self.p2p3_map_par = pg.PlotWidget(self.centralwidget)
        self.p2p3_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p2p3_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p2p3_map_par.setObjectName("p2p3_map_par")
        self.horizontalLayout.addWidget(self.p2p3_map_par)
        self.p3_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p3_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p3_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p3_slide_par.setMaximum(3)
        self.p3_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p3_slide_par.setObjectName("p3_slide_par")
        self.horizontalLayout.addWidget(self.p3_slide_par)
        self.p3p4_map_par = pg.PlotWidget(self.centralwidget)
        self.p3p4_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p3p4_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p3p4_map_par.setObjectName("p3p4_map_par")
        self.horizontalLayout.addWidget(self.p3p4_map_par)
        self.p4_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p4_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p4_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p4_slide_par.setMaximum(3)
        self.p4_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p4_slide_par.setObjectName("p4_slide_par")
        self.horizontalLayout.addWidget(self.p4_slide_par)
        self.p4p5_map_par = pg.PlotWidget(self.centralwidget)
        self.p4p5_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p4p5_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p4p5_map_par.setObjectName("p4p5_map_par")
        self.horizontalLayout.addWidget(self.p4p5_map_par)
        self.p5_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p5_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p5_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p5_slide_par.setMaximum(3)
        self.p5_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p5_slide_par.setObjectName("p5_slide_par")
        self.horizontalLayout.addWidget(self.p5_slide_par)
        self.p5p6_map_par = pg.PlotWidget(self.centralwidget)
        self.p5p6_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p5p6_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p5p6_map_par.setObjectName("p5p6_map_par")
        self.horizontalLayout.addWidget(self.p5p6_map_par)
        self.p6_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p6_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p6_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p6_slide_par.setMaximum(3)
        self.p6_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p6_slide_par.setObjectName("p6_slide_par")
        self.horizontalLayout.addWidget(self.p6_slide_par)
        self.p6p7_map_par = pg.PlotWidget(self.centralwidget)
        self.p6p7_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p6p7_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p6p7_map_par.setObjectName("p6p7_map_par")
        self.horizontalLayout.addWidget(self.p6p7_map_par)
        self.p7_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p7_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p7_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p7_slide_par.setMaximum(3)
        self.p7_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p7_slide_par.setObjectName("p7_slide_par")
        self.horizontalLayout.addWidget(self.p7_slide_par)
        self.p7p8_map_par = pg.PlotWidget(self.centralwidget)
        self.p7p8_map_par.setMinimumSize(QtCore.QSize(80, 200))
        self.p7p8_map_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24)")
        self.p7p8_map_par.setObjectName("p7p8_map_par")
        self.horizontalLayout.addWidget(self.p7p8_map_par)
        self.p8_slide_par = QtWidgets.QSlider(self.centralwidget)
        self.p8_slide_par.setMinimumSize(QtCore.QSize(15, 200))
        self.p8_slide_par.setStyleSheet("QSlider::groove:vertical {\n background: red;\n position: absolute; \n left: 4px; right: 4px;\n}\n\n" 
                                        "QSlider::handle:vertical {\n height: 15px;\n background: #403618;\n margin: 0 -4px; border-radius: 3px;\n}\n\n"
                                        "QSlider::add-page:vertical {\n background: #e6c257;\n}\n\n"
                                        "QSlider::sub-page:vertical {\n background: #806C30;\n}")
        self.p8_slide_par.setMaximum(3)
        self.p8_slide_par.setOrientation(QtCore.Qt.Vertical)
        self.p8_slide_par.setObjectName("p8_slide_par")
        self.horizontalLayout.addWidget(self.p8_slide_par)
        self.verticalLayout_15.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout_15, 0, 1, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 2, 0, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem3, 0, 0, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(35, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem4, 1, 2, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.par1_par = QtWidgets.QLabel(self.centralwidget)
        self.par1_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par1_par.setFont(font)
        self.par1_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par1_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par1_par.setObjectName("par1_par")
        self.verticalLayout_7.addWidget(self.par1_par)
        self.opt1_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt1_par.setFont(font)
        self.opt1_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt1_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt1_par.setObjectName("opt1_par")
        self.verticalLayout_7.addWidget(self.opt1_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_7)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.verticalLayout_8 = QtWidgets.QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.par2_par = QtWidgets.QLabel(self.centralwidget)
        self.par2_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par2_par.setFont(font)
        self.par2_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par2_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par2_par.setObjectName("par2_par")
        self.verticalLayout_8.addWidget(self.par2_par)
        self.opt2_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt2_par.setFont(font)
        self.opt2_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt2_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt2_par.setObjectName("opt2_par")
        self.verticalLayout_8.addWidget(self.opt2_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_8)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.par3_par = QtWidgets.QLabel(self.centralwidget)
        self.par3_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par3_par.setFont(font)
        self.par3_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par3_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par3_par.setObjectName("par3_par")
        self.verticalLayout_10.addWidget(self.par3_par)
        self.opt3_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt3_par.setFont(font)
        self.opt3_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt3_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt3_par.setObjectName("opt3_par")
        self.verticalLayout_10.addWidget(self.opt3_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_10)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem7)
        self.verticalLayout_9 = QtWidgets.QVBoxLayout()
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.par4_par = QtWidgets.QLabel(self.centralwidget)
        self.par4_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par4_par.setFont(font)
        self.par4_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par4_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par4_par.setObjectName("par4_par")
        self.verticalLayout_9.addWidget(self.par4_par)
        self.opt4_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt4_par.setFont(font)
        self.opt4_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt4_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt4_par.setObjectName("opt4_par")
        self.verticalLayout_9.addWidget(self.opt4_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_9)
        spacerItem8 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem8)
        self.verticalLayout_13 = QtWidgets.QVBoxLayout()
        self.verticalLayout_13.setObjectName("verticalLayout_13")
        self.par5_par = QtWidgets.QLabel(self.centralwidget)
        self.par5_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par5_par.setFont(font)
        self.par5_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par5_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par5_par.setObjectName("par5_par")
        self.verticalLayout_13.addWidget(self.par5_par)
        self.opt5_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt5_par.setFont(font)
        self.opt5_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt5_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt5_par.setObjectName("opt5_par")
        self.verticalLayout_13.addWidget(self.opt5_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_13)
        spacerItem9 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem9)
        self.verticalLayout_12 = QtWidgets.QVBoxLayout()
        self.verticalLayout_12.setObjectName("verticalLayout_12")
        self.par6_par = QtWidgets.QLabel(self.centralwidget)
        self.par6_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par6_par.setFont(font)
        self.par6_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par6_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par6_par.setObjectName("par6_par")
        self.verticalLayout_12.addWidget(self.par6_par)
        self.opt6_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt6_par.setFont(font)
        self.opt6_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt6_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt6_par.setObjectName("opt6_par")
        self.verticalLayout_12.addWidget(self.opt6_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_12)
        spacerItem10 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem10)
        self.verticalLayout_14 = QtWidgets.QVBoxLayout()
        self.verticalLayout_14.setObjectName("verticalLayout_14")
        self.par7_par = QtWidgets.QLabel(self.centralwidget)
        self.par7_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par7_par.setFont(font)
        self.par7_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par7_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par7_par.setObjectName("par7_par")
        self.verticalLayout_14.addWidget(self.par7_par)
        self.opt7_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt7_par.setFont(font)
        self.opt7_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt7_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt7_par.setObjectName("opt7_par")
        self.verticalLayout_14.addWidget(self.opt7_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_14)
        spacerItem11 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem11)
        self.verticalLayout_11 = QtWidgets.QVBoxLayout()
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.par8_par = QtWidgets.QLabel(self.centralwidget)
        self.par8_par.setMinimumSize(QtCore.QSize(50, 0))
        font = QtGui.QFont()
        font.setPointSize(6)
        font.setBold(True)
        font.setWeight(75)
        self.par8_par.setFont(font)
        self.par8_par.setStyleSheet(" background-color:rgb(230, 194, 87);border: 1px solid rgb(64, 54, 24); border-radius: 3px")
        self.par8_par.setAlignment(QtCore.Qt.AlignCenter)
        self.par8_par.setObjectName("par8_par")
        self.verticalLayout_11.addWidget(self.par8_par)
        self.opt8_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setBold(False)
        font.setWeight(50)
        self.opt8_par.setFont(font)
        self.opt8_par.setStyleSheet(" background-color:rgb(255, 215, 97)")
        self.opt8_par.setAlignment(QtCore.Qt.AlignCenter)
        self.opt8_par.setObjectName("opt8_par")
        self.verticalLayout_11.addWidget(self.opt8_par)
        self.horizontalLayout_2.addLayout(self.verticalLayout_11)
        self.gridLayout.addLayout(self.horizontalLayout_2, 1, 0, 1, 2)
        self.verticalLayout_6 = QtWidgets.QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        spacerItem12 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem12)
        self.op1_par = QtWidgets.QLabel(self.centralwidget)
        self.op1_par.setMinimumSize(QtCore.QSize(80, 0))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.op1_par.setFont(font)
        self.op1_par.setObjectName("op1_par")
        self.verticalLayout.addWidget(self.op1_par)
        self.op1val_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.op1val_par.setFont(font)
        self.op1val_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255); border-radius: 3px")
        self.op1val_par.setText("")
        self.op1val_par.setObjectName("op1val_par")
        self.verticalLayout.addWidget(self.op1val_par)
        self.verticalLayout_6.addLayout(self.verticalLayout)
        spacerItem13 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem13)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.op2_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.op2_par.setFont(font)
        self.op2_par.setObjectName("op2_par")
        self.verticalLayout_2.addWidget(self.op2_par)
        self.op2val_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.op2val_par.setFont(font)
        self.op2val_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255); border-radius: 3px")
        self.op2val_par.setText("")
        self.op2val_par.setObjectName("op2val_par")
        self.verticalLayout_2.addWidget(self.op2val_par)
        self.verticalLayout_6.addLayout(self.verticalLayout_2)
        spacerItem14 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem14)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.op3_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.op3_par.setFont(font)
        self.op3_par.setObjectName("op3_par")
        self.verticalLayout_3.addWidget(self.op3_par)
        self.op3val_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.op3val_par.setFont(font)
        self.op3val_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255); border-radius: 3px")
        self.op3val_par.setText("")
        self.op3val_par.setObjectName("op3val_par")
        self.verticalLayout_3.addWidget(self.op3val_par)
        self.verticalLayout_6.addLayout(self.verticalLayout_3)
        spacerItem15 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem15)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.op4_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.op4_par.setFont(font)
        self.op4_par.setObjectName("op4_par")
        self.verticalLayout_4.addWidget(self.op4_par)
        self.op4val_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.op4val_par.setFont(font)
        self.op4val_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255); border-radius: 3px")
        self.op4val_par.setText("")
        self.op4val_par.setObjectName("op4val_par")
        self.verticalLayout_4.addWidget(self.op4val_par)
        self.verticalLayout_6.addLayout(self.verticalLayout_4)
        spacerItem16 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_6.addItem(spacerItem16)
        self.verticalLayout_5 = QtWidgets.QVBoxLayout()
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.op5_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.op5_par.setFont(font)
        self.op5_par.setObjectName("op5_par")
        self.verticalLayout_5.addWidget(self.op5_par)
        self.op5val_par = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.op5val_par.setFont(font)
        self.op5val_par.setStyleSheet(" background-color:rgb(128, 108, 48); color:rgb(255,255,255); border-radius: 3px")
        self.op5val_par.setText("")
        self.op5val_par.setObjectName("op5val_par")
        self.verticalLayout_5.addWidget(self.op5val_par)
        self.verticalLayout_6.addLayout(self.verticalLayout_5)
        self.gridLayout.addLayout(self.verticalLayout_6, 0, 2, 1, 1)
        spacerItem17 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem17, 4, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 882, 21))
        self.menubar.setStyleSheet("background-color: rgb(230, 194, 87)")
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuOption = QtWidgets.QMenu(self.menubar)
        self.menuOption.setObjectName("menuOption")
        self.menuMore = QtWidgets.QMenu(self.menubar)
        self.menuMore.setObjectName("menuMore")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionF2 = QtWidgets.QAction(MainWindow)
        self.actionF2.setObjectName("actionF2")
        self.actionF3 = QtWidgets.QAction(MainWindow)
        self.actionF3.setObjectName("actionF3")
        self.actionF4 = QtWidgets.QAction(MainWindow)
        self.actionF4.setObjectName("actionF4")
        self.actionReset = QtWidgets.QAction(MainWindow)
        self.actionReset.setObjectName("actionReset")
        self.actionE3 = QtWidgets.QAction(MainWindow)
        self.actionE3.setObjectName("actionE3")
        self.actionE4 = QtWidgets.QAction(MainWindow)
        self.actionE4.setObjectName("actionE4")
        self.actionTop_5 = QtWidgets.QAction(MainWindow)
        self.actionTop_5.setObjectName("actionTop_5")
        self.actionTop_10 = QtWidgets.QAction(MainWindow)
        self.actionTop_10.setObjectName("actionTop_10")
        self.actionM1 = QtWidgets.QAction(MainWindow)
        self.actionM1.setObjectName("actionM1")
        self.actionM2 = QtWidgets.QAction(MainWindow)
        self.actionM2.setObjectName("actionM2")
        self.actionTop_50 = QtWidgets.QAction(MainWindow)
        self.actionTop_50.setObjectName("actionTop_50")
        self.menuFile.addAction(self.actionF2)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionF3)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionF4)
        self.menuEdit.addAction(self.actionReset)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionE3)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionE4)
        self.menuOption.addAction(self.actionTop_5)
        self.menuOption.addSeparator()
        self.menuOption.addAction(self.actionTop_10)
        self.menuOption.addSeparator()
        self.menuOption.addAction(self.actionTop_50)
        self.menuMore.addAction(self.actionM1)
        self.menuMore.addSeparator()
        self.menuMore.addAction(self.actionM2)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuOption.menuAction())
        self.menubar.addAction(self.menuMore.menuAction())

        bestcase_item1=list(headval)[0]
        bestcase_item2=list(headval)[1]
        bestcase_item3=list(headval)[2]
        bestcase_item4=list(headval)[3]
        self.op_select_par.addItem(bestcase_item1)
        self.op_select_par.addItem(bestcase_item2)
        self.op_select_par.addItem(bestcase_item3)
        self.op_select_par.addItem(bestcase_item4)
        
        
        self.p1p2_map_par.hideAxis('bottom')
        self.p1p2_map_par.hideAxis('left')
        self.p1p2_map_par.setXRange(0, 1, padding=0)
        self.p1p2_map_par.setYRange(0, 3, padding=0)
        self.p2p3_map_par.hideAxis('bottom')
        self.p2p3_map_par.hideAxis('left')
        self.p2p3_map_par.setXRange(0, 1, padding=0)
        self.p2p3_map_par.setYRange(0, 3, padding=0)
        self.p3p4_map_par.hideAxis('bottom')
        self.p3p4_map_par.hideAxis('left')
        self.p3p4_map_par.setXRange(0, 1, padding=0)
        self.p3p4_map_par.setYRange(0, 3, padding=0)
        self.p4p5_map_par.hideAxis('bottom')
        self.p4p5_map_par.hideAxis('left')
        self.p4p5_map_par.setXRange(0, 1, padding=0)
        self.p4p5_map_par.setYRange(0, 3, padding=0)
        self.p5p6_map_par.hideAxis('bottom')
        self.p5p6_map_par.hideAxis('left')
        self.p5p6_map_par.setXRange(0, 1, padding=0)
        self.p5p6_map_par.setYRange(0, 3, padding=0)
        self.p6p7_map_par.hideAxis('bottom')
        self.p6p7_map_par.hideAxis('left')
        self.p6p7_map_par.setXRange(0, 1, padding=0)
        self.p6p7_map_par.setYRange(0, 3, padding=0)
        self.p7p8_map_par.hideAxis('bottom')
        self.p7p8_map_par.hideAxis('left')
        self.p7p8_map_par.setXRange(0, 1, padding=0)
        self.p7p8_map_par.setYRange(0, 3, padding=0)
        
        
        
        self.p1_slide_par.setValue(1)
        self.p2_slide_par.setValue(1)
        self.p3_slide_par.setValue(1)
        self.p4_slide_par.setValue(1)
        self.p5_slide_par.setValue(1)
        self.p6_slide_par.setValue(1)
        self.p7_slide_par.setValue(1)
        self.p8_slide_par.setValue(1)
        
        
        
        self.p1p2_map_par.plot(y=[self.p1_slide_par.value(),self.p2_slide_par.value()])
        self.p2p3_map_par.plot(y=[self.p2_slide_par.value(),self.p3_slide_par.value()])
        self.p3p4_map_par.plot(y=[self.p3_slide_par.value(),self.p4_slide_par.value()])
        self.p4p5_map_par.plot(y=[self.p4_slide_par.value(),self.p5_slide_par.value()])
        self.p5p6_map_par.plot(y=[self.p5_slide_par.value(),self.p6_slide_par.value()])
        self.p6p7_map_par.plot(y=[self.p6_slide_par.value(),self.p7_slide_par.value()])
        self.p7p8_map_par.plot(y=[self.p7_slide_par.value(),self.p8_slide_par.value()])
        
        self.p1_slide_par.valueChanged['int'].connect(implotter)
        self.p2_slide_par.valueChanged['int'].connect(implotter)
        self.p3_slide_par.valueChanged['int'].connect(implotter)
        self.p4_slide_par.valueChanged['int'].connect(implotter)
        self.p5_slide_par.valueChanged['int'].connect(implotter)
        self.p6_slide_par.valueChanged['int'].connect(implotter)
        self.p7_slide_par.valueChanged['int'].connect(implotter)
        self.p8_slide_par.valueChanged['int'].connect(implotter)
        
        
        self.actionF2.triggered.connect(openFileDialog)
        
        

        self.retranslateUi(MainWindow)
        self.best_case_slide_par.valueChanged['int'].connect(self.best_case_val_par.setValue)
        self.best_case_val_par.valueChanged['int'].connect(self.best_case_slide_par.setValue)
        self.p5_slide_par.valueChanged['int'].connect(self.opt5_par.setNum)
        self.p4_slide_par.valueChanged['int'].connect(self.opt4_par.setNum)
        self.p3_slide_par.valueChanged['int'].connect(self.opt3_par.setNum)
        self.p2_slide_par.valueChanged['int'].connect(self.opt2_par.setNum)
        self.p1_slide_par.valueChanged['int'].connect(self.opt1_par.setNum)
        self.p6_slide_par.valueChanged['int'].connect(self.opt6_par.setNum)
        self.p7_slide_par.valueChanged['int'].connect(self.opt7_par.setNum)
        self.p8_slide_par.valueChanged['int'].connect(self.opt8_par.setNum)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.op_select_par.currentTextChanged.connect(on_case_changed)
        

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "POT: Parametric Optimisation Tool"))
        self.label.setText(_translate("MainWindow", "Best Cases for"))
        self.par1_par.setText(_translate("MainWindow", "Parameter 1"))
        self.opt1_par.setText(_translate("MainWindow", "Option"))
        self.par2_par.setText(_translate("MainWindow", "Parameter 2"))
        self.opt2_par.setText(_translate("MainWindow", "Option"))
        self.par3_par.setText(_translate("MainWindow", "Parameter 3"))
        self.opt3_par.setText(_translate("MainWindow", "Option"))
        self.par4_par.setText(_translate("MainWindow", "Parameter 4"))
        self.opt4_par.setText(_translate("MainWindow", "Option"))
        self.par5_par.setText(_translate("MainWindow", "Parameter 5"))
        self.opt5_par.setText(_translate("MainWindow", "Option"))
        self.par6_par.setText(_translate("MainWindow", "Parameter 6"))
        self.opt6_par.setText(_translate("MainWindow", "Option"))
        self.par7_par.setText(_translate("MainWindow", "Parameter 7"))
        self.opt7_par.setText(_translate("MainWindow", "Option"))
        self.par8_par.setText(_translate("MainWindow", "Parameter 8"))
        self.opt8_par.setText(_translate("MainWindow", "Option"))
        self.op1_par.setText(_translate("MainWindow", "EUI"))
        self.op2_par.setText(_translate("MainWindow", "Cooling"))
        self.op3_par.setText(_translate("MainWindow", "Heating"))
        self.op4_par.setText(_translate("MainWindow", "Lighting"))
        self.op5_par.setText(_translate("MainWindow", "Case #"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuOption.setTitle(_translate("MainWindow", "Option"))
        self.menuMore.setTitle(_translate("MainWindow", "More"))
        self.actionF2.setText(_translate("MainWindow", "Select CSV Input"))
        self.actionF3.setText(_translate("MainWindow", "Parameter Definition"))
        self.actionF4.setText(_translate("MainWindow", "--"))
        self.actionReset.setText(_translate("MainWindow", "Reset"))
        self.actionE3.setText(_translate("MainWindow", "--"))
        self.actionE4.setText(_translate("MainWindow", "--"))
        self.actionTop_5.setText(_translate("MainWindow", "Top 5"))
        self.actionTop_10.setText(_translate("MainWindow", "Top 10"))
        self.actionM1.setText(_translate("MainWindow", "Credits"))
        self.actionM2.setText(_translate("MainWindow", "Contact"))
        self.actionTop_50.setText(_translate("MainWindow", "Top 50"))


if __name__ == "__main__":
    import sys
    app_fs=QApplication(sys.argv)
    fs_window=file_select_Window()
    app_fs.exec_()
    del app_fs
    app_plot = QtWidgets.QApplication(sys.argv)
    MainWindow_plotter = QtWidgets.QMainWindow()
    paraplot = plotter_parametric()
    paraplot.setupUi(MainWindow_plotter)
    MainWindow_plotter.show()
    app_plot.exec_()
    del app_plot

