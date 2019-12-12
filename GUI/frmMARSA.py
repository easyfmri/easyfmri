# Copyright (c) 2014--2020 Tony (Muhammad) Yousefnezhad
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import time
import numpy as np
import scipy.io as io
from PyQt5.QtWidgets import *
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error
from Base.dialogs import LoadFile, SaveFile
from Base.utility import getVersion, getBuild, SimilarityMatrixBetweenClass
from GUI.frmMARSAGUI import *

# Plot
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt



class frmMARSA(Ui_frmMARSA):
    ui = Ui_frmMARSA()
    dialog = None
    # This function is run when the main form start
    # and initiate the default parameters.
    def show(self):
        global dialog
        global ui
        ui = Ui_frmMARSA()
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        dialog = QtWidgets.QMainWindow()
        ui.setupUi(dialog)
        self.set_events(self)
        ui.tabWidget.setCurrentIndex(0)

        dialog.setWindowTitle("easy fMRI Session Level Representational Similarity Analysis (RSA) - V" + getVersion() + "B" + getBuild())
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        dialog.setFixedSize(dialog.size())
        dialog.show()


    # This function initiate the events procedures
    def set_events(self):
        global ui
        ui.btnClose.clicked.connect(self.btnClose_click)
        ui.btnInFile.clicked.connect(self.btnInFile_click)
        ui.btnRef.clicked.connect(self.btnRefresh_click)
        ui.btnOutFile.clicked.connect(self.btnOutFile_click)
        ui.btnConvert.clicked.connect(self.btnConvert_click)
        ui.btnRedraw.clicked.connect(self.btnRedraw_click)


    def btnClose_click(self):
        global dialog
        dialog.close()


    def btnInFile_click(self):
        filename = LoadFile("Load MatLab data file ...",['MatLab files (*.mat)'],'mat',\
                            os.path.dirname(ui.txtInFile.text()))
        if len(filename):
            if os.path.isfile(filename):
                try:
                    print("Loading ...")
                    data = io.loadmat(filename)
                    Keys = data.keys()

                    # Data
                    ui.txtData.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtData.addItem(key)
                        if key == "data":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtData.setCurrentText("data")
                        print("Data Shape: ", np.shape(data["data"]))


                    # Label
                    ui.txtLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtLabel.addItem(key)
                        if key == "label":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtLabel.setCurrentText("label")
                        Labels = data[ui.txtLabel.currentText()]
                        Labels = np.unique(Labels)
                        print("Number of labels: ", np.shape(Labels)[0])
                        print("Labels:")
                        print(Labels)
                        ui.txtClass.clear()
                        for lbl in Labels:
                            ui.txtClass.append(str(lbl))

                    # Design
                    ui.txtDesign.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtDesign.addItem(key)
                        if key == "design":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtDesign.setCurrentText("design")

                    # Subject
                    ui.txtSubject.clear()
                    ui.txtSubjectVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtSubject.addItem(key)
                        if key == "subject":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtSubject.setCurrentText("subject")
                        values = np.unique(data["subject"])
                        for val in values:
                            ui.txtSubjectVal.addItem(str(val))

                    # Run
                    ui.txtRun.clear()
                    ui.txtRunVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtRun.addItem(key)
                        if key == "run":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtRun.setCurrentText("run")
                        values = np.unique(data["run"])
                        for val in values:
                            ui.txtRunVal.addItem(str(val))

                    # Counter
                    ui.txtCounter.clear()
                    ui.txtCounterVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtCounter.addItem(key)
                        if key == "counter":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtCounter.setCurrentText("counter")
                        values = np.unique(data["counter"])
                        for val in values:
                            ui.txtCounterVal.addItem(str(val))

                    # Task
                    ui.txtTask.clear()
                    ui.txtTaskVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtTask.addItem(key)
                        if key == "task":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtTask.setCurrentText("task")
                        values = np.unique(data["task"])
                        for val in values:
                            ui.txtTaskVal.addItem(str(val[0]))

                    ui.txtInFile.setText(filename)
                    print("DONE.")
                except Exception as e:
                    print(e)
                    print("Cannot load data file!")
                    return
            else:
                print("File not found!")


    def btnRefresh_click(self):
        filename = ui.txtInFile.text()
        if len(filename):
            if os.path.isfile(filename):
                try:
                    data = io.loadmat(filename)
                    Keys = data.keys()
                    # Data
                    ui.txtData.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtData.addItem(key)
                        if key == "data":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtData.setCurrentText("data")

                    # Label
                    ui.txtLabel.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtLabel.addItem(key)
                        if key == "label":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtLabel.setCurrentText("label")
                        Labels = data[ui.txtLabel.currentText()]
                        Labels = np.unique(Labels)
                        ui.txtClass.clear()
                        for lbl in Labels:
                            ui.txtClass.append(str(lbl))
                    # Design
                    ui.txtDesign.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtDesign.addItem(key)
                        if key == "design":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtDesign.setCurrentText("design")

                    # Subject
                    ui.txtSubject.clear()
                    ui.txtSubjectVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtSubject.addItem(key)
                        if key == "subject":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtSubject.setCurrentText("subject")
                        values = np.unique(data["subject"])
                        for val in values:
                            ui.txtSubjectVal.addItem(str(val))

                    # Run
                    ui.txtRun.clear()
                    ui.txtRunVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtRun.addItem(key)
                        if key == "run":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtRun.setCurrentText("run")
                        values = np.unique(data["run"])
                        for val in values:
                            ui.txtRunVal.addItem(str(val))

                    # Counter
                    ui.txtCounter.clear()
                    ui.txtCounterVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtCounter.addItem(key)
                        if key == "counter":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtCounter.setCurrentText("counter")
                        values = np.unique(data["counter"])
                        for val in values:
                            ui.txtCounterVal.addItem(str(val))

                    # Task
                    ui.txtTask.clear()
                    ui.txtTaskVal.clear()
                    HasDefualt = False
                    for key in Keys:
                        ui.txtTask.addItem(key)
                        if key == "task":
                            HasDefualt = True
                    if HasDefualt:
                        ui.txtTask.setCurrentText("task")
                        values = np.unique(data["task"])
                        for val in values:
                            ui.txtTaskVal.addItem(str(val[0]))

                    ui.txtInFile.setText(filename)
                except Exception as e:
                    print(e)
                    print("Cannot load data file!")
                    return
            else:
                print("File not found!")


    def btnOutFile_click(self):
        ofile = SaveFile("Save result file ...",['Result files (*.mat)'],'mat',\
                             os.path.dirname(ui.txtOutFile.text()))
        if len(ofile):
            ui.txtOutFile.setText(ofile)


    def btnConvert_click(self):
        msgBox = QMessageBox()
        tStart = time.time()
        if not ui.cbCov.isChecked() and not ui.cbCorr.isChecked():
            msgBox.setText("At least, you must select one metric!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        # Filter
        try:
            Filter = ui.txtFilter.text()
            if not len(Filter):
                Filter = None
            else:
                Filter = Filter.replace("\'", " ").replace(",", " ").replace("[", "").replace("]","").split()
                Filter = np.int32(Filter)
        except:
            print("Filter is wrong!")
            return

        # OutFile
        OutFile = ui.txtOutFile.text()
        if not len(OutFile):
            msgBox.setText("Please enter out file!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        OutData = dict()

        # InFile
        InFile = ui.txtInFile.text()
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
        print("Loading ...")
        InData = io.loadmat(InFile)

        # Data
        if not len(ui.txtData.currentText()):
            msgBox.setText("Please enter Input Data variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        # Label
        if not len(ui.txtLabel.currentText()):
                msgBox.setText("Please enter Train Label variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

        # Design
        if not len(ui.txtDesign.currentText()):
            msgBox.setText("Please enter Input Design variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            Design = InData[ui.txtDesign.currentText()]
        except:
            msgBox.setText("Design value is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            X = InData[ui.txtData.currentText()]
            L = InData[ui.txtLabel.currentText()][0]
        except:
            print("Cannot load data or label")
            return

        # Task
        if not len(ui.txtTask.currentText()):
                msgBox.setText("Please enter Task variable name!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False
        # Task Val
        if not len(ui.txtTaskVal.currentText()):
                msgBox.setText("Please enter Task value!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

        try:
            TaskIDTitle = ui.txtTaskVal.currentText()
        except:
            msgBox.setText("Task value is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        try:
            TaskTitle = InData[ui.txtTask.currentText()][0]
        except:
            msgBox.setText("Task variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        TaskTitleUnique = np.unique(TaskTitle)
        Task = np.zeros(np.shape(TaskTitle))

        for ttinx, tt in enumerate(TaskTitle):
            for ttlinx, ttl in enumerate(TaskTitleUnique):
                if tt[0] == ttl:
                    Task[ttinx] = ttlinx + 1
                    break

        for ttlinx, ttl in enumerate(TaskTitleUnique):
            if TaskIDTitle == ttl:
                TaskID = ttlinx + 1
                break

        OutData["Task"] = TaskIDTitle

        # Subject
        if not len(ui.txtSubject.currentText()):
            msgBox.setText("Please enter Subject variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        # Subject Val
        if not len(ui.txtSubjectVal.currentText()):
            msgBox.setText("Please enter Subject value!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            SubID = np.int32(ui.txtSubjectVal.currentText())
        except:
            msgBox.setText("Subject value is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            Sub = InData[ui.txtSubject.currentText()][0]
        except:
            msgBox.setText("Subject variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        OutData["SubjectID"] = SubID

        # Run
        if not len(ui.txtRun.currentText()):
            msgBox.setText("Please enter Run variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        # Run Val
        if not len(ui.txtRunVal.currentText()):
            msgBox.setText("Please enter Run value!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            RunID = np.int32(ui.txtRunVal.currentText())
        except:
            msgBox.setText("Run value is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            Run = InData[ui.txtRun.currentText()][0]
        except:
            msgBox.setText("Run variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        OutData["RunID"] = RunID

        # Counter
        if not len(ui.txtCounter.currentText()):
            msgBox.setText("Please enter Counter variable name!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        # Counter Val
        if not len(ui.txtCounterVal.currentText()):
            msgBox.setText("Please enter Counter value!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            ConID = np.int32(ui.txtCounterVal.currentText())
        except:
            msgBox.setText("Counter value is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        try:
            Con = InData[ui.txtCounter.currentText()][0]
        except:
            msgBox.setText("Counter variable name is wrong!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False
        OutData["CounterID"] = ConID


        if Filter is not None:
            for fil in Filter:
                # Remove Training Set
                labelIndx = np.where(L == fil)[0]
                Design = np.delete(Design, labelIndx, axis=0)
                X = np.delete(X, labelIndx, axis=0)
                L = np.delete(L, labelIndx, axis=0)
                Task = np.delete(Task, labelIndx, axis=0)
                Sub = np.delete(Sub, labelIndx, axis=0)
                Run = np.delete(Run, labelIndx, axis=0)
                Con = np.delete(Con, labelIndx, axis=0)
                print("Class ID = " + str(fil) + " is removed from data.")

        # Select Task
        TaskIndex = np.where(Task == TaskID)
        Design  = Design[TaskIndex,:][0]
        X       = X[TaskIndex,:][0]
        L       = L[TaskIndex]
        Sub     = Sub[TaskIndex]
        Run     = Run[TaskIndex]
        Con     = Con[TaskIndex]
        # Select Subject
        SubIndex = np.where(Sub == SubID)
        Design  = Design[SubIndex,:][0]
        X       = X[SubIndex,:][0]
        L       = L[SubIndex]
        Run     = Run[SubIndex]
        Con     = Con[SubIndex]
        # Select Counter
        ConIndex = np.where(Con == ConID)
        Design  = Design[ConIndex,:][0]
        X       = X[ConIndex,:][0]
        L       = L[ConIndex]
        Run     = Run[ConIndex]
        # Select Run
        RunIndex = np.where(Run == RunID)
        Design  = Design[RunIndex,:][0]
        X       = X[RunIndex,:][0]
        L       = L[RunIndex]           # This will only use in supervised methods
        LUnique = np.unique(L)
        LNum    = np.shape(LUnique)[0]
        OutData["Label"] = LUnique
        OutData["ModelAnalysis"] = "Numpy.Session.RSA"


        if np.shape(X)[0] == 0:
            msgBox.setText("The selected data is empty!")
            msgBox.setIcon(QMessageBox.Critical)
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.exec_()
            return False

        if ui.cbScale.isChecked():
            X = preprocessing.scale(X)
            print("Data is scaled to N(0,1).")
        print("Running RSA ...")
        # RSA Method
        Reg     = np.insert(Design, 0, 1, axis=1)
        Betas   = np.linalg.lstsq(Reg, X)[0][1:,:]
        print("Calculating MSE ...")
        MSE = mean_squared_error(X, np.matmul(Design, Betas))
        print("MSE: %f" % (MSE))
        OutData["MSE"] = MSE

        if ui.cbBeta.isChecked():
            OutData["Betas"]        = Betas
        # Calculate Results
        if ui.cbCorr.isChecked():
            print("Calculating Correlation ...")
            Corr = np.corrcoef(Betas)
            corClass = SimilarityMatrixBetweenClass(Corr)
            OutData["Correlation"]      = Corr
            OutData["Correlation_min"]  = corClass.min()
            OutData["Correlation_max"]  = corClass.max()
            OutData["Correlation_std"]  = corClass.std()
            OutData["Correlation_mean"] = corClass.mean()

        if ui.cbCov.isChecked():
            print("Calculating Covariance ...")
            Cov = np.cov(Betas)
            covClass = SimilarityMatrixBetweenClass(Cov)
            OutData["Covariance"]       = Cov
            OutData["Covariance_min"]   = covClass.min()
            OutData["Covariance_max"]   = covClass.max()
            OutData["Covariance_std"]   = covClass.std()
            OutData["Covariance_mean"]  = covClass.mean()

        OutData["RunTime"] = time.time() - tStart
        print("Runtime (s): %f" % (OutData["RunTime"]))
        print("Saving results ...")
        io.savemat(OutFile,mdict=OutData,do_compression=True)
        print("Output is saved.")

        if ui.cbDiagram.isChecked():
            if ui.cbCorr.isChecked():
                fig1 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(Corr, vmin=-0.1, vmax=1)
                plt.xlim([0, LNum])
                plt.ylim([0, LNum])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Correlation of Categories\nTask: %s\nSub: %d, Counter: %d, Run: %d' % (TaskIDTitle, SubID, ConID, RunID))
                plt.show()

            if ui.cbCov.isChecked():
                fig2 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(Cov)
                plt.xlim([0, LNum])
                plt.ylim([0, LNum])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Covariance of Categories\nTask: %s\nSub: %d, Counter: %d, Run: %d' % (TaskIDTitle, SubID, ConID, RunID))
                plt.show()
        print("DONE.")
        msgBox.setText("Representational Similarity Analysis (RSA) is done.")
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.exec_()


    def btnRedraw_click(self):
        msgBox = QMessageBox()

        ofile = LoadFile("Save result file ...",['Result files (*.mat)'],'mat',\
                             os.path.dirname(ui.txtOutFile.text()))
        if len(ofile):
            try:
                Res     = io.loadmat(ofile)
                LUnique = Res["Label"][0]
                LNum    = np.shape(LUnique)[0]
                SubID   = Res["SubjectID"]
                ConID   = Res["CounterID"]
                RunID   = Res["RunID"]
                TaskIDTitle = Res["Task"][0]
            except:
                print("Cannot load result file!")
                msgBox.setText("Cannot load result file!")
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
                return False

            if ui.cbCorr.isChecked():
                try:
                    Corr = Res["Correlation"]
                except:
                    print("Cannot load Correlation variable!")
                    msgBox.setText("Cannot load Correlation variable!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                fig1 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(Corr, vmin=-0.1, vmax=1)
                plt.xlim([0, LNum])
                plt.ylim([0, LNum])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Correlation\nTask: %s\nSub: %d, Counter: %d, Run: %d' % (TaskIDTitle, SubID, ConID, RunID))
                plt.show()


            if ui.cbCov.isChecked():
                try:
                    Cov = Res["Covariance"]
                except:
                    print("Cannot load Covariance variable!")
                    msgBox.setText("Cannot load Covariance variable!")
                    msgBox.setIcon(QMessageBox.Critical)
                    msgBox.setStandardButtons(QMessageBox.Ok)
                    msgBox.exec_()
                    return False
                fig2 = plt.figure(num=None, figsize=(5, 5), dpi=100)
                plt.pcolor(Cov)
                plt.xlim([0, LNum])
                plt.ylim([0, LNum])
                plt.colorbar()
                ax = plt.gca()
                ax.set_aspect(1)
                plt.title('Covariance\nTask: %s\nSub: %d, Counter: %d, Run: %d' % (TaskIDTitle, SubID, ConID, RunID))
                plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    frmMARSA.show(frmMARSA)
    sys.exit(app.exec_())