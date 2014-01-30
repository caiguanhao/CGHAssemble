import os
import sys
import subprocess

from PyQt4.QtCore import *
from PyQt4.QtGui import *

remote_repository = 'https://github.com/choigoonho/maijie.git'

if getattr(sys, 'frozen', False):
  basedir = sys._MEIPASS # PyInstaller path
else:
  basedir = os.path.dirname(os.path.abspath(__file__))

class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self);
    width = 400
    height = 200
    self.resize(width, height)
    self.move((QApplication.desktop().width() - width) / 2, 100)

app = QApplication([])
app.setApplicationName('CGHAssemble')

main = MainWindow()
main.setWindowTitle('CGHAssemble')

grid = QGridLayout()

source = QLabel('Source')
grid.addWidget(source, 0, 0)

remote = QLabel('<a href="' + remote_repository + '">' + remote_repository + '</a>')
grid.addWidget(remote, 0, 1)

dest = QLabel('Local')
grid.addWidget(dest, 1, 0)

local = QLabel('<a href="' + basedir + '">' + basedir + '</a>')
grid.addWidget(local, 1, 1)

frame = QFrame()
frame.setLayout(grid)

main.setCentralWidget(frame)
main.show()

app.exec_()
