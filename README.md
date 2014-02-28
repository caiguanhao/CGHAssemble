CGHAssemble v1.0.4.0
====================

A stupid Assemble tool.

Introduction
------------

This is a handy cross-platform desktop app to use [Assemble](
http://assemble.io/), a static website generator written in Node.js.
The app can download a Assemble website git repository to local
directory, install dependencies and run grunt tasks.

Designed for those probably every-day Windows users who know how
to edit templates and HTML/CSS/JS files but don't know much about the
commands.

Tested on 32bit/64bit of Windows XP+, Mac OS X 10.9+, Ubuntu 10.04+ in
both normal and high DPI/retina screen.

This app bundles with npm, grunt-cli and latest stable version of
platform-specific Node.js binary.

Screenshots
-----------

![mac](https://f.cloud.github.com/assets/1284703/2184733/6df8363e-97c6-11e3-87f4-41ced658d7b5.png)

[More...](https://github.com/caiguanhao/CGHAssemble/issues/1)

Conventions
-----------

* ``grunt`` to assemble the site in development mode.
* ``grunt make`` to assemble the site in production mode.
* File names in git repository can contain Unicode characters
but it is not recommended to do so.

Install and Uninstall
---------------------

For Windows version, open the installer "CGHAssemble-...-setup.exe" to start
the installation. Once it completes, a shortcut link will appear either on
desktop or in the Start Menu. To uninstall, click "Uninstall CGHAssemble" from
the Start Menu or click remove from Add/Remove Programs in Control Panel.

For Mac version, download the zip file and unzip it. Drag the extracted .app
file to Applications folder. Right click CGHAssemble.app and then click Open.
In the warning dialog, click Open. To uninstall, move that CGHAssemble.app
to trash.

For Ubuntu version, download .deb file and open it. Click Install Package to
install. Or you can run ``sudo dpkg -i cgh-assemble-*.deb`` in the terminal.
To uninstall, open your package manager, find CGH-Assemble and mark the app
for removal and then click Apply. Or you can run ``sudo apt-get purge
cgh-assemble*`` in the terminal.

Make
----

* ``./configure`` to download dependencies.
* go to ``res`` directory and run ``make`` to generate icons.
* Optionally run ``make CleanNodeModules UglifyJS`` to compress Node modules.
* ``make`` to build the app, installer (or zip archive).
* ``make user=<different-user> repo=<different-repo>`` to build your own.
* ``make version=<new-version>`` to update the version number.

If you want to use this tool with your own repository or to use
different grunt command, you must build it on your own.
Build suggestions on Windows: Download msysgit (PortableGit),
mintty (msys), Python 2.7.6, PyQt4 Windows binaries, NSIS, and then
install Python packages like PyInstaller.

It is recommended to build the app on Windows XP and Ubuntu 10.04.

Bugs
----

* In exchange of not showing a weird command-line window, the console
(output) area may 'freeze' for a period of time while processing tasks
on some versions of Windows.

Developer
---------

caiguanhao &lt;caiguanhao@gmail.com&gt;
