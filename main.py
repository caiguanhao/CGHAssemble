# -*- coding: utf-8 -*-
VERSION = "1.0.3.0"

import os
import sys
import subprocess
import platform
import hashlib

import psutil

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import *

from dulwich.repo import Repo
from dulwich.client import get_transport_and_path

from ansi2html import Ansi2HTMLConverter

# will be replaced by `make`
USER = '{{USER}}'
REPO = '{{REPO}}'
NODE_SHASUM = '{{NODE_SHASUM}}'

if USER[0] is '{': USER = 'choigoonho'
if REPO[0] is '{': REPO = 'maijie'

remote_repository = 'https://github.com/%s/%s.git' % (USER, REPO)

if getattr(sys, 'frozen', False):
  basedir = sys._MEIPASS # PyInstaller path
else:
  basedir = os.path.dirname(os.path.abspath(__file__))

PLATFORM = platform.system()
WINDOWS = PLATFORM == 'Windows'
MAC = PLATFORM == 'Darwin'

NODE = None
if os.path.isfile(os.path.join(basedir, 'node.exe')):
  NODE = os.path.join(basedir, "node.exe")
elif os.path.isfile(os.path.join(basedir, 'node')):
  NODE = os.path.join(basedir, "node")
NPM = os.path.join(basedir, "npm", "cli.js")
GRUNT = os.path.join(basedir, "grunt-cli", "bin", "grunt")
USER_HOME_DIR = os.path.expanduser('~')
SETTINGS_FILE = os.path.join(USER_HOME_DIR, '.cgh-assemble-settings')

SETTINGS = QSettings(SETTINGS_FILE, QSettings.IniFormat)
SETTINGS.beginGroup('%s-%s' % (USER, REPO));

CONVERTER = Ansi2HTMLConverter(dark_bg=False, scheme='solarized')

REBOOT_CODE = 123

QTextCodec.setCodecForTr(QTextCodec.codecForName('utf-8'))

link_style = ' style="text-decoration: none"'

# http://stackoverflow.com/a/3431835
def shasum(filename, blocksize=65536):
  sha1 = hashlib.new('sha1')
  file = open(filename, 'rb')
  buf = file.read(blocksize)
  while len(buf) > 0:
    sha1.update(buf)
    buf = file.read(blocksize)
  return sha1.hexdigest()

def set_window_icon(widget):
  if not MAC:
    widget.setWindowIcon(QIcon(os.path.join(basedir, 'res', 'hammer.png')))

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
      self.progress.emit(tr('Up-to-date.'))
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

    startupinfo = None
    try:
      startupinfo = subprocess.STARTUPINFO()
      startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    except:
      pass

    try:
      env = os.environ.copy()
      self.process = subprocess.Popen([ NODE ] + self.commands, cwd=self.local,
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        startupinfo=startupinfo)
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
    QMainWindow.__init__(self)

    scale = 1
    if WINDOWS:
      scale = float(self.logicalDpiX()) / 96
    width = 600 * scale
    height = 400 * scale
    self.resize(width, height)
    self.move((QApplication.desktop().width() - width) / 2, 100)

    self.setWindowTitle(tr('CGHAssemble') + ' %s (%s/%s)' %
      (VERSION, USER, REPO))
    set_window_icon(self)
    try:
      self.local_dir = str(SETTINGS.value('local_dir').toString())
      if not self.local_dir: raise
    except:
      self.local_dir = self.path(USER_HOME_DIR)

    # kill previous launched but not ended node process
    for proc in psutil.process_iter():
      try:
        if (proc.name == "node" or proc.name == "node.exe") and \
          proc.getcwd().startswith(self.local_dir):
          proc.kill()
      except:
        pass

    self.previewing = False
    self.setup_ui()

  def resizeEvent(self, event):
    self.update_remote()
    self.update_local()

  def setup_ui(self):
    self.buttons = []
    self.buttons_all_frozen = False;

    grid = QGridLayout()

    # the middle column expands
    grid.setColumnStretch(1, 10);

    source = QLabel(tr('Source'))
    grid.addWidget(source, 0, 0)

    self.remote = QLabel()
    self.remote.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    self.remote.setOpenExternalLinks(True)
    grid.addWidget(self.remote, 0, 1)
    # let the label to elide text on start:
    QTimer.singleShot(1, lambda: self.update_remote())

    self.copy_remote = QPushButton(tr('Copy'))
    self.copy_remote.clicked.connect(self.to_copy_remote)
    self.copy_remote.setFocusPolicy(Qt.NoFocus)
    grid.addWidget(self.copy_remote, 0, 2)
    self.buttons.append(self.copy_remote)

    dest = QLabel(tr('Local'))
    grid.addWidget(dest, 1, 0)

    self.local = QLabel()
    self.local.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
    self.local.linkActivated.connect(self.local_clicked)
    grid.addWidget(self.local, 1, 1)
    # let the label to elide text on start:
    QTimer.singleShot(1, lambda: self.update_local())

    select_local = QPushButton(tr('Browse...'))
    select_local.clicked.connect(self.browse_folder)
    select_local.setFocusPolicy(Qt.NoFocus)
    grid.addWidget(select_local, 1, 2)
    self.buttons.append(select_local)

    self.console = QTextEdit()
    self.console.setReadOnly(True)
    self.console.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    self.console.setStyleSheet("QTextEdit { background: #FDF6E3 }")
    self.console_append(tr('Ready.'))
    grid.addWidget(self.console, 2, 0, 1, 3)

    button_grid = QGridLayout()
    grid.addLayout(button_grid, 3, 0, 1, 3)

    self.pull = QPushButton(tr('Download/Update'))
    self.pull.clicked.connect(self.pull_clicked)
    button_grid.addWidget(self.pull, 0, 0)
    self.buttons.append(self.pull)

    self.install = QPushButton(tr('Install'))
    self.install.clicked.connect(self.install_clicked)
    button_grid.addWidget(self.install, 0, 1)
    self.buttons.append(self.install)

    self.preview = QPushButton(tr('Preview'))
    self.preview.clicked.connect(self.preview_clicked)
    button_grid.addWidget(self.preview, 0, 2)
    self.buttons.append(self.preview)

    self.assemble = QPushButton(tr('Assemble'))
    self.assemble.clicked.connect(self.assemble_clicked)
    button_grid.addWidget(self.assemble, 0, 3)
    self.buttons.append(self.assemble)

    credits = QLabel()
    font = QFont()
    font.setPointSize(10)
    font.setUnderline(False)
    if WINDOWS:
      font.setPointSize(8)
    credits.setFont(font)
    credits.setAlignment(Qt.AlignHCenter)
    credits.setText('Created by <a href="http://cgh.io/"' + link_style +
      '>caiguanhao</a>. View source and docs or report issues on ' +
      '<a href="https://github.com/caiguanhao/CGHAssemble"' + link_style +
      '>GitHub</a>. <a href="setlang:' + tr('lang-zh') + '"' + link_style +
      '>' + tr('中文') + '</a>')
    credits.linkActivated.connect(self.credits_clicked)
    button_grid.addWidget(credits, 1, 0, 1, 4)

    frame = QFrame()
    frame.setLayout(grid)
    self.setCentralWidget(frame)

  def local_clicked(self, url):
    try:
      url = str(url)
      if not os.path.isdir(url): url = os.path.dirname(url)
      url = url.replace('\\', '/')
      QDesktopServices.openUrl(QUrl('file:///' + url))
    except:
      pass

  def credits_clicked(self, url):
    if url[:8] == 'setlang:':
      if self.buttons_all_frozen:
        self.warn(tr("Changing the language will break current task. " +
          "Please try again once current task completes."));
        return
      SETTINGS.setValue('lang', url[13:])
      app.exit(REBOOT_CODE)
      return
    QDesktopServices.openUrl(QUrl(url))

  def path(self, path):
    basename = os.path.splitext(os.path.basename(remote_repository))[0]
    newpath = os.path.abspath(os.path.join(path, basename))
    newpath = newpath[:1].upper() + newpath[1:]
    return newpath

  def to_copy_remote(self):
    QApplication.clipboard().setText(remote_repository)
    self.copy_remote.setText(tr('Copied!'))
    QTimer.singleShot(1000, lambda: self.copy_remote.setText(tr('Copy')))

  def browse_folder(self, ele):
    folder = QFileDialog.getExistingDirectory(self, tr('Select Folder'),
      self.local_dir, QFileDialog.ShowDirsOnly)
    if not folder: return
    try:
      str(folder).decode('ascii')
    except UnicodeEncodeError:
      self.warn(tr("Please select a folder which path contains no unicode " +
        "characters."))
    else:
      self.local_dir = self.path(str(folder))
      self.update_local()

  def update_label(self, label, text):
    elided_text = QFontMetrics(label.font()).elidedText(text,
      Qt.ElideMiddle, label.width());
    label.setText('<a href="' + text + '"' + link_style + '>' +
      elided_text + '</a>');

  def update_remote(self):
    self.update_label(self.remote, remote_repository)

  def update_local(self):
    self.update_label(self.local, self.local_dir)
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
    self.buttons_all_frozen = True

  def unfreeze_buttons(self):
    for index, button in enumerate(self.buttons):
      button.setEnabled(True)
    self.buttons_all_frozen = False

  def clone_begin(self):
    self.console_append(tr('Connecting...'))
    self.pull.setText(tr('Processing...'))
    self.freeze_buttons()

  def clone_finish(self):
    self.pull.setText(tr('Download/Update'))
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
    self.install.setText(tr('Processing...'))
    self.freeze_buttons()

  def install_finish(self, return_code):
    self.install.setText(tr('Install'))
    self.unfreeze_buttons()
    if return_code is 0:
      self.console_append(tr('All packages have been successfully installed.'))

  def install_clicked(self):
    if self.validate_node() is not True: return
    self.console_clear()
    node = Node(self, self.local_dir, [ NPM, "install" ])
    node.progress.connect(self.console_append)
    node.error.connect(self.console_append)
    node.begin.connect(self.install_begin)
    node.finish.connect(self.install_finish)
    node.start()

  preview_timer = None

  def preview_begin(self):
    self.previewing = False
    self.preview.setText(tr('Processing...'))
    self.freeze_buttons()
    self.preview_timer = QTimer(self)
    self.preview_timer.setInterval(5000)
    self.preview_timer.setSingleShot(True)
    self.preview_timer.timeout.connect(self.preview_previewing)
    self.preview_timer.start()

  def preview_previewing(self):
    self.previewing = True
    self.preview.setEnabled(True)
    self.preview.setText(tr('Close'))

  def preview_finish(self, return_code=-1):
    self.previewing = False
    self.preview.setText(tr('Preview'))
    self.unfreeze_buttons()
    try:
      self.preview_timer.stop()
    except:
      pass

  def preview_closed(self):
    self.console_append(tr('Preview is now closed.'))
    self.preview_finish()

  def preview_clicked(self):
    if self.previewing:
      try:
        self.preview_process.finish.disconnect(self.preview_finish);
        self.freeze_buttons()
        self.preview_process.process.kill()
      except:
        pass
      finally:
        QTimer.singleShot(1000, self.preview_closed)
    else:
      if self.validate_node() is not True: return
      if self.validate_package() is not True: return
      self.console_clear()
      node = Node(self, self.local_dir, [ GRUNT ])
      node.progress.connect(self.console_append)
      node.error.connect(self.console_append)
      node.begin.connect(self.preview_begin)
      node.finish.connect(self.preview_finish)
      node.start()
      self.preview_process = node

  def validate_node(self):
    if not NODE or not os.path.isfile(NODE):
      return self.warn(tr("Node.js executable file is missing. " +
        "You may need to re-install this software."))
    else:
      if NODE_SHASUM[0] is '{':
        print 'Warning: NODE_SHASUM is empty.'
      else:
        try:
          if shasum(NODE) != NODE_SHASUM: raise None
        except:
          return self.warn(tr("Node.js executable file is corrupted. " +
            "You may need to re-install this software."))
    if not os.path.isfile(NPM):
      return self.warn(tr("NPM is missing. " +
        "You may need to re-install this software."))
    return True

  def validate_package(self):
    if not os.path.isfile(GRUNT):
      return self.warn(tr("Grunt is missing. " +
        "You may need to re-install this software."))
    if not os.path.isfile(os.path.join(self.local_dir, 'package.json')):
      return self.warn(tr("The package.json file is not " +
        "found in local directory. Please update your repository."))
    if not os.path.isfile(os.path.join(self.local_dir, 'Gruntfile.js')):
      return self.warn(tr("The Gruntfile.js file is not found in local " +
        "directory. Please update your repository."))
    if not os.path.isdir(os.path.join(self.local_dir, 'node_modules', 'grunt')):
      return self.warn(tr("Grunt is not installed in node_modules directory. " +
        "Please click Install button first."))
    return True

  def assemble_begin(self):
    self.assemble.setText(tr('Processing...'))
    self.freeze_buttons()

  def assemble_finish(self, return_code):
    self.assemble.setText(tr('Assemble'))
    self.unfreeze_buttons()

  def assemble_clicked(self):
    if self.validate_node() is not True: return
    if self.validate_package() is not True: return
    self.console_clear()
    node = Node(self, self.local_dir, [ GRUNT, "make" ])
    node.progress.connect(self.console_append)
    node.error.connect(self.console_append)
    node.begin.connect(self.assemble_begin)
    node.finish.connect(self.assemble_finish)
    node.start()

  def warn(self, text):
    QMessageBox.warning(self, tr("Error"), text)

def tr(msg):
  return QCoreApplication.translate("@default", msg)

def already_running():
  pid = os.getpid()
  ppid = os.getppid() if hasattr(os, 'getppid') else -1
  for proc in psutil.process_iter():
    try:
      if proc.exe == psutil.Process(pid).exe:
        if ppid == -1: ppid = proc.ppid
        # print proc.pid, proc.ppid, pid, ppid
        if (proc.pid == pid and proc.ppid == ppid) or (proc.pid == ppid):
          pass
        else:
          return True
    except:
      pass
  return False

if __name__ == '__main__':

  while True:

    app = QApplication(sys.argv)
    app.setApplicationName(tr('CGHAssemble'))

    if WINDOWS:
      font = QFont()
      font.setFamily('Verdana')
      app.setFont(font)

    try:
      lang = str(SETTINGS.value('lang').toString())
      translator = QTranslator()
      translator.load(os.path.join(basedir, 'i18n', lang))
      app.installTranslator(translator)
    except:
      pass

    if already_running():
      widget = QWidget()
      set_window_icon(widget)
      QMessageBox.warning(widget, tr("Error"), tr("CGHAssemble is already " +
        "running."))
      return_code = 1
      break

    main = MainWindow()
    main.show()
    main.raise_()
    return_code = app.exec_()

    if return_code is REBOOT_CODE:
      del app
      del main
    else:
      break

  try:
    main.preview_process.process.kill()
  finally:
    sys.exit(return_code)
