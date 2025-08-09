from PyQt6 import QtCore, QtWidgets, QtGui
import sys, os
import subprocess
import ffmpeg

QtGui.QPixmapCache.setCacheLimit(128*128*3*30)

class FrameModel(QtCore.QAbstractListModel):
    def __init__(self, file: QtCore.QFile):
        super().__init__()
        self.file = file
        #process video
        cmd = ["ffprobe", 
               "-select_streams", "v:0", 
               "-show_frames", 
               "-skip_frame", "nokey", 
               "-show_entries", "frame=pts_time",
               "-of", "csv=p=0",
               self.file.fileName()]
        
        try:
            csv_frames = subprocess.run(cmd, capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError as e:
            print("reason: %s" % e.stderr.strip())
            sys.exit()

        
        self.iframe_timestamps = [line.split(",")[0] for line in csv_frames.stdout.strip().splitlines()]
        

    def rowCount(self, parent=None):
        return len(self.iframe_timestamps)
    def data(self, index: QtCore.QModelIndex, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return self.iframe_timestamps[index.row()]
        if role == QtCore.Qt.ItemDataRole.DecorationRole:
            frame = self.iframe_timestamps[index.row()]
            pix = QtGui.QPixmapCache.find(str(frame))
            if not pix:
                pix = QtGui.QPixmap()
                fpix = ffmpeg.input(self.file.fileName(), ss=frame) \
                                    .filter('scale',128,-1) \
                                    .output('pipe:1', vframes=1, format='image2', vcodec='png') \
                                    .run(capture_stdout=True)
                pix.loadFromData(QtCore.QByteArray(fpix[0]),"PNG")
                QtGui.QPixmapCache.insert(str(frame), pix)
            return pix



class VDMainWindow(QtWidgets.QMainWindow):
    def __init__(self, file: QtCore.QFile, parent=None):
        super().__init__(parent)
        self.file = file
        withoutPath = os.path.split(self.file.fileName())[-1]
        self.setWindowTitle(withoutPath)
        
        

        # set up the window
        fmodel = FrameModel(self.file)

        ifListView = QtWidgets.QListView()
        ifListView.setModel(fmodel)
        
        self.setCentralWidget(ifListView)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    if(len(sys.argv) > 1):
        if not os.path.exists(sys.argv[1]):
            print("No such file")
        file = QtCore.QFile(sys.argv[1])
        if QtCore.QFileInfo(file).completeSuffix() != "mp4":
            print("Invalid file")

    else:
        fileUrl, _ = QtWidgets.QFileDialog.getOpenFileUrl(
            caption="Select Video",
            filter=".mp4 (*.mp4)"
        )
        if fileUrl.isEmpty():
            print("You must select a file, or provide one as an argument!")
            sys.exit()
        
        file = QtCore.QFile(fileUrl.toString())


    mw = VDMainWindow(file)
    halfscreenw = int(mw.screen().availableSize().width() / 2)
    halfscreenh = int(mw.screen().availableSize().height() / 2)
    mw.setFixedWidth(halfscreenw)
    mw.setFixedHeight(halfscreenh)
    mw.move(int(halfscreenw / 2), int(halfscreenh / 2))
    mw.show()

    app.exec()
