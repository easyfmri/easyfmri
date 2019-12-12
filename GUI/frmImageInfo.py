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
import nibabel as nb
import numpy as np
from PyQt5.QtWidgets import *
from Base.utility import getVersion, getBuild
from Base.dialogs import LoadFile
from GUI.frmImageInfoGUI import *


class frmImageInfo(Ui_frmImageInfo):
    ui = Ui_frmImageInfo()
    dialog = None
    # This function is run when the main form start
    # and initiate the default parameters.
    def show(self):
        global dialog
        global ui
        ui = Ui_frmImageInfo()
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create('Fusion'))
        dialog = QtWidgets.QMainWindow()
        ui.setupUi(dialog)
        self.set_events(self)


        dialog.setWindowTitle("easy fMRI Image Information - V" + getVersion() + "B" + getBuild())
        dialog.setWindowFlags(dialog.windowFlags() | QtCore.Qt.CustomizeWindowHint)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowMaximizeButtonHint)
        dialog.setFixedSize(dialog.size())
        dialog.show()


    # This function initiate the events procedures
    def set_events(self):
        global ui
        ui.btnClose.clicked.connect(self.btnClose_click)
        ui.btnImage.clicked.connect(self.btnImage_click)


    def btnClose_click(self):
        global dialog
        dialog.close()


    def btnImage_click(self):
        filename = LoadFile("Select an image file ...",['(f)MRI image files (*.nii.gz)', 'All files (*.*)'],'nii.gz',
                            os.path.dirname(ui.txtImage.text()))
        if len(filename):
            if os.path.isfile(filename):
                try:
                    mriHDR   = nb.load(filename)
                    mriData  = mriHDR.get_data()
                    AllVoxel = 1
                    for size in  np.shape(mriData):
                        AllVoxel = AllVoxel * size
                    Zero = 1
                    for size in np.shape(np.where(mriData == 0)[0]):
                        Zero = Zero * size
                    ui.txtImageInfo.clear()
                    ui.txtImageInfo.append("---- Image Shape: " + str(mriHDR.header.get_data_shape()))
                    ui.txtImageInfo.append("---- Number of Voxels: %d = (Zero Value Voxel: %d + Other: %d)" % (AllVoxel, Zero, AllVoxel - Zero))
                    ui.txtImageInfo.append("---- Affine Matrix:")
                    ui.txtImageInfo.append(str(mriHDR.affine))
                    ui.txtImageInfo.append("---- Header Information:")
                    ui.txtImageInfo.append(str(mriHDR.header).replace("<class 'nibabel.nifti1.Nifti1Header'> object, endian='<'","").replace("\n","",1))
                    ui.txtImage.setText(filename)
                except:

                    print("Cannot load image file!")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frmImageInfo.show(frmImageInfo)
    sys.exit(app.exec_())