from PyQt6.QtCore import QAbstractListModel, QFile, QModelIndex, Qt
from PyQt6.QtCore import QByteArray, pyqtSignal, QThread
from PyQt6.QtGui import QPixmap
import sys
import subprocess
import ffmpeg

class FrameLoader(QThread):
    added = pyqtSignal(int)

    def __init__(self, timestamps: list[str], load: dict[int,QByteArray], file: QFile):
        super().__init__()
        self.load = load
        self.timestamps = timestamps
        self.file = file
    
    def run(self):
        for i, time in enumerate(self.timestamps):
        
            fpix = ffmpeg.input(self.file.fileName(), ss=time) \
                            .filter('scale',128,128) \
                            .output('pipe:1', vframes=1, format='image2', vcodec='mjpeg', qscale=5) \
                            .global_args('-hide_banner', '-loglevel', 'error') \
                            .run(capture_stdout=True)
        
            self.load[i] = QByteArray(fpix[0])
            self.added.emit(i)

        

class IFrameModel(QAbstractListModel):
    def __init__(self, file: QFile):
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
        self.frame_load = dict[int,QByteArray]()
        self.frame_loader = FrameLoader(self.iframe_timestamps,self.frame_load,self.file)
        self.frame_loader.added.connect(self.frame_added)
        self.frame_loader.start()

    def frame_added(self, i: int):
        idx = self.index(i)
        self.dataChanged.emit(idx, idx, [Qt.ItemDataRole.DecorationRole])

    def rowCount(self, parent=None):
        return len(self.iframe_timestamps)
    
    def columnCount(self, parent = None):
        return 2
    
    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self.iframe_timestamps[index.row()]
        if role == Qt.ItemDataRole.DecorationRole:
            if index.row() in self.frame_load:    
                pix = QPixmap()
                pix.loadFromData(self.frame_load[index.row()], "JPG")
                return pix
            else:
                return QPixmap(128,128)
        return None

            
