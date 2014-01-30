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

def to_copy_remote(button):
  QApplication.clipboard().setText(remote_repository)
  button.setText('Copied!')

def find_folder(ref):
  folder = QFileDialog.getExistingDirectory(ref, 'Select Folder', remote_repository, QFileDialog.ShowDirsOnly)
  if folder:
    print folder

app = QApplication([])
app.setApplicationName('CGHAssemble')

main = MainWindow()
main.setWindowTitle('CGHAssemble')

grid = QGridLayout()

source = QLabel('Source')
grid.addWidget(source, 0, 0)

remote = QLabel('<a href="' + remote_repository + '">' + remote_repository + '</a>')
remote.setOpenExternalLinks(True)
grid.addWidget(remote, 0, 1)

copy_remote = QPushButton('Copy')
copy_remote.clicked.connect(lambda: to_copy_remote(copy_remote))
grid.addWidget(copy_remote, 0, 2)

dest = QLabel('Local')
grid.addWidget(dest, 1, 0)

local = QLabel('<a href="file://' + basedir + '">' + basedir + '</a>')
local.setOpenExternalLinks(True)
grid.addWidget(local, 1, 1)

select_local = QPushButton('Browse...')
select_local.clicked.connect(lambda: find_folder(main))
grid.addWidget(select_local, 1, 2)

frame = QFrame()
frame.setLayout(grid)

main.setCentralWidget(frame)
main.show()

app.exec_()
