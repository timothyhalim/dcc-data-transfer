import json
import os
from maya import cmds

from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import *
    
def getMayaWindow():
    for w in QApplication.topLevelWidgets():
        try:
            if w.objectName() == 'MayaWindow':
                return w
        except:
            pass
    return None
    
class ExportCam(QMainWindow):
    def __init__(self, parent=None):
        super(ExportCam, self).__init__(parent)
        
        # CHECK EXISTING WINDOW
        windowName = 'ExportCam'
        for w in QApplication.topLevelWidgets():
            if w.objectName == windowName :
                w.close()
                w.deleteLater()
        
        self.setWindowTitle("ExportCam - timo.ink" )
        self.objectName = windowName
        self.setAttribute(Qt.WA_DeleteOnClose)
        
        self.buildUI()
        self.initUI()
        self.connectSignal()
        self.show()
        
    def buildUI(self):
        # MAIN WIDGET
        self.mainWidget = QWidget()
        self.setCentralWidget(self.mainWidget)
        self.mainLayout = QVBoxLayout(self.mainWidget)
        
        # CAMERA
        self.cameraLayout = QHBoxLayout()
        self.cameraLabel = QLabel('Camera :')
        self.cameraList = QComboBox()
        self.cameraReload = QPushButton("Reload")
        for w in [self.cameraLabel, self.cameraList, self.cameraReload]:
            self.cameraLayout.addWidget(w)
        
        # FRAMES
        self.frameLayout = QHBoxLayout()
        self.frameLabel = QLabel('Frame :')
        self.frameStart = QSpinBox()
        self.frameDiv = QLabel('-')
        self.frameEnd = QSpinBox()
        for w in [self.frameLabel, self.frameStart, 
                    self.frameDiv, self.frameEnd]:
            self.frameLayout.addWidget(w)
        
        # OUTPUT
        self.exportPathLayout = QHBoxLayout()
        self.exportPathLabel = QLabel('Path :')
        self.exportPath = QLineEdit()
        self.exportSelect = QPushButton("...")
        for w in [self.exportPathLabel, self.exportPath, self.exportSelect]:
            self.exportPathLayout.addWidget(w)
            
        # EXECUTE
        self.export = QPushButton("Export")
        
        # ADD TO WIDGET
        for w in ( self.cameraLayout, 
                   self.frameLayout, 
                   self.exportPathLayout, 
                   self.export
                   ):
            try:
                self.mainLayout.addWidget(w)
            except:
                self.mainLayout.addLayout(w)
                
    def initUI(self):
        # SET WIDTH
        for l in (self.cameraLabel,
                  self.frameLabel,
                  self.exportPathLabel,
                ):
            l.setMaximumWidth(50)
            l.setMinimumWidth(50)
            l.setAlignment(Qt.AlignRight)
        
        self.frameDiv.setMaximumWidth(10)
        self.frameDiv.setMinimumWidth(10)
        
        self.cameraReload.setMaximumWidth(70)
        self.cameraReload.setMinimumWidth(70)
        
        self.exportSelect.setMaximumWidth(25)
        self.exportSelect.setMinimumWidth(25)
        
        # SET LIMIT
        for w in [self.frameStart, self.frameEnd]:
            w.setMinimum(-999999999)
            w.setMaximum(999999999)
        
        # INITIAL VALUE
        self.frameStart.setValue(int(cmds.playbackOptions(q=True, ast=True)))
        self.frameEnd.setValue(int(cmds.playbackOptions(q=True, aet=True)))
        self.exportPath.setText(
            os.path.join(
                os.path.dirname(cmds.file(q=1, sn=1)),
                "cache",
                "Camera.abc"
            ).replace("/", "\\")
        )
        
        self.reloadCameraList()
    
    def connectSignal(self):
        self.cameraList.currentIndexChanged.connect(self.setCamera)
        self.cameraReload.clicked.connect(self.reloadCameraList)
        self.exportSelect.clicked.connect(self.selectDirectory)
        self.export.clicked.connect(self.exportCamera)
        
    def selectDirectory(self):
        currentDir = os.path.dirname(self.exportPath.text())
        newDir = QFileDialog.getExistingDirectory(caption="Select Export Folder", dir=currentDir)
        if newDir:
            self.exportPath.setText(os.path.normpath(os.path.join(newDir, "Camera.abc")))
        
    def reloadCameraList(self):
        self.sceneCameras = [cmds.listRelatives(c, p=True, type="transform", f=True)[0] for c in cmds.ls(cameras=True)]
        self.cameraList.clear()
        self.cameraList.addItems(self.sceneCameras)
        self.cameraToExport = self.sceneCameras[self.cameraList.currentIndex()]
        
    def setCamera(self):
        self.cameraToExport = self.sceneCameras[self.cameraList.currentIndex()]
        
    def buildCameraData(self):
        camData = {}
        cam = self.cameraToExport
        start = int(self.frameStart.text())
        end = int(self.frameEnd.text())
        for f in range(start,end+1):
            camData[f] = {
                "lens" : cmds.getAttr(cam+".focalLength", time=f),
                "sensor_fit" : cmds.getAttr(cam+".filmFit", time=f, asString=True).upper(),
                "sensor_width" : cmds.getAttr(cam+".horizontalFilmAperture", time=f)*25.4,
                "sensor_height" : cmds.getAttr(cam+".verticalFilmAperture", time=f)*25.4,
                "clip_start" : cmds.getAttr(cam+".nearClipPlane", time=f),
                "clip_end" : cmds.getAttr(cam+".farClipPlane", time=f)
            }
        return camData
        
    def exportCamera(self):
        abcOutput = self.exportPath.text().replace("\\", "/")
        if not os.path.isdir(os.path.dirname(abcOutput)):
            os.makedirs(os.path.dirname(abcOutput))
        basename = os.path.basename(abcOutput)
        filename = os.path.splitext(basename)[0]
        if not abcOutput.endswith(".abc"):
            abcOutput += ".abc"
        jsonOutput = os.path.join(os.path.dirname(abcOutput), filename+".json")
        
        cmds.refresh(suspend=True)
        cmds.select(cl=True)
        cmds.select(self.cameraToExport)
        
        job =  "-frameRange {start} {end} ".format(start=int(self.frameStart.text()), end=int(self.frameEnd.text()))
        job += "-dataFormat ogawa -worldSpace -uvWrite -writeUVSets -wholeFrameGeo -step 0.5 "
        job += "-root {camera} ".format(camera=self.cameraToExport)
        job += "-file '{output}' ".format(output=abcOutput)
        
        print(job)
        cmds.AbcExport(j=job, duf=True)
        
        cmds.refresh(suspend=False)
        camData = self.buildCameraData()
        with open(jsonOutput, "w") as f:
            f.write(json.dumps(camData, indent=4))
        
ExportCam(parent=getMayaWindow())
        