#!/usr/bin/env python

__author__="Benjamin Trias"
__version__ = '0.5'

# Furthermore is currently under development.
# Copyright : (C) 2012 by Benjamin Trias
# E-mail : jesuisbenjamin@gmail.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# http://www.gnu.org/licenses/licenses.html#GPL

from __future__ import division
from PyQt4 import QtGui, QtCore
from popplerqt4 import Poppler


class MainWindow(QtGui.QMainWindow):

	"""
		Main window to the application.
	"""

	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)

        	self.application = QtCore.QCoreApplication.instance()

		self.setWindowTitle('Furthermore')

		self.display = Display(self)
		self.setCentralWidget(self.display)

		self.toolbar = ToolBar(self)
		self.addToolBar(self.toolbar)

		self.createMenuBar()

		# TODO: loading the document this way is only for development purpose
		#self.display.displayDocument('/home/benjamin/test_large.pdf')

	def createMenuBar(self):

		"""
			Builds up menu bar and its content.
		"""

		menubar = self.menuBar()
		menu_app = menubar.addMenu('Furthermore')
		menu_doc = menubar.addMenu('Document')

		action_pref = QtGui.QAction('Preferences', self)
		action_pref.setShortcut('Ctrl+P')
		action_pref.setStatusTip('Change your preferences.')
		#action_pref.triggered.connect()
		menu_app.addAction(action_pref)

		action_help = QtGui.QAction('Help', self)
		action_help.setShortcut('Ctrl+H')
		action_help.setStatusTip('Help with Furthermore.')
		#action_help.triggered.connect()
		menu_app.addAction(action_help)

		action_about = QtGui.QAction('About', self)
		action_about.setShortcut('Ctrl+Shft+A')
		action_about.setStatusTip('Information about Furthermore.')
		#action_about.triggered.connect()
		menu_app.addAction(action_about)

		action_quit = QtGui.QAction('Quit', self)
		action_quit.setShortcut('Ctrl+Q')
		action_quit.setStatusTip('Quit Furthermore.')
		action_quit.triggered.connect(QtGui.qApp.quit)
		menu_app.addAction(action_quit)

		action_open = QtGui.QAction('Open...', self)
		action_open.setShortcut('Ctrl+O')
		action_open.setStatusTip('Open a new document.')
		action_open.triggered.connect(self.display.displayDocument)
		menu_doc.addAction(action_open)

		
		



class Display(QtGui.QScrollArea):

	"""
		Scroll Area display for PDF document and annotations.
	"""

	def __init__(self, parent=None):
		QtGui.QScrollArea.__init__(self, parent)
        
		self.application = QtCore.QCoreApplication.instance()
		self.scale = 100
		self.max_scale = 400
		self.min_scale = 10
		self.setBackgroundRole(QtGui.QPalette.Dark)

	
	def displayDocument(self):
		
		""" 
			Loads the PDFDocument widget (derived from QFrame)
		"""
		
		uri = QtGui.QFileDialog.getOpenFileName(self, "Choose a PDF file", '/home')
		try:
			self.document = Document(uri, self)
			self.setWidget(self.document)
			self.setWidgetResizable(True)
			self.setAlignment(QtCore.Qt.AlignCenter)
		except:
			pass

	def zoomIn(self):

		"""
			Increments the scale of the document.
		"""

		if self.scale == self.max_scale:
			return
		self.scale += 10
		self.document.applyScale()

	def zoomOut(self):

		"""
			Decrements the scale of the document.
		"""

		if self.scale == self.min_scale:
			return
		self.scale -= 10
		self.document.applyScale()
		
	
class ToolBar(QtGui.QToolBar):

	"""
		Main window's toolbar.
	"""

	def __init__(self, parent=None):
		QtGui.QToolBar.__init__(self, parent)
		
		self.display = self.parent().display

		self.zoomInAction = QtGui.QAction('Zoom in', self)
		self.zoomInAction.triggered.connect(self.display.zoomIn)
		self.addAction(self.zoomInAction)

		self.zoomOutAction = QtGui.QAction('Zoom out', self)
		self.zoomOutAction.triggered.connect(self.display.zoomOut)
		self.addAction(self.zoomOutAction)		


class Document(QtGui.QFrame):

	"""
		Document where all pages are layed out.
		The document consists of QLabels.
	"""

	def __init__(self, uri, parent=None):
		QtGui.QFrame.__init__(self, parent)

       		self.application = QtCore.QCoreApplication.instance()
		self.display = self.parent()
		
		self.source = Poppler.Document.load(uri)
		self.source.setRenderHint(Poppler.Document.TextAntialiasing)
		self.source.setRenderHint(Poppler.Document.Antialiasing)

		self.layOutPages()

	def showEvent(self, event):

		"""
			Check which page are visible on opening the document.
		"""
		
		self.checkVisibility()
		event.ignore()

	def moveEvent(self, event):
		
		"""
			Check if any page has become visible after moving.
		"""

		self.checkVisibility()
		event.ignore()

	def resizeEvent(self, event):

		"""
			Check if any page has become visible after scaling.
		"""

		self.checkVisibility()
		event.ignore()

	def checkVisibility(self):

		"""
			Check which page is visible and apply image if necessary.
		"""

		for page in self.getPages():
			if not page.visibleRegion().isEmpty() and not page.image.hasPixmap():
				# i.e. page is visible and has yet not pixmap rendered
				page.setPixmap()
			else:
				pass

	def layOutPages(self):

		"""
			Creates blank page widgets (QFrame) according to the size
			provided by Poppler Pages.	
		"""

		self.layout = QtGui.QVBoxLayout()

		for page_number, source_page in enumerate(self.getSourcePages()):
			blank_page = Page(page_number, source_page.pageSize(), self)
			self.layout.addWidget(blank_page)
		
		self.setLayout(self.layout)
		self.layout.setAlignment(QtCore.Qt.AlignCenter)

	def getSourcePages(self):
		
		"""
			Returns a list of Poppler.Pages from content.
		"""

		source_pages = []

		for number in range(self.source.numPages()):
			source_page = self.source.page(number)
			source_pages.append(source_page)
		return source_pages

	def getSourcePage(self, page_number):
		
		"""
			Returns a single Poppler.Page from content, based on page number.
		"""

		return self.source.page(page_number)

	def getPages(self):

		"""
			Returns a list of page widgets (QFrame) from document widget.
		"""

		pages = []
		for child in self.children():
			if isinstance(child, Page):
				pages.append(child)
			else:
				pass
		return pages

	def getPage(self, page_number):

		"""
			Returns page widget (QFrame) for page number.
		"""
		
		return self.getPages()[page_number]

	def getPageNumber(self, page):

		"""
			Returns page number of page.
		"""

		return page.page_number

	def applyScale(self):							#TODO Apply scale to visible only and gain speed.

		"""
			Set pages' image size to scale.
		"""
		
		scale = self.display.scale / 100

		for page in self.getPages():
			page_number = self.getPageNumber(page)
			size = self.getSourcePage(page_number).pageSize()
			page.image.setFixedSize(size.width() * scale, size.height() *scale)


class Page(QtGui.QFrame):

	"""
		Abstract page of oject containing data and image.
	"""

	def __init__(self, page_number, size, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.page_number = page_number
		self.document = self.parent()
		self.display = self.document.parent()

		self.layout = QtGui.QHBoxLayout()
		self.image = Image(size, self)
		self.layout.addWidget(self.image)
		self.setLayout(self.layout)

	def setPixmap(self):							#TODO: run this as a thread and gain speed.

		"""
			Renders and sets pixmap into Image label.
		"""
		
		if self.image.hasPixmap():
			return

		source = self.document.getSourcePage(self.page_number)
		scale = self.display.max_scale / 100
		image = source.renderToImage(72*scale, 72*scale)
		pixmap = QtGui.QPixmap.fromImage(image)
		self.image.setPixmap(pixmap)
		self.image.pixmap = True
	

class Image(QtGui.QLabel):

	"""
		Image of the PDF to display on Page.
	"""

	def __init__(self, size, parent=None):
		QtGui.QLabel.__init__(self, parent)		

		self.setFixedSize(size)
		self.setStyleSheet("Image { background-color : white}")
		self.setScaledContents(True)
		self.pixmap = None

	def hasPixmap(self): 

		"""
			Tells whether Image label already has a rendered pixmap.
		"""

		if self.pixmap:
			return True
		else:
			return False

		
	
