### Curses binaries

The curses binaries were downloaded from [Cristoph Gohlke's Unofficial Windows Binaries for Python Extension Packages 
directory](https://www.lfd.uci.edu/~gohlke/pythonlibs/) - the author of the page claims 
that the source code from [PDCurses](https://github.com/wmcbrine/PDCurses) ([project's webpage](https://pdcurses.org/)) 
was utilized.

The files files are provided "as is" without warranty or support of any kind. The entire risk as to the quality and
performance is with you.

As of June 14th 2020, the the referred Gohlke's page only asks to "refer to the documentation of the individual packages
for license restrictions" and both the PDCurses Github page and project's webpage refer to the source code of PDCurses 
as public domain, noting that "small portions of PDCurses are subject to copyright under various licenses". Please refer
to their webpages to gather information about the current licensing state of these binaries and the PDCurses source
code. 

The PDCurses library python extension for windows hosts on this directory are used as a convenience tool to facilitate
the development of TASIAp, serving as a replacement for the X/Open Curses library available for Unix hosts; this
library is required by the telnetsrv package used in this project to set a mocking Telnet server as a testing
environment for telnet related functions during the development. The final product does not contain any portion of
PDCurses in it and neither requires any kind of Curses library to run.

#### Install
Download the wheel file relative to your system and Python version and install it directly using pip. This examples
refers to Windows 64 bits with Python version 3.8: 
```
pip install /path/to/curses-2.2.1+utf8-cp38-win_amd64.whl
``` 
