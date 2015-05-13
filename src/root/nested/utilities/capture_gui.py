'''
Created on 30 Apr 2015

@author: Mark
'''
import sys
from PyQt4 import QtGui, QtCore


class CaptureGui(QtGui.QMainWindow):

    def __init__(self):
        super(CaptureGui, self).__init__()
        widget = QtGui.QWidget(self)
        layout = QtGui.QVBoxLayout(widget)
        self.area = QtGui.QTextEdit(self)
        layout.addWidget(self.area)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setCentralWidget(widget)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove:
            pos = event.pos()
            if event.buttons() == QtCore.Qt.NoButton:
                self.area.append("No Click @ x: %d, y: %d"
                                 % (pos.x(), pos.y()))
            elif event.buttons() == QtCore.Qt.LeftButton:
                self.area.append("Left Click @ x: %d, y: %d"
                                 % (pos.x(), pos.y()))
            elif event.buttons() == QtCore.Qt.RightButton:
                self.area.append("Right Click @ x: %d, y: %d"
                                 % (pos.x(), pos.y()))
            else:
                pass
        return QtGui.QMainWindow.eventFilter(self, source, event)

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            try:
                with open("../dump/test.txt", "w+") as file:
                    file.write(self.area.toPlainText())
            except FileNotFoundError:
                with open("../dump/test.txt", "a") as file:
                    file.write(self.area.toPlainText())
            self.close()


def main():
    app = QtGui.QApplication(sys.argv)
    tracker = CaptureGui()
    tracker.showMaximized()
    app.installEventFilter(tracker)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
