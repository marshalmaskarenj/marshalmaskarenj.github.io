from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from PyQt5.QtWidgets import QFileDialog
import pandas as pd
import os
from PyQt5.QtCore import  QSize

def openFileDialog():
    global newarray, filename1, exportbtnval
    qfd = QFileDialog()
    fname=QFileDialog.getOpenFileNames(qfd, "Read CSV Files to scrape"," ","CSV Files (*.csv);; All Files(*)")
    filename1=fname[0]
#    newarray = readCSV(filename1)
    exportbtnval=1
#    return newarray

def readCSV(fn1):
    global luxdata, scraped_data, row_val, column_val
    row_val=ui.row_name.value()-1
    column_val=ui.column_name.value()-1
    print (row_val,column_val)
    newarray=[]#['Cell Value of '+str(row_val)+" by "+str(column_val)+" cell"]
    for fn in fn1:
        head, tail = os.path.split(fn)
#        narray=list(np.zeros((2)).astype(int))
        narray=list(np.zeros((2)))
        luxdata=pd.read_csv(fn,sep=',',header=None)
        narray[1]=luxdata.iat[row_val,column_val]
        narray[0]=tail
        newarray.append(narray)
    scraped_data=np.array(newarray)
    return newarray


def csvexport():
    newarray = readCSV(filename1)
    if exportbtnval==1:
        np.savetxt("EPcsvScrape_"+str(row_val+1)+"_by_"+str(column_val+1)+".csv", newarray, delimiter=",", fmt='%s')   

class Ui_Form(object):
    def setupUi(self, Form):
        global row_val, column_val
        Form.setObjectName("Form")
        Form.resize(121, 163)
        Form.setFixedSize(QSize(121, 163))
        Form.setStyleSheet("background-color: #41CAC6")
        self.open_csv = QtWidgets.QPushButton(Form)
        self.open_csv.setGeometry(QtCore.QRect(10, 10, 101, 31))
        self.open_csv.setStyleSheet("font-size:12px; font-family:Arial; background-color:#4976AB; color:rgb(255,255,255)")
        self.open_csv.setObjectName("open_csv")
        self.open_csv.clicked.connect(openFileDialog)
        self.export_data = QtWidgets.QPushButton(Form)
        self.export_data.setGeometry(QtCore.QRect(10, 100, 101, 31))
        self.export_data.setStyleSheet("font-size:12px; font-family:Arial; background-color:#4976AB; color:rgb(255,255,255)")
        self.export_data.setObjectName("export_data")
        self.export_data.clicked.connect(csvexport)
        self.row_name = QtWidgets.QSpinBox(Form)
        self.row_name.setGeometry(QtCore.QRect(10, 70, 51, 22))
        self.row_name.setStyleSheet("font-size:12px; font-family:Arial; background-color:#4976AB; color:rgb(255,255,255)")
        self.row_name.setObjectName("row_name")
        self.row_name.setMinimum(1)
        self.row_name.setMaximum(3000)
        self.row_name.setProperty("value", 1)
        self.column_name = QtWidgets.QSpinBox(Form)
        self.column_name.setGeometry(QtCore.QRect(61, 70, 51, 22))
        self.column_name.setStyleSheet("font-size:12px; font-family:Arial; background-color:#4976AB; color:rgb(255,255,255)")
        self.column_name.setObjectName("column_name")
        self.column_name.setMinimum(1)
        self.column_name.setMaximum(3000)
        self.column_name.setProperty("value", 1)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(20, 140, 91, 20))
        font = QtGui.QFont()
        font.setPointSize(7)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(10, 50, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(Form)
        self.label_3.setGeometry(QtCore.QRect(60, 50, 47, 13))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("")
        self.label_3.setObjectName("label_3")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.open_csv.setText(_translate("Form", "Read CSVs"))
        self.export_data.setText(_translate("Form", "Export Data"))
        self.label.setText(_translate("Form", "(c) Marshal Maskarenj"))
        self.label_2.setText(_translate("Form", "Row"))
        self.label_3.setText(_translate("Form", "Column"))

if __name__ == "__main__":
    import sys
    exportbtnval=0
    csvscrape_app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    csvscrape_app.exec_()
    del csvscrape_app
