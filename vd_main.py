from PyQt6.QtWidgets import QMainWindow, QListView, QApplication, QFileDialog
from PyQt6.QtCore import QFile, QFileInfo
from iframe_model import IFrameModel
import sys, os

class VDMainWindow(QMainWindow):
    def __init__(self, file: QFile, parent=None):
        super().__init__(parent)
        self.file = file
        withoutPath = os.path.split(self.file.fileName())[-1]
        self.setWindowTitle(withoutPath)
        
        

        # set up the window
        self.ifListView = QListView()
        self.fmodel = IFrameModel(self.file)
        self.ifListView.setModel(self.fmodel)
        self.setCentralWidget(self.ifListView)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    if(len(sys.argv) > 1):
        if not os.path.exists(sys.argv[1]):
            print("No such file")
        file = QFile(sys.argv[1])
        if QFileInfo(file).completeSuffix() != "mp4":
            print("Invalid file")

    else:
        fileUrl, _ = QFileDialog.getOpenFileUrl(
            caption="Select Video",
            filter=".mp4 (*.mp4)"
        )
        if fileUrl.isEmpty():
            print("You must select a file, or provide one as an argument!")
            sys.exit()
        
        file = QFile(fileUrl.toString())


    mw = VDMainWindow(file)
    halfscreenw = int(mw.screen().availableSize().width() / 2)
    halfscreenh = int(mw.screen().availableSize().height() / 2)
    mw.setFixedWidth(halfscreenw)
    mw.setFixedHeight(halfscreenh)
    mw.move(int(halfscreenw / 2), int(halfscreenh / 2))
    mw.show()

    app.exec()
