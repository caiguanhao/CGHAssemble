Translations
------------

To get a list of words to start translating, run:

    pylupdate4 main.py -ts i18n/zh.ts

You can edit the translation file in your favorite text editor, or in
[Qt Linguist](https://code.google.com/p/qtlinguistdownload/).

Once you completes, run this command to generate the .qm file:

    lrelease i18n/zh.ts
