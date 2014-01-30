import os
import sys
import subprocess
import platform

from dulwich.repo import Repo
from dulwich.client import get_transport_and_path

PLATFORM = platform.system()
WINDOWS = PLATFORM == 'Windows'

from PyQt4.QtCore import *
from PyQt4.QtGui import *

remote_repository = 'https://github.com/caiguanhao/test.git'

if getattr(sys, 'frozen', False):
  basedir = sys._MEIPASS # PyInstaller path
else:
  basedir = os.path.dirname(os.path.abspath(__file__))

def path(path):
  basename = QFileInfo(remote_repository).baseName()
  return QDir.toNativeSeparators(QDir(path).canonicalPath() + QDir.separator() + basename)

local_dir = path(basedir)

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

class Clone(QThread):
  begin = pyqtSignal()
  finish = pyqtSignal()
  error = pyqtSignal(object)
  progress = pyqtSignal(str)

  def __init__(self, parent):
    QThread.__init__(self, parent)

  def run(self):
    self.begin.emit()
    try:
      client, host_path = get_transport_and_path(str(remote_repository))
      repo = Repo.init(str(local_dir), mkdir=True)
      remote_refs = client.fetch(host_path, repo,
        determine_wants=repo.object_store.determine_wants_all,
        progress=self.progress.emit)
      repo["HEAD"] = remote_refs["HEAD"]
      repo._build_tree()
    except Exception as error:
      self.error.emit(error)
    finally:
      self.finish.emit()

class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self);
    width = 500
    height = 200
    self.resize(width, height)
    self.move((QApplication.desktop().width() - width) / 2, 100)
    self.setWindowTitle('CGHAssemble')
    self.setup_ui()

  def setup_ui(self):
    self.buttons = []

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
    self.buttons.append(copy_remote)

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
    self.buttons.append(select_local)

    self.console = QTextEdit()
    self.console.setFontFamily('Menlo, Lucida Console, Courier New, Courier')
    self.console.setFontPointSize(10)
    self.console.setText('Ready.')
    grid.addWidget(self.console, 2, 0, 1, 3)

    button_grid = QGridLayout()
    grid.addLayout(button_grid, 3, 0, 1, 3)

    self.pull = QPushButton('Download/Update')
    self.pull.clicked.connect(self.pull_clicked)
    button_grid.addWidget(self.pull, 0, 0)
    self.buttons.append(self.pull)

    preview = QPushButton('Preview')
    button_grid.addWidget(preview, 0, 1)
    self.buttons.append(preview)

    assemble = QPushButton('Assemble')
    button_grid.addWidget(assemble, 0, 2)
    self.buttons.append(assemble)

    frame = QFrame()
    frame.setLayout(grid)
    self.setCentralWidget(frame)

  def console_append(self, content):
    self.console.append(str(content))
    self.console.moveCursor(QTextCursor.End)

  def freeze_buttons(self):
    for index, button in enumerate(self.buttons):
      button.setEnabled(False)

  def unfreeze_buttons(self):
    for index, button in enumerate(self.buttons):
      button.setEnabled(True)

  def clone_begin(self):
    self.pull.setText('Processing...')
    self.freeze_buttons()

  def clone_finish(self):
    self.pull.setText('Download/Update')
    self.unfreeze_buttons()

  def pull_clicked(self):
    clone = Clone(self)
    clone.progress.connect(self.console_append)
    clone.error.connect(self.console_append)
    clone.begin.connect(self.clone_begin)
    clone.finish.connect(self.clone_finish)
    clone.start()

if __name__ == '__main__':
  app = QApplication(sys.argv)
  app.setApplicationName('CGHAssemble')
  main = MainWindow()
  main.show()
  sys.exit(app.exec_())
