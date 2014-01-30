import os
import sys
import subprocess
import platform

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dulwich.repo import Repo
from dulwich.client import get_transport_and_path

PLATFORM = platform.system()
WINDOWS = PLATFORM == 'Windows'

remote_repository = 'https://github.com/caiguanhao/test.git'

if getattr(sys, 'frozen', False):
  basedir = sys._MEIPASS # PyInstaller path
else:
  basedir = os.path.dirname(os.path.abspath(__file__))

def path(*args):
  return QDir.toNativeSeparators(str(QDir.separator()).join(args))

class Clone(QThread):
  begin = pyqtSignal()
  finish = pyqtSignal()
  error = pyqtSignal(object)
  progress = pyqtSignal(str)

  def __init__(self, parent, remote, local):
    QThread.__init__(self, parent)
    self.remote = remote
    self.local = local

  def run(self):
    self.begin.emit()
    try:
      client, host_path = get_transport_and_path(str(self.remote))

      if QFile.exists(path(str(self.local), '.git')):
        repo = Repo(str(self.local))
      else:
        repo = Repo.init(str(self.local), mkdir=True)

      remote_refs = client.fetch(host_path, repo,
        determine_wants=repo.object_store.determine_wants_all,
        progress=self.progress.emit)
      repo["HEAD"] = remote_refs["HEAD"]
      repo._build_tree()
      self.progress.emit("Up-to-date.\n")
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
    self.local_dir = self.path(basedir)
    self.setup_ui()

  def setup_ui(self):
    self.buttons = []

    grid = QGridLayout()

    # the middle column expands
    grid.setColumnStretch(1, 10);

    source = QLabel('Source')
    grid.addWidget(source, 0, 0)

    self.remote = QLabel()
    self.remote.setOpenExternalLinks(True)
    grid.addWidget(self.remote, 0, 1)
    self.update_remote()

    self.copy_remote = QPushButton('Copy')
    self.copy_remote.clicked.connect(self.to_copy_remote)
    self.copy_remote.setFocusPolicy(Qt.NoFocus)
    grid.addWidget(self.copy_remote, 0, 2)
    self.buttons.append(self.copy_remote)

    dest = QLabel('Local')
    grid.addWidget(dest, 1, 0)

    self.local = QLabel()
    self.local.setOpenExternalLinks(True)
    grid.addWidget(self.local, 1, 1)
    self.update_local()

    select_local = QPushButton('Browse...')
    select_local.clicked.connect(self.browse_folder)
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

  def path(self, path):
    basename = QFileInfo(remote_repository).baseName()
    return QDir.toNativeSeparators(QDir(path).canonicalPath() + QDir.separator() + basename)

  def to_copy_remote(self):
    QApplication.clipboard().setText(remote_repository)
    self.copy_remote.setText('Copied!')
    QTimer.singleShot(1000, lambda: self.copy_remote.setText('Copy'))

  def browse_folder(self, ele):
    folder = QFileDialog.getExistingDirectory(self, 'Select Folder',
      remote_repository, QFileDialog.ShowDirsOnly)
    if not folder: return
    self.local_dir = self.path(folder)
    self.update_local()

  def update_label(self, label, text, url):
    elided_text = QFontMetrics(label.font()).elidedText(text, Qt.ElideMiddle, label.width());
    label.setText('<a href="' + url + '">' + elided_text + '</a>');

  def update_remote(self):
    self.update_label(self.remote, remote_repository, remote_repository)

  def update_local(self):
    self.update_label(self.local, self.local_dir, 'file:///' + self.local_dir)

  def console_clear(self):
    self.console.clear()

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
    self.console_clear()
    clone = Clone(self, remote_repository, self.local_dir)
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
