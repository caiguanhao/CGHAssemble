import os
import sys
import subprocess
import platform

PLATFORM = platform.system()
WINDOWS = PLATFORM == 'Windows'

from PyQt4.QtCore import *
from PyQt4.QtGui import *

remote_repository = 'https://github.com/choigoonho/maijie.git'

if getattr(sys, 'frozen', False):
  basedir = sys._MEIPASS # PyInstaller path
else:
  basedir = os.path.dirname(os.path.abspath(__file__))

def path(path):
  return QDir.toNativeSeparators(QDir(path).canonicalPath())

local_dir = path(basedir)

class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self);
    width = 500
    height = 200
    self.resize(width, height)
    self.move((QApplication.desktop().width() - width) / 2, 100)

def to_copy_remote(button):
  QApplication.clipboard().setText(remote_repository)
  button.setText('Copied!')

def find_folder(ref, ele):
  folder = QFileDialog.getExistingDirectory(ref, 'Select Folder', remote_repository, QFileDialog.ShowDirsOnly)
  if not folder: return
  global local_dir
  local_dir = path(folder)
  update_local(ele)

def update_label(label, text, url):
  elided_text = QFontMetrics(label.font()).elidedText(text, Qt.ElideMiddle, label.width());
  label.setText('<a href="' + url + '">' + elided_text + '</a>');

def update_remote(label):
  update_label(label, remote_repository, remote_repository)

def update_local(label):
  update_label(label, local_dir, 'file:///' + local_dir)

app = QApplication([])
app.setApplicationName('CGHAssemble')

main = MainWindow()
main.setWindowTitle('CGHAssemble')

grid = QGridLayout()

# the middle column expands
grid.setColumnStretch(1, 10);

source = QLabel('Source')
grid.addWidget(source, 0, 0)

remote = QLabel()
update_remote(remote)
remote.setOpenExternalLinks(True)
grid.addWidget(remote, 0, 1)

copy_remote = QPushButton('Copy')
copy_remote.clicked.connect(lambda: to_copy_remote(copy_remote))
copy_remote.setFocusPolicy(Qt.NoFocus)
grid.addWidget(copy_remote, 0, 2)

dest = QLabel('Local')
grid.addWidget(dest, 1, 0)

local = QLabel()
update_local(local)
local.setOpenExternalLinks(True)
grid.addWidget(local, 1, 1)

select_local = QPushButton('Browse...')
select_local.clicked.connect(lambda: find_folder(main, local))
select_local.setFocusPolicy(Qt.NoFocus)
grid.addWidget(select_local, 1, 2)

console = QTextEdit()
console.setFontFamily('Menlo, Lucida Console, Courier New, Courier')
console.setFontPointSize(10)
console.setText('Ready.')
grid.addWidget(console, 2, 0, 1, 3)

button_grid = QGridLayout()
grid.addLayout(button_grid, 3, 0, 1, 3)

pull = QPushButton('Download/Update')
button_grid.addWidget(pull, 0, 0)

preview = QPushButton('Preview')
button_grid.addWidget(preview, 0, 1)

assemble = QPushButton('Assemble')
button_grid.addWidget(assemble, 0, 2)

frame = QFrame()
frame.setLayout(grid)

main.setCentralWidget(frame)
main.show()

app.exec_()
