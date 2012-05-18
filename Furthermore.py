#!/usr/bin/env python

import sys
from PyQt4 import QtGui, QtCore
from Window import MainWindow


class Application(QtGui.QApplication):
    
	"""
		Main application class derived from QApplication.
	"""
    
	def __init__(self):
		QtGui.QApplication.__init__(self, sys.argv)
		
		self.main = MainWindow()
		self.main.show()

		
if __name__ == "__main__":
	    application = Application()
	    sys.exit(application.exec_())
