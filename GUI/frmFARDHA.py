# This file is part of the easy fMRI distribution 
#
# Copyright (c) 2014—2021 Tony Muhammad Yousefnezhad.
#
# Website: https://easyfmri.learningbymachine.com
# GitLab:  https://gitlab.com/easyfmri/easyfmri
# GitHub:  https://github.com/easyfmri/easyfmri
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#

import os
import sys
import time
import torch
import numpy as np
import scipy.io as io
from PyQt5.QtWidgets import *
from sklearn import preprocessing
from Base.dialogs import LoadFile, SaveFile
from Base.utility import getVersion, getBuild
from GUI.frmFARDHAGUI import *
from GUI.frmMLPDialog import frmLayer
from IO.mainIO import mainIO_load, mainIO_save, reshape_1Dvector
from Hyperalignment.RDHA import RDHA


class frmFARDHA(Ui_frmFARDHA):
    ui = Ui_frmFARDHA()
    dialog = None
    # This function is run when the main form start
    # and initiate the default parameters.
    def show(self):
        global dialog
        global ui
        ui = Ui_frmFARDHA()
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        dialog = QtWidgets.QMainWindow()
        ui.setupUi(dialog)
        self.set_events(self)
        ui.tabWidget.setCurrentIndex(0)

        ui.tbModel.setRowCount(0)
        ui.tbModel.setColumnCount(2)
        ui.tbModel.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        ui.tbModel.setHorizontalHeaderLabels(['Function', 'Output Unit'])
        ui.tbModel.setColumnWidth(0, 200)
        ui.tbModel.setColumnWidth(1, 200)

        # LOSS Type
        ui.cbLossType.addItem('Mean Square Error', 'mse')
        ui.cbLossType.addItem('Soft Margin Loss', 'soft')
        ui.cbLossType.addItem('Norm', 'norm')
        ui.cbLossType.addItem('Mean', 'mean')

        # Optimization
        ui.cbOptim.addItem('Adam', 'adam')
        ui.cbOptim.addItem('SGD', 'sgd')

        # Output
        ui.cbOutAF.addItem("None", "none")
        ui.cbOutAF.addItem("ReLu", "relu")
        ui.cbOutAF.addItem("Sigmoid", "sigmoid")
        ui.cbOutAF.addItem("Tanh", "tanh")
        ui.cbOutAF.addItem("Soft Max", "softmax")
        ui.cbOutAF.addItem("Soft Min", "softmin")

        # Device
        ui.cbDevice.addItem("Auto", torch.cuda.is_available())
        ui.cbDevice.addItem("Just CPU", False)



        dialog.setWindowTitle("easy fMRI Robust Deep Hyperalignment - V" + getVersion() + "B" + getBuild())
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        dialog.setFixedSize(dialog.size())
        dialog.show()


    # This function initiate the events procedures
    def set_events(self):
        global ui
        ui.btnClose.clicked.connect(self.btnClose_click)
        ui.btnInFile.clicked.connect(self.btnInFile_click)
        ui.btnOutFile.clicked.connect(self.btnOutFile_click)
        ui.btnConvert.clicked.connect(self.btnConvert_click)
        ui.btnDelete.clicked.connect(self.btnDelete_click)
        ui.btnUp.clicked.connect(self.btnUp_click)
        ui.btnDown.clicked.connect(self.btnDown_click)
        ui.btnClearNet.clicked.connect(self.btnClearNet_click)
        ui.btnAdd.clicked.connect(self.btnAdd_click)
        ui.btnSaveNet.clicked.connect(self.btnSaveNet_click)
        ui.btnLoadNet.clicked.connect(self.btnLoadNet_click)



    def btnClose_click(self):
        global dialog
        dialog.close()

    def btnInFile_click(self):
        filename = LoadFile("Load data file ...",['Data files (*.ezx *.mat *.ezdata)'],'ezx',\
                            os.path.dirname(ui.txtInFile.text()))
        if len(filename):
            if os.path.isfile(filename):
                try:
                    data = mainIO_load(filename)
                    Keys = data.keys()

                    # Train Data
                    ui.txtITrData.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrData.addItem(key)
                        if key == "train_data":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrData.setCurrentText("train_data")

                    # Test Data
                    ui.txtITeData.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeData.addItem(key)
                        if key == "test_data":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeData.setCurrentText("test_data")

                    # Train Label
                    ui.txtITrLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrLabel.addItem(key)
                        if key == "train_label":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrLabel.setCurrentText("train_label")

                    # Test Label
                    ui.txtITeLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeLabel.addItem(key)
                        if key == "test_label":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeLabel.setCurrentText("test_label")

                    # Train mLabel
                    ui.txtITrmLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrmLabel.addItem(key)
                        if key == "train_mlabel":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrmLabel.setCurrentText("train_mlabel")
                    ui.cbmLabel.setChecked(HasDefualt)

                    # Test mLabel
                    ui.txtITemLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITemLabel.addItem(key)
                        if key == "test_mlabel":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITemLabel.setCurrentText("test_mlabel")
                    if ui.cbmLabel.isChecked():
                        ui.cbmLabel.setChecked(HasDefualt)

                    # Coordinate
                    ui.txtCol.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtCol.addItem(key)
                        if key == "coordinate":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtCol.setCurrentText("coordinate")
                    ui.cbCol.setChecked(HasDefualt)

                    # Train Design
                    ui.txtITrDM.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrDM.addItem(key)
                        if key == "train_design":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrDM.setCurrentText("train_design")
                    ui.cbDM.setChecked(HasDefualt)

                    # Test Design
                    ui.txtITeDM.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeDM.addItem(key)
                        if key == "test_design":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeDM.setCurrentText("test_design")
                    if ui.cbDM.isChecked():
                        ui.cbDM.setChecked(HasDefualt)

                    # Train Subject
                    ui.txtITrSubject.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrSubject.addItem(key)
                        if key == "train_subject":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrSubject.setCurrentText("train_subject")

                    # Test Subject
                    ui.txtITeSubject.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeSubject.addItem(key)
                        if key == "test_subject":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeSubject.setCurrentText("test_subject")

                    # Train Task
                    ui.txtITrTask.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrTask.addItem(key)
                        if key == "train_task":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrTask.setCurrentText("train_task")
                    ui.cbTask.setChecked(HasDefualt)

                    # Test Task
                    ui.txtITeTask.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeTask.addItem(key)
                        if key == "test_task":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeTask.setCurrentText("test_task")
                    if ui.cbTask.isChecked():
                        ui.cbTask.setChecked(HasDefualt)

                    # Train Run
                    ui.txtITrRun.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrRun.addItem(key)
                        if key == "train_run":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrRun.setCurrentText("train_run")
                    ui.cbRun.setChecked(HasDefualt)

                    # Test Run
                    ui.txtITeRun.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeRun.addItem(key)
                        if key == "test_run":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeRun.setCurrentText("test_run")
                    if ui.cbRun.isChecked():
                        ui.cbRun.setChecked(HasDefualt)

                    # Train Counter
                    ui.txtITrCounter.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrCounter.addItem(key)
                        if key == "train_counter":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrCounter.setCurrentText("train_counter")
                    ui.cbCounter.setChecked(HasDefualt)

                    # Test Counter
                    ui.txtITeCounter.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeCounter.addItem(key)
                        if key == "test_counter":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeCounter.setCurrentText("test_counter")
                    if ui.cbCounter.isChecked():
                        ui.cbCounter.setChecked(HasDefualt)

                    # Condition
                    ui.txtCond.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtCond.addItem(key)
                        if key == "condition":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtCond.setCurrentText("condition")
                    ui.cbCond.setChecked(HasDefualt)

                    # Train NScan
                    ui.txtITrScan.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITrScan.addItem(key)
                        if key == "train_nscan":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITrScan.setCurrentText("train_nscan")
                    ui.cbNScan.setChecked(HasDefualt)

                    # Test NScan
                    ui.txtITeScan.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtITeScan.addItem(key)
                        if key == "test_nscan":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtITeScan.setCurrentText("test_nscan")
                    if ui.cbNScan.isChecked():
                        ui.cbNScan.setChecked(HasDefualt)

                    # FoldID
                    ui.txtFoldID.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtFoldID.addItem(key)
                        if key == "FoldID":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtFoldID.setCurrentText("FoldID")
                    ui.cbFoldID.setChecked(HasDefualt)

                    # FoldInfo
                    ui.txtFoldInfo.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtFoldInfo.addItem(key)
                        if key == "FoldInfo":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtFoldInfo.setCurrentText("FoldInfo")
                    ui.cbFoldInfo.setChecked(HasDefualt)

                    # set number of features
                    XShape = np.shape(data[ui.txtITrData.currentText()])
                    ui.txtNumFea.setMaximum(0)
                    ui.txtNumFea.setMaximum(XShape[1])
                    ui.txtNumFea.setValue(0)
                    ui.lblFeaNum.setText("1 ... " + str(XShape[1]) + ", 0 = auto")
                    if ui.cbFoldID.isChecked():
                        ui.lbFoldID.setText("ID=" + str(data[ui.txtFoldID.currentText()][0][0]))


                    ui.txtInFile.setText(filename)
                except Exception as e:
                    print(e)
                    print("Cannot load data file!")
                    return
            else:
                print("File not found!")

    def btnOutFile_click(self):
        ofile = SaveFile("Save data file ...",['Data files (*.ezx *.mat)'],'ezx',\
                             os.path.dirname(ui.txtOutFile.text()))
        if len(ofile):
            ui.txtOutFile.setText(ofile)

    def btnConvert_click(self):
        totalTime = 0
        msgBox = QMessageBox()

        LossType    = ui.cbLossType.currentData()
        Optim       = ui.cbOptim.currentData()

        try:
            Epoch = np.int32(ui.txtEpoch.text())
        except:
            msgBox.setText("Number of epoch is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Batch = np.int32(ui.txtBatch.text())
        except:
            msgBox.setText("Number of batch is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Iter = np.int32(ui.txtIter.text())
        except:
            msgBox.setText("Number of iteration is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            LearningRate = np.float32(ui.txtRate.text())
        except:
            msgBox.setText("Learning rate is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Alpha = np.float32(ui.txtAlpha.text())
        except:
            msgBox.setText("Alpha is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Per = np.float32(ui.txtPer.text())
        except:
            msgBox.setText("Percentage of data per epoch is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        if Per <= 0:
            msgBox.setText("Percentage of data per epoch must be greater than 0!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        if Per > 1:
            msgBox.setText("Percentage of data per epoch must be smaller than 1!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        TrFoldErr = list()
        TeFoldErr = list()
        try:
            FoldFrom = np.int32(ui.txtFoldFrom.text())
            FoldTo   = np.int32(ui.txtFoldTo.text())
        except:
            print("Please check fold parameters!")
            return

        if FoldTo < FoldFrom:
            print("Please check fold parameters!")
            return

        for fold_all in range(FoldFrom, FoldTo+1):
            tic = time.time()
            # Regularization
            try:
                Regularization = np.float(ui.txtRegularization.text())
            except:
                msgBox.setText("Regularization value is wrong!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            # OutFile
            OutFile = ui.txtOutFile.text()
            OutFile = OutFile.replace("$FOLD$", str(fold_all))
            if not len(OutFile):
                msgBox.setText("Please enter out file!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            # InFile
            InFile = ui.txtInFile.text()
            InFile = InFile.replace("$FOLD$", str(fold_all))
            if not len(InFile):
                msgBox.setText("Please enter input file!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not os.path.isfile(InFile):
                msgBox.setText("Input file not found!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            InData = mainIO_load(InFile)
            OutData = dict()
            OutData["imgShape"] = reshape_1Dvector(InData["imgShape"])

            # Data
            if not len(ui.txtITrData.currentText()):
                msgBox.setText("Please enter Input Train Data variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not len(ui.txtITeData.currentText()):
                msgBox.setText("Please enter Input Test Data variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not len(ui.txtOTrData.text()):
                msgBox.setText("Please enter Output Train Data variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not len(ui.txtOTeData.text()):
                msgBox.setText("Please enter Output Test Data variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            try:
                XTr = InData[ui.txtITrData.currentText()]
                XTe = InData[ui.txtITeData.currentText()]

                if ui.cbScale.isChecked() and not ui.rbScale.isChecked():
                    XTr = preprocessing.scale(XTr)
                    XTe = preprocessing.scale(XTe)
                    print("Whole of data is scaled X~N(0,1).")
            except:
                print("Cannot load data")
                return

            # NComponent
            try:
                NumFea = int(ui.txtNumFea.text())
            except:
                msgBox.setText("Number of features is wrong!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if NumFea < 0:
                msgBox.setText("Number of features must be greater than zero!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if NumFea > np.shape(XTr)[1]:
                msgBox.setText("Number of features is wrong!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if NumFea == 0:
                NumFea = None

            # Label
            if not len(ui.txtITrLabel.currentText()):
                    msgBox.setText("Please enter Train Input Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
            if not len(ui.txtITeLabel.currentText()):
                    msgBox.setText("Please enter Test Input Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
            if not len(ui.txtOTrLabel.text()):
                    msgBox.setText("Please enter Train Output Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
            if not len(ui.txtOTeLabel.text()):
                    msgBox.setText("Please enter Test Output Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
            try:
                OutData[ui.txtOTrLabel.text()] = reshape_1Dvector(InData[ui.txtITrLabel.currentText()])
                OutData[ui.txtOTeLabel.text()] = reshape_1Dvector(InData[ui.txtITeLabel.currentText()])
            except:
                print("Cannot load labels!")

            # Subject
            if not len(ui.txtITrSubject.currentText()):
                msgBox.setText("Please enter Train Input Subject variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not len(ui.txtITeSubject.currentText()):
                msgBox.setText("Please enter Test Input Subject variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not len(ui.txtOTrSubject.text()):
                msgBox.setText("Please enter Train Output Subject variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            if not len(ui.txtOTeSubject.text()):
                msgBox.setText("Please enter Test Output Subject variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
            try:
                TrSubject = InData[ui.txtITrSubject.currentText()]
                OutData[ui.txtOTrSubject.text()] = reshape_1Dvector(TrSubject)
                TeSubject = InData[ui.txtITeSubject.currentText()]
                OutData[ui.txtOTeSubject.text()] = reshape_1Dvector(TeSubject)
            except:
                print("Cannot load Subject IDs")
                return

            # Task
            if ui.cbTask.isChecked():
                if not len(ui.txtITrTask.currentText()):
                    msgBox.setText("Please enter Input Train Task variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtITeTask.currentText()):
                    msgBox.setText("Please enter Input Test Task variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTrTask.text()):
                    msgBox.setText("Please enter Output Train Task variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTeTask.text()):
                    msgBox.setText("Please enter Output Test Task variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    TrTask = np.asarray(InData[ui.txtITrTask.currentText()])
                    OutData[ui.txtOTrTask.text()] = reshape_1Dvector(TrTask)
                    TeTask = np.asarray(InData[ui.txtITeTask.currentText()])
                    OutData[ui.txtOTeTask.text()] = reshape_1Dvector(TeTask)
                    TrTaskIndex = TrTask.copy()
                    for tasindx, tas in enumerate(np.unique(TrTask)):
                        TrTaskIndex[TrTask == tas] = tasindx + 1
                    TeTaskIndex = TeTask.copy()
                    for tasindx, tas in enumerate(np.unique(TeTask)):
                        TeTaskIndex[TeTask == tas] = tasindx + 1
                except:
                    print("Cannot load Tasks!")
                    return

            # Run
            if ui.cbRun.isChecked():
                if not len(ui.txtITrRun.currentText()):
                    msgBox.setText("Please enter Train Input Run variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtITeRun.currentText()):
                    msgBox.setText("Please enter Test Input Run variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTrRun.text()):
                    msgBox.setText("Please enter Train Output Run variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTeRun.text()):
                    msgBox.setText("Please enter Test Output Run variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    TrRun = InData[ui.txtITrRun.currentText()]
                    OutData[ui.txtOTrRun.text()] = reshape_1Dvector(TrRun)
                    TeRun = InData[ui.txtITeRun.currentText()]
                    OutData[ui.txtOTeRun.text()] = reshape_1Dvector(TeRun)
                except:
                    print("Cannot load Runs!")
                    return

            # Counter
            if ui.cbCounter.isChecked():
                if not len(ui.txtITrCounter.currentText()):
                    msgBox.setText("Please enter Train Input Counter variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtITeCounter.currentText()):
                    msgBox.setText("Please enter Test Input Counter variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTrCounter.text()):
                    msgBox.setText("Please enter Train Output Counter variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTeCounter.text()):
                    msgBox.setText("Please enter Test Output Counter variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    TrCounter = InData[ui.txtITrCounter.currentText()]
                    OutData[ui.txtOTrCounter.text()] = reshape_1Dvector(TrCounter)
                    TeCounter = InData[ui.txtITeCounter.currentText()]
                    OutData[ui.txtOTeCounter.text()] = reshape_1Dvector(TeCounter)
                except:
                    print("Cannot load Counters!")
                    return

            # Matrix Label
            if ui.cbmLabel.isChecked():
                if not len(ui.txtITrmLabel.currentText()):
                    msgBox.setText("Please enter Train Input Matrix Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtITemLabel.currentText()):
                    msgBox.setText("Please enter Test Input Matrix Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTrmLabel.text()):
                    msgBox.setText("Please enter Train Output Matrix Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTemLabel.text()):
                    msgBox.setText("Please enter Test Output Matrix Label variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOTrmLabel.text()] = InData[ui.txtITrmLabel.currentText()]
                    OutData[ui.txtOTemLabel.text()] = InData[ui.txtITemLabel.currentText()]
                except:
                    print("Cannot load matrix lables!")
                    return

            # Design
            if ui.cbDM.isChecked():
                if not len(ui.txtITrDM.currentText()):
                    msgBox.setText("Please enter Train Input Design Matrix variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtITeDM.currentText()):
                    msgBox.setText("Please enter Test Input Design Matrix variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTrDM.text()):
                    msgBox.setText("Please enter Train Output Design Matrix variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTeDM.text()):
                    msgBox.setText("Please enter Test Output Design Matrix variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOTrDM.text()] = InData[ui.txtITrDM.currentText()]
                    OutData[ui.txtOTeDM.text()] = InData[ui.txtITeDM.currentText()]
                except:
                    print("Cannot load design matrices!")
                    return

            # Coordinate
            if ui.cbCol.isChecked():
                if not len(ui.txtCol.currentText()):
                    msgBox.setText("Please enter Coordinator variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOCol.text()):
                    msgBox.setText("Please enter Coordinator variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOCol.text()] = InData[ui.txtCol.currentText()]
                except:
                    print("Cannot load coordinator!")
                    return

            # Condition
            if ui.cbCond.isChecked():
                if not len(ui.txtCond.currentText()):
                    msgBox.setText("Please enter Condition variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOCond.text()):
                    msgBox.setText("Please enter Condition variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOCond.text()] = InData[ui.txtCond.currentText()]
                except:
                    print("Cannot load conditions!")
                    return

            # FoldID
            if ui.cbFoldID.isChecked():
                if not len(ui.txtFoldID.currentText()):
                    msgBox.setText("Please enter FoldID variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOFoldID.text()):
                    msgBox.setText("Please enter FoldID variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOFoldID.text()] = reshape_1Dvector(InData[ui.txtFoldID.currentText()])
                except:
                    print("Cannot load Fold ID!")
                    return

            # FoldInfo
            if ui.cbFoldInfo.isChecked():
                if not len(ui.txtFoldInfo.currentText()):
                    msgBox.setText("Please enter FoldInfo variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOFoldInfo.text()):
                    msgBox.setText("Please enter FoldInfo variable name!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOFoldInfo.text()] = InData[ui.txtFoldInfo.currentText()]
                except:
                    print("Cannot load Fold Info!")
                    return
                pass

            # Number of Scan
            if ui.cbNScan.isChecked():
                if not len(ui.txtITrScan.currentText()):
                    msgBox.setText("Please enter Number of Scan variable name for Input Train!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtITeScan.currentText()):
                    msgBox.setText("Please enter Number of Scan variable name for Input Test!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTrScan.text()):
                    msgBox.setText("Please enter Number of Scan variable name for Output Train!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                if not len(ui.txtOTeScan.text()):
                    msgBox.setText("Please enter Number of Scan variable name for Output Test!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                try:
                    OutData[ui.txtOTrScan.text()] = reshape_1Dvector(InData[ui.txtITrScan.currentText()])
                    OutData[ui.txtOTeScan.text()] = reshape_1Dvector(InData[ui.txtITeScan.currentText()])
                except:
                    print("Cannot load NScan!")
                    return

            # Train Analysis Level
            print("Calculating Analysis Level for Training Set ...")
            TrGroupFold = None
            FoldStr = ""
            if ui.cbFSubject.isChecked():
                if not ui.rbFRun.isChecked():
                    TrGroupFold = TrSubject
                    FoldStr = "Subject"
                else:
                    TrGroupFold = np.concatenate((TrSubject,TrRun))
                    FoldStr = "Subject+Run"

            if ui.cbFTask.isChecked():
                TrGroupFold = np.concatenate((TrGroupFold,TrTaskIndex)) if TrGroupFold is not None else TrTaskIndex
                FoldStr = FoldStr + "+Task"

            if ui.cbFCounter.isChecked():
                TrGroupFold = np.concatenate((TrGroupFold,TrCounter)) if TrGroupFold is not None else TrCounter
                FoldStr = FoldStr + "+Counter"

            TrGroupFold = np.transpose(TrGroupFold)

            TrUniqFold = np.array(list(set(tuple(i) for i in TrGroupFold.tolist())))

            TrFoldIDs = np.arange(len(TrUniqFold)) + 1

            TrListFold = list()
            for gfold in TrGroupFold:
                for ufoldindx, ufold in enumerate(TrUniqFold):
                    if (ufold == gfold).all():
                        currentID = TrFoldIDs[ufoldindx]
                        break
                TrListFold.append(currentID)
            TrListFold = np.int32(TrListFold)
            TrListFoldUniq = np.unique(TrListFold)


            # Test Analysis Level
            print("Calculating Analysis Level for Testing Set ...")
            TeGroupFold = None
            if ui.cbFSubject.isChecked():
                if not ui.rbFRun.isChecked():
                    TeGroupFold = TeSubject
                else:
                    TeGroupFold = np.concatenate((TeSubject,TeRun))

            if ui.cbFTask.isChecked():
                TeGroupFold = np.concatenate((TeGroupFold,TeTaskIndex)) if TeGroupFold is not None else TeTaskIndex

            if ui.cbFCounter.isChecked():
                TeGroupFold = np.concatenate((TeGroupFold,TeCounter)) if TeGroupFold is not None else TeCounter

            TeGroupFold = np.transpose(TeGroupFold)

            TeUniqFold = np.array(list(set(tuple(i) for i in TeGroupFold.tolist())))

            TeFoldIDs = np.arange(len(TeUniqFold)) + 1

            TeListFold = list()
            for gfold in TeGroupFold:
                for ufoldindx, ufold in enumerate(TeUniqFold):
                    if (ufold == gfold).all():
                        currentID = TeFoldIDs[ufoldindx]
                        break
                TeListFold.append(currentID)
            TeListFold = np.int32(TeListFold)
            TeListFoldUniq = np.unique(TeListFold)

            # Train Partition
            print("Partitioning Training Data ...")
            TrX = list()
            TrShape = None
            for foldindx, fold in enumerate(TrListFoldUniq):
                dat = XTr[np.where(TrListFold == fold)]
                if ui.cbScale.isChecked() and ui.rbScale.isChecked():
                    dat = preprocessing.scale(dat)
                    print("Data belong to View " + str(foldindx + 1) + " is scaled X~N(0,1).")

                TrX.append(dat)
                if TrShape is None:
                    TrShape = np.shape(dat)
                else:
                    if not(TrShape == np.shape(dat)):
                        print("ERROR: Train, Reshape problem for Fold " + str(foldindx + 1) + ", Shape: " + str(np.shape(dat)))
                        return
                print("Train: View " + str(foldindx + 1) + " is extracted. Shape: " + str(np.shape(dat)))

            print("Training Shape: " + str(np.shape(TrX)))

            # Test Partition
            print("Partitioning Testing Data ...")
            TeX = list()
            TeShape = None
            for foldindx, fold in enumerate(TeListFoldUniq):
                dat = XTe[np.where(TeListFold == fold)]
                if ui.cbScale.isChecked() and ui.rbScale.isChecked():
                    dat = preprocessing.scale(dat)
                    print("Data belong to View " + str(foldindx + 1) + " is scaled X~N(0,1).")
                TeX.append(dat)
                if TeShape is None:
                    TeShape = np.shape(dat)
                else:
                    if not(TeShape == np.shape(dat)):
                        print("Test: Reshape problem for Fold " + str(foldindx + 1))
                        return
                print("Test: View " + str(foldindx + 1) + " is extracted.")

            print("Testing Shape: " + str(np.shape(TeX)))

            # Net Shape & Activation
            NetShape = None
            Active   = None

            if ui.tbModel.rowCount() > 0:
                for rowID in range(ui.tbModel.rowCount()):
                    NetShape = [int(ui.tbModel.item(rowID, 1).text())] if NetShape is None else np.concatenate((NetShape, [int(ui.tbModel.item(rowID, 1).text())]))

                    afun = str.lower(ui.tbModel.item(rowID, 0).text())
                    if afun == 'none':
                        afun = None
                    Active   = [afun] if Active is None else np.concatenate((Active, [afun]))


            afun = str.lower(ui.cbOutAF.currentData())
            if afun == 'none':
                afun = None

            NetShape = [NumFea] if NetShape is None else np.concatenate((NetShape, [NumFea]))
            Active = [afun] if Active is None else np.concatenate((Active, [afun]))

            try:
                model = RDHA(net_shape=NetShape, activation=Active, loss_type=LossType, optim=Optim, iteration=Iter,\
                             epoch=Epoch, epoch_internal_iteration=Per, batch_size=Batch, learning_rate=LearningRate,\
                             alpha=Alpha,regularization=Regularization,norm1_enable=ui.cbNorm1.isChecked(),\
                             norm2_enable=ui.cbNorm2.isChecked(), best_result_enable=ui.cbBest.isChecked(),\
                             gpu_enable=ui.cbDevice.currentData())

                print("Running Hyperalignment on Training Data ...")
                model.train(views=TrX, verbose=ui.cbVerbose.isChecked())
                G = model.Share
                print("Running Hyperalignment on Testing Data ...")
                model.test(views=TeX,verbose=ui.cbVerbose.isChecked())
            except Exception as e:
                print(str(e))
                msgBox.setText(str(e))
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False


            # Train Dot Product
            print("Producting Training Data ...")
            TrHX = None
            TrErr = None
            for XiRi in model.TrainFeatures:
                TrHX = np.concatenate((TrHX, XiRi)) if TrHX is not None else XiRi
                TrErr = TrErr + (G - XiRi) if TrErr is not None else G - XiRi

            OutData[ui.txtOTrData.text()] = TrHX
            foldindx = foldindx + 1
            TrErr = TrErr / foldindx
            print("Train: alignment error ", np.linalg.norm(TrErr))
            TrFoldErr.append(np.linalg.norm(TrErr))

            # Train Dot Product
            print("Producting Testing Data ...")
            TeHX = None
            TeErr = None
            for XiRi in model.TestFeatures:
                TeHX = np.concatenate((TeHX, XiRi)) if TeHX is not None else XiRi
                TeErr = TeErr + (G - XiRi) if TeErr is not None else G - XiRi
            OutData[ui.txtOTeData.text()] = TeHX
            foldindx = foldindx + 1
            TeErr = TeErr / foldindx
            print("Test: alignment error ", np.linalg.norm(TeErr))
            TeFoldErr.append(np.linalg.norm(TeErr))

            HAParam = dict()
            HAParam["Share"] = G
            HAParam["Level"] = FoldStr
            OutData["FunctionalAlignment"] = HAParam
            OutData["Runtime"] = time.time() - tic
            totalTime += OutData["Runtime"]
            print("Saving ...")
            mainIO_save(OutData, OutFile)
            print("Fold " + str(fold_all) + " is DONE: " + OutFile)

        print("Training -> Alignment Error: mean " + str(np.mean(TrFoldErr)) + " std " + str(np.std(TrFoldErr)))
        print("Testing  -> Alignment Error: mean " + str(np.mean(TeFoldErr)) + " std " + str(np.std(TeFoldErr)))
        print("Runtime: ", totalTime)
        print("Robust Deep Hyperalignment is done.")
        msgBox.setText("Robust Deep Hyperalignment is done.")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()



    def btnDelete_click(self):
        currentRowID = ui.tbModel.currentRow()
        if currentRowID >= 0:
            ui.tbModel.removeRow(currentRowID)


    def btnUp_click(self):
        row = ui.tbModel.currentRow()
        column = ui.tbModel.currentColumn()
        if row > 0:
            ui.tbModel.insertRow(row - 1)
            for i in range(ui.tbModel.columnCount()):
                ui.tbModel.setItem(row - 1, i, ui.tbModel.takeItem(row + 1, i))
                ui.tbModel.setCurrentCell(row-1,column)
            ui.tbModel.removeRow(row+1)


    def btnDown_click(self):
        row = ui.tbModel.currentRow()
        column = ui.tbModel.currentColumn()
        if row < ui.tbModel.rowCount() - 1:
            ui.tbModel.insertRow(row + 2)
            for i in range(ui.tbModel.columnCount()):
               ui.tbModel.setItem(row + 2, i, ui.tbModel.takeItem(row, i))
               ui.tbModel.setCurrentCell(row + 2, column)
            ui.tbModel.removeRow(row)


    def btnClearNet_click(self):
        ui.tbModel.clear()
        ui.tbModel.setRowCount(0)
        ui.tbModel.setColumnCount(2)
        ui.tbModel.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        ui.tbModel.setHorizontalHeaderLabels(['Function', 'Output Unit'])
        ui.tbModel.setColumnWidth(0, 200)
        ui.tbModel.setColumnWidth(1, 200)


    def btnAdd_click(self):
        frmal = frmLayer()
        if frmal.isAdd:
            id = ui.tbModel.rowCount()
            ui.tbModel.insertRow(id)
            typeItm = QTableWidgetItem(frmal.func)
            typeItm.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            ui.tbModel.setItem(id, 0, typeItm)
            FunItm = QTableWidgetItem(str(frmal.unit))
            FunItm.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            ui.tbModel.setItem(id, 1, FunItm)


    def btnSaveNet_click(self):
        ofile = SaveFile("Save network model ...", ['Model files (*.model)'], 'model', os.path.dirname(ui.txtOutFile.text()))
        if len(ofile):
            Model = dict()
            Model["NumFea"] = ui.txtNumFea.value()
            Model["OutAF"]  = ui.cbOutAF.currentIndex()
            if ui.tbModel.rowCount() > 0:
                for rowID in range(ui.tbModel.rowCount()):
                    Model["hidden" + str(rowID)] = np.array([ui.tbModel.item(rowID, 0).text(), ui.tbModel.item(rowID, 1).text()], dtype=object)
            io.savemat(ofile, mdict=Model, appendmat=False)


    def btnLoadNet_click(self):
        ifile = LoadFile("Load network model ...",['Model files (*.model)'],'model', os.path.dirname(ui.txtOutFile.text()))
        if len(ifile):
            Model = io.loadmat(ifile, appendmat=False)

            try:
                ui.txtNumFea.setValue(int(Model["NumFea"][0][0]))
                ui.cbOutAF.setCurrentIndex(int(Model["OutAF"][0][0]))
                rowCounter = 0
                for key in Model.keys():
                    if str.lower(key).find("hidden") >= 0:
                        rowCounter += 1
                print("Number of hidden layer is ", rowCounter)
                ui.tbModel.clear()
                ui.tbModel.setRowCount(0)
                ui.tbModel.setColumnCount(2)
                ui.tbModel.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
                ui.tbModel.setHorizontalHeaderLabels(['Function', 'Output Unit'])
                ui.tbModel.setColumnWidth(0, 200)
                ui.tbModel.setColumnWidth(1, 200)
                for rowID in range(rowCounter):
                    id = ui.tbModel.rowCount()
                    ui.tbModel.insertRow(id)
                    typeItm = QTableWidgetItem(Model["hidden" + str(rowID)][0][0][0])
                    typeItm.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    ui.tbModel.setItem(id, 0, typeItm)
                    FunItm = QTableWidgetItem(str(int(Model["hidden" + str(rowID)][0][1][0])))
                    FunItm.setFlags(QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                    ui.tbModel.setItem(id, 1, FunItm)
            except Exception as e:
                print(str(e))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frmFARDHA.show(frmFARDHA)
    sys.exit(app.exec_())