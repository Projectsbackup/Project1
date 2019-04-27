# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setWindowModality(QtCore.Qt.NonModal)
        MainWindow.resize(858, 734)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("mjp-multijet-printing.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.Next_layer = QtWidgets.QPushButton(self.centralwidget)
        self.Next_layer.setGeometry(QtCore.QRect(610, 470, 93, 28))
        self.Next_layer.setObjectName("Next_layer")
        self.previous_layer = QtWidgets.QPushButton(self.centralwidget)
        self.previous_layer.setGeometry(QtCore.QRect(110, 480, 93, 28))
        self.previous_layer.setObjectName("previous_layer")
        self.layer = QtWidgets.QLabel(self.centralwidget)
        self.layer.setGeometry(QtCore.QRect(620, 30, 151, 271))
        self.layer.setObjectName("layer")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(20, 10, 521, 411))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.openGLWidget = QtWidgets.QOpenGLWidget(self.tab)
        self.openGLWidget.setGeometry(QtCore.QRect(50, 40, 411, 271))
        self.openGLWidget.setObjectName("openGLWidget")
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 858, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "3DP"))
        self.Next_layer.setText(_translate("MainWindow", "Next layer"))
        self.previous_layer.setText(_translate("MainWindow", "previous layer"))
        self.layer.setText(_translate("MainWindow", "Layers Display"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "Tab 1"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "Tab 2"))
        #self.tabWidget.currentChanged['int'].connect(self.tabSelected)       
    def tabSelected(self, arg=None):
       # print ('\n\t tabSelected() current Tab index =', arg)
       #print(arg)
       return arg

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

