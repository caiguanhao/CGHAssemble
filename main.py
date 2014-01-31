# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import platform

import psutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from dulwich.repo import Repo
from dulwich.client import get_transport_and_path

from ansi2html import Ansi2HTMLConverter

remote_repository = 'https://github.com/choigoonho/maijie.git'

if getattr(sys, 'frozen', False):
  basedir = sys._MEIPASS # PyInstaller path
else:
  basedir = os.path.dirname(os.path.abspath(__file__))

PLATFORM = platform.system()
WINDOWS = PLATFORM == 'Windows'

NODE = os.path.join(basedir, "node.exe")
NPM = os.path.join(basedir, "npm", "cli.js")
GRUNT = os.path.join(basedir, "grunt-cli", "bin", "grunt")
SETTINGS_FILE = os.path.join(basedir, "settings.ini")

SETTINGS = QSettings(SETTINGS_FILE, QSettings.IniFormat)

CONVERTER = Ansi2HTMLConverter(dark_bg=False, scheme='solarized')

# kill previous launched but not ended node process
for proc in psutil.process_iter():
  try:
    if proc.name == "node.exe" and proc.getcwd().startswith(basedir):
      proc.kill()
  except:
    pass

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
      self.remote = str(self.remote)
      self.local = str(self.local)

      client, host_path = get_transport_and_path(self.remote)

      if os.path.isdir(os.path.join(self.local, '.git')):
        repo = Repo(self.local)
      else:
        repo = Repo.init(self.local, mkdir=True)

      remote_refs = client.fetch(host_path, repo,
        determine_wants=repo.object_store.determine_wants_all,
        progress=self.progress.emit)
      repo["HEAD"] = remote_refs["HEAD"]
      repo._build_tree()
      self.progress.emit('Up-to-date.')
    except Exception as error:
      self.error.emit(error)
    finally:
      self.finish.emit()

class Node(QThread):
  begin = pyqtSignal()
  finish = pyqtSignal(int)
  progress = pyqtSignal(str)
  error = pyqtSignal(object)

  def __init__(self, parent, local, commands):
    QThread.__init__(self, parent)
    self.local = local
    self.commands = commands
    self.process = None

  def run(self):
    self.begin.emit()
    try:
      env = os.environ.copy()
      self.process = subprocess.Popen([ NODE ] + self.commands, cwd=self.local,
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      while True:
        line = self.process.stdout.readline()
        if line != '':
          line = line.decode('utf-8').strip()
          self.progress.emit(line)
        else:
          break
    except Exception as error:
      self.error.emit(error)
    finally:
      return_code = 1
      if hasattr(self.process, 'communicate'):
        self.process.communicate()
        return_code = self.process.returncode
      self.process = None
      self.finish.emit(return_code)

class MainWindow(QMainWindow):
  def __init__(self):
    QMainWindow.__init__(self);
    width = 600
    height = 400
    self.resize(width, height)
    self.move((QApplication.desktop().width() - width) / 2, 100)
    self.setWindowTitle('CGHAssemble')
    try:
      self.local_dir = str(SETTINGS.value('local_dir').toString())
      if not self.local_dir: raise
    except:
      self.local_dir = self.path(os.path.expanduser('~'))
    self.previewing = False
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
    self.console.setReadOnly(True)
    self.console.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.console.setStyleSheet("QTextEdit { background: #FDF6E3 }");
    self.console_append('Ready.')
    grid.addWidget(self.console, 2, 0, 1, 3)

    button_grid = QGridLayout()
    grid.addLayout(button_grid, 3, 0, 1, 3)

    self.pull = QPushButton('Download/Update')
    self.pull.clicked.connect(self.pull_clicked)
    button_grid.addWidget(self.pull, 0, 0)
    self.buttons.append(self.pull)

    self.install = QPushButton('Install')
    self.install.clicked.connect(self.install_clicked)
    button_grid.addWidget(self.install, 0, 1)
    self.buttons.append(self.install)

    self.preview = QPushButton('Preview')
    self.preview.clicked.connect(self.preview_clicked)
    button_grid.addWidget(self.preview, 0, 2)
    self.buttons.append(self.preview)

    self.assemble = QPushButton('Assemble')
    self.assemble.clicked.connect(self.assemble_clicked)
    button_grid.addWidget(self.assemble, 0, 3)
    self.buttons.append(self.assemble)

    credits = QLabel()
    font = QFont()
    font.setPointSize(10)
    credits.setFont(font)
    credits.setAlignment(Qt.AlignHCenter)
    credits.setText('Created by caiguanhao. View source and docs or report' +
      ' issues on <a href="https://github.com/caiguanhao/CGHAssemble">' +
      'GitHub</a>.')
    credits.setOpenExternalLinks(True)
    button_grid.addWidget(credits, 1, 0, 1, 4)

    frame = QFrame()
    frame.setLayout(grid)
    self.setCentralWidget(frame)

  def path(self, path):
    basename = os.path.splitext(os.path.basename(remote_repository))[0]
    newpath = os.path.abspath(os.path.join(path, basename))
    newpath = newpath[:1].upper() + newpath[1:]
    return newpath

  def to_copy_remote(self):
    QApplication.clipboard().setText(remote_repository)
    self.copy_remote.setText('Copied!')
    QTimer.singleShot(1000, lambda: self.copy_remote.setText('Copy'))

  def browse_folder(self, ele):
    folder = QFileDialog.getExistingDirectory(self, 'Select Folder',
      self.local_dir, QFileDialog.ShowDirsOnly)
    if not folder: return
    try:
      str(folder).decode('ascii')
    except UnicodeEncodeError:
      self.warn("Please select a folder which path contains no unicode " +
        "characters.")
    else:
      self.local_dir = self.path(str(folder))
      self.update_local()

  def update_label(self, label, text, url):
    elided_text = QFontMetrics(label.font()).elidedText(text,
      Qt.ElideMiddle, label.width());
    label.setText('<a href="' + url + '">' + elided_text + '</a>');

  def update_remote(self):
    self.update_label(self.remote, remote_repository, remote_repository)

  def update_local(self):
    local_dir_ = self.local_dir
    if not os.path.isdir(local_dir_): local_dir_ = os.path.dirname(local_dir_)
    local_dir_ = local_dir_.replace('\\', '/')
    self.update_label(self.local, self.local_dir, 'file:///' + local_dir_)
    SETTINGS.setValue('local_dir', self.local_dir)

  def console_clear(self):
    self.console.clear()

  def console_append(self, content):
    text = unicode(content)
    text = text.replace('\r', '\n')
    text = CONVERTER.convert(text)
    self.console.append(text)
    self.console.moveCursor(QTextCursor.End)
    self.console.horizontalScrollBar().setValue(0)

  def freeze_buttons(self):
    for index, button in enumerate(self.buttons):
      button.setEnabled(False)

  def unfreeze_buttons(self):
    for index, button in enumerate(self.buttons):
      button.setEnabled(True)

  def clone_begin(self):
    self.console_append('Connecting...')
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

  def install_begin(self):
    self.install.setText('Processing...')
    self.freeze_buttons()

  def install_finish(self, return_code):
    self.install.setText('Install')
    self.unfreeze_buttons()
    if return_code is 0:
      self.console_append('All packages have been successfully installed.')

  def install_clicked(self):
    if not os.path.isfile(os.path.join(self.local_dir, 'package.json')):
      QMessageBox.warning(self, "Error", "The package.json file is not " +
        "found in local directory. Nothing to install.")
      return
    self.console_clear()
    node = Node(self, self.local_dir, [ NPM, "install" ])
    node.progress.connect(self.console_append)
    node.error.connect(self.console_append)
    node.begin.connect(self.install_begin)
    node.finish.connect(self.install_finish)
    node.start()

  def preview_begin(self):
    self.previewing = False
    self.preview.setText('Processing...')
    self.freeze_buttons()
    QTimer.singleShot(5000, self.preview_previewing)

  def preview_previewing(self):
    self.previewing = True
    self.preview.setEnabled(True)
    self.preview.setText('Close')

  def preview_finish(self, return_code=-1):
    self.previewing = False
    self.preview.setText('Preview')
    self.unfreeze_buttons()

  def preview_closed(self):
    self.console_append('Preview is now closed.')
    self.preview_finish()

  def preview_clicked(self):
    if self.previewing:
      try:
        self.preview_process.finish.disconnect(self.preview_finish);
        self.freeze_buttons()
        self.preview_process.process.kill()
        QTimer.singleShot(1000, self.preview_closed)
      except Exception as error:
        self.console_append(error)
    else:
      if not os.path.isfile(os.path.join(self.local_dir, 'Gruntfile.js')):
        self.warn("The Gruntfile.js file is not found in local directory. " +
          "Nothing to preview.")
        return
      if not os.path.isdir(os.path.join(self.local_dir, 'node_modules',
        'grunt')):
        self.warn("Grunt is not installed in node_modules directory. " +
          "Please click Install button first.")
        return
      self.console_clear()
      node = Node(self, self.local_dir, [ GRUNT ])
      node.progress.connect(self.console_append)
      node.error.connect(self.console_append)
      node.begin.connect(self.preview_begin)
      node.finish.connect(self.preview_finish)
      node.start()
      self.preview_process = node

  def assemble_begin(self):
    self.assemble.setText('Processing...')
    self.freeze_buttons()

  def assemble_finish(self, return_code):
    self.assemble.setText('Assemble')
    self.unfreeze_buttons()

  def assemble_clicked(self):
    if not os.path.isfile(os.path.join(self.local_dir, 'Gruntfile.js')):
      self.warn("The Gruntfile.js file is not found in local directory. " +
        "Nothing to assemble.")
      return
    if not os.path.isdir(os.path.join(self.local_dir, 'node_modules', 'grunt')):
      self.warn("Grunt is not installed in node_modules directory. " +
        "Please click Install button first.")
      return
    self.console_clear()
    node = Node(self, self.local_dir, [ GRUNT, "make" ])
    node.progress.connect(self.console_append)
    node.error.connect(self.console_append)
    node.begin.connect(self.assemble_begin)
    node.finish.connect(self.assemble_finish)
    node.start()

  def warn(self, text):
    QMessageBox.warning(self, "Error", text)

if __name__ == '__main__':
  app = QApplication(sys.argv)
  app.setApplicationName('CGHAssemble')
  main = MainWindow()
  main.show()
  sys.exit(app.exec_())
