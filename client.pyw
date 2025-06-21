import sys,win32event,win32api
from PyQt5.QtWidgets import*
from PyQt5.QtGui import QIcon
m=win32event.CreateMutex(None,1,'multiclient_singletonMutex')
if win32api.GetLastError()==183:sys.exit()
a=QApplication([])
a.setQuitOnLastWindowClosed(False)
if not QSystemTrayIcon.isSystemTrayAvailable():sys.exit()
t=QSystemTrayIcon(a.style().standardIcon(a.style().SP_TitleBarMaxButton))
m=QMenu()
e=QAction('Exit')
e.triggered.connect(a.quit)
m.addAction(e)
t.setContextMenu(m)
t.setToolTip('Multiclient')
t.show()
t.showMessage('Multiclient','Started',QSystemTrayIcon.Information,2000)
sys.exit(a.exec_())