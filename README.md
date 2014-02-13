CGHAssemble v1.0.0.0
====================

A stupid Assemble tool.

This is a handy cross-platform desktop app to use [Assemble](
http://assemble.io/), a static website generator written in Node.js.
The app can download a Assemble website git repository to local
directory, install dependencies and run grunt tasks.

Designed for those probably every-day Windows users who know how
to edit templates and HTML/CSS/JS files but don't know much about the
commands.

This app bundles with npm, grunt-cli and latest stable version of
platform-specific Node.js binary. Supports high DPI/retina screen.

Conventions:

* ``grunt`` to assemble the site in development mode.
* ``grunt make`` to assemble the site in production mode.
* File names can contain Unicode characters but it is not recommended
to do so.

If you want to use this tool with your own repository or to use
different grunt command, you must build it on your own.
Build suggestions on Windows: Download msysgit (PortableGit),
mintty (msys), Python 2.7.6, PyQt4 Windows binaries, NSIS, and then
install Python packages like PyInstaller.

Translations
------------

To get a list of words to start translating, run:

    pylupdate4 main.py -ts i18n/zh.ts

Once you completes editing the ts file, 'compile' it:

    lrelease i18n/zh.ts

The Qt Linguist that helps translating .ts file can be found
[here](https://code.google.com/p/qtlinguistdownload/)

Bugs
----

* In exchange of not showing a weird command-line window the console
(output) area may 'freeze' for a period of time while processing tasks
on some versions of Windows.

Developer
---------

caiguanhao &lt;caiguanhao@gmail.com&gt;
