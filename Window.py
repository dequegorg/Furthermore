#!/usr/bin/env python

from __future__ import division

__author__="Benjamin"
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
		self.setMinimumSize(400, 300)
		self.showMaximized()

		self.display = Display(self)
		self.setCentralWidget(self.display)

		self.toolbar = ToolBar(self)
		self.addToolBar(self.toolbar)

		self.createMenuBar()
		self.clipboard = QtGui.QApplication.clipboard()



	def createMenuBar(self):						#TODO: should create toolbar this way too

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

		self.display = self.parent()
		self.source = Poppler.Document.load(uri)
		self.source.setRenderHint(Poppler.Document.TextAntialiasing)
		self.source.setRenderHint(Poppler.Document.Antialiasing)

		self.setContentsMargins(0, 0, 0, 0)
		self.layOutPages()
		
		# The rubberband is used to select text from the document.
		self.rubberband = QtGui.QRubberBand(QtGui.QRubberBand.Rectangle, self)
		self.rubberband.hide()
		self.selection = None # selection capture by rubberband
		
		print "document loaded"
	
	def mousePressEvent(self, event):

		"""
			Pick up event if mouse pressed on image.
		"""

		print "mouse press event"

		# Hide the selection mask if it was already there
		for page in self.getPages():
			page.image.selection_mask.removeFromPage()

		# Reset rubberband
		self.rubberband.origin = event.pos()				
		self.updateRubberbandGeometry(event.pos())
		self.rubberband.show()

	def mouseMoveEvent(self, event):

		"""
			Pick up event if mouse moves on image.
		"""
		
		print "mouse move event"
		
		self.updateRubberbandGeometry(event.pos())
		# scroll document if rubberband moving beyond display
		self.display.ensureVisible(event.pos().x(), event.pos().y(), 2, 2)

	def mouseReleaseEvent(self, event):


		"""
			Pick up event if mouse released.
		"""

		# get selection content and apply mask if needed.
		self.captureSelection()
		self.rubberband.hide()

	def showEvent(self, event):

		"""
			Check which page are visible on opening the document.
		"""
		
		print "show event"
		self.checkPageVisibility()
		event.ignore()

	def moveEvent(self, event):
		
		"""
			Check if any page has become visible after moving.
		"""

		print "move event"
		self.checkPageVisibility()
		event.ignore()

	def resizeEvent(self, event):

		"""
			Check if any page has become visible after scaling.
		"""
		
		print "resize event"
		self.checkPageVisibility()
		event.ignore()

	def applyScale(self):

		"""
			Sends a request to pages to update their size according to scale.
		"""

		for page in self.getPages():
			page.applyScale()

	def updateRubberbandGeometry(self, pos):

		"""
			Updates the ruberband geometry according to QPoint.
		"""
		
		origin = self.rubberband.origin
		difference = pos - origin

		if difference.x() > 0 and difference.y() > 0:
			# bottom right from origin
			self.rubberband.setGeometry(QtCore.QRect(origin, pos).normalized())
		elif difference.x() < 0 and difference.y() < 0:
			# top left from origin
			self.rubberband.setGeometry(QtCore.QRect(pos, origin).normalized())
		elif difference.x() > 0 and difference.y() < 0:
			# top right from origin
			fake_origin = QtCore.QPoint(origin.x(), pos.y())
			fake_end = QtCore.QPoint(pos.x(), origin.y())
			self.rubberband.setGeometry(QtCore.QRect(fake_origin, fake_end).normalized())
		elif difference.x() < 0 and difference.y() > 0:
			# top left from origin
			fake_origin = QtCore.QPoint(pos.x(), origin.y())
			fake_end = QtCore.QPoint(origin.x(), pos.y())
			self.rubberband.setGeometry(QtCore.QRect(fake_origin, fake_end).normalized())
		else:
			self.rubberband.setGeometry(QtCore.QRect(origin, pos).normalized())

	def checkPageVisibility(self):						

		"""
			Addresses potential changes to pages which are visible.
		"""

		print "checking page visibility"
		for page in self.getVisiblePages():
			page.checkPixmap()

	def getVisiblePages(self):


		"""
			Returns a list of pages currently visible in the display.
		"""

		print "getting visible pages"
		visible_pages = []

		for page in self.getPages():
			if not page.visibleRegion().isEmpty():
				visible_pages.append(page)

		return visible_pages			

	def layOutPages(self):

		"""
			Creates blank page widgets (QFrame) according to the size
			provided by Poppler Pages.	
		"""

		print "laying out pages"
		self.layout = QtGui.QVBoxLayout()
		self.layout.setSpacing(30)

		for page_number, source_page in enumerate(self.getSourcePages()):
			print "creating page", page_number
			blank_page = Page(page_number, source_page.pageSize(), self)
			self.layout.addWidget(blank_page)
		
		self.setLayout(self.layout)
		self.layout.setAlignment(QtCore.Qt.AlignCenter)

	def getSourcePages(self):
		
		"""
			Returns a list of Poppler.Pages from content.
		"""

		print "getting source pages"
		source_pages = []

		for number in range(self.source.numPages()):
			source_page = self.source.page(number)
			source_pages.append(source_page)
		return source_pages

	def getSourcePage(self, page_number):
		
		"""
			Returns a single Poppler.Page from content, based on page number.
		"""

		print "getting source page, for page number", page_number
		return self.source.page(page_number)

	def getPages(self):

		"""
			Returns a list of page widgets (QFrame) from document widget.
		"""

		print "getting pages"
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
		
		print "getting page", page_number
		return self.getPages()[page_number]

	def getPageNumber(self, page):

		"""
			Returns page number of page.
		"""

		print "getting page number for page", page
		return page.page_number

	def pageHasText(self, page):						#FIXME: should be a page method

		"""
			Returns True if Poppler.Page associated to Page contains text,
			otherwise returns False.
		"""

		print "checking if page", page.page_number," has text"
		if len(self.getSourcePage(self.getPageNumber(page)).textList()) == 0:
			return False
		else:
			return True

	def scaledFromSelection(self, selected_area, page):

		"""
			Returns a QRectF from selection, mapped to Poppler.Page.
		"""

		print "mapping selection to page"
		scale = self.display.scale / 100
		# convert document area to page-centric area in full scale.
		# NB: Page.Image.pixmap is loaded at full scale and stretched on display.
		return QtCore.QRectF((selected_area.x() - page.x()) / scale,
				      	(selected_area.y() - page.y()) / scale,
				      	selected_area.width() / scale,
				      	selected_area.height() / scale)
	
	def scaledToSelection(self, selection, page):

		"""
			Returns a QRectF from selection, mapped to Document.

		"""
		print "mapping page to selection"
		scale = self.display.scale / 100

		# since the selection is applied to image (whereas it was draw from document)
		# it is not necessary to add up the coordinate of the page.
		return QtCore.QRectF(selection.x() * scale - self.getPage(page).image.x(),
				      	selection.y() * scale - self.getPage(page).image.y(),
				      	selection.width() * scale,
				      	selection.height() * scale)
	
	def captureSelection(self):

		"""
			Registers pages, areas and text captured within rubberband's geometry.
		"""

		print "capturing selection"
		selection = []

		# impose a minimum of 10px width an height for selection to be valid
		if self.rubberband.geometry().width() < 10 or self.rubberband.geometry().height() < 10:
			print "print selection is too small"
			self.selection = selection
			return # the mask will therefore not be applied

		# otherwise selection ought to be on visible pages
		for page in self.getVisiblePages():
			# as well as intersect with any of those visible pages
			print "page geometry is", page.geometry()
			print "image geometry is", page.image.geometry()
			print "rubberband selection is", self.rubberband.geometry()
			if page.geometry().intersects(self.rubberband.geometry()):
				selected_area = page.geometry().intersected(self.rubberband.geometry())
				# we keep the true scale of the selection, i.e. what it would be at 100 %
				# that's easier to re-use and to handle if the document is scaled
				true_area = self.scaledFromSelection(selected_area, page)
				print "intersection is:", selected_area
				print "poppler selection is:", true_area
				if self.pageHasText(page):
					# see if there is text in this selected area of the Poppler.Page
					selected_text = self.getSourcePage(self.getPageNumber(page)).text(true_area)
				else:
					selected_text = QtCore.QString('')
				# keep the current selection for later 
				selection.append({
						'page_number' : self.getPageNumber(page),
						'area' : true_area,
				             	'text' : selected_text
					    	})
		
		self.selection = selection
		print "selection captured"
		for item in selection:
			print item

		# apply the mask to the selection
		if len(self.selection) > 0:
			for page in self.getPages():
				page.image.selection_mask.applyToPage()


		# paste selection to clipboard
		copy = []
		for item in self.selection:
			copy.append(unicode(item['text']))
		self.display.parent().clipboard.setText(''.join(copy))
	
	def isTextSelected(self):

		"""
			Checks whether there is text in selection.
		"""		
		
		print "checking if text is selected"
		for item in self.selection:
			if len(item['text']) > 0:
				return True
		return False

	def setFocusOnSelectedText(self):

		"""
			Masks the region of the document where the text is not selected.
		"""
		# for each selection scale text rect to display size
		#TODO: use QRect.united()
		# create document-wide mask
		# intersect mask with rects
		# show mask
		# ensure selection visible

		pass


class Page(QtGui.QFrame):

	"""
		Page of the Document, exclusively graphical.
	"""

	def __init__(self, page_number, size, parent=None):
		QtGui.QFrame.__init__(self, parent)
		
		self.page_number = page_number
		self.document = self.parent()
		self.display = self.document.parent()
		#self.setStyleSheet("Page { background-color : red}")

		self.setContentsMargins(0, 0, 0, 0)
		self.layout = QtGui.QHBoxLayout()
		self.image = Image(size, self)
		self.layout.addWidget(self.image)
		self.layout.setSpacing(0)
		self.layout.setContentsMargins(0, 0, 0, 0)
		self.setLayout(self.layout)
		print "page", page_number, "loaded"

	def setPixmap(self):							#TODO: run this as a thread and gain speed.

		"""
			Renders and sets pixmap into Image label.
		"""
		
		print "setting pixmap to page", self.page_number
		if self.image.hasPixmap():
			return

		source = self.document.getSourcePage(self.page_number)
		scale = self.display.max_scale / 100
		image = source.renderToImage(72*scale, 72*scale)
		pixmap = QtGui.QPixmap.fromImage(image)
		self.image.setPixmap(pixmap)
		self.image.pixmap = True
		self.image.data = image

	def hasPixmap(self):

		"""
			Returns True if the page's Image has a pixmap,
			otherwise False.
		"""
		print "checking if page has pixmap"
		return self.image.hasPixmap()

	def checkPixmap(self):

		"""
			Sets the pixmap to page if not already the case.
		"""

		if not self.hasPixmap():
			self.setPixmap()

	def applyScale(self):

		"""
			Set pages' image size to scale.
		"""
		print "applying scale to page", self.page_number
		scale = self.display.scale / 100

		size = self.document.getSourcePage(self.page_number).pageSize()
		self.image.setFixedSize(size.width() * scale, size.height() *scale)
		self.image.selection_mask.setFixedSize(size.width() * scale, size.height() *scale)

	

class Image(QtGui.QLabel):

	"""
		Image of the PDF to display on Page.
	"""

	def __init__(self, size, parent=None):
		QtGui.QLabel.__init__(self, parent)		

		self.setFixedSize(size)
		self.setStyleSheet("Image { background-color : white}")
		self.setContentsMargins(0, 0, 0, 0)
		self.setScaledContents(True)
		self.pixmap = None
		self.data = None
		self.selection_mask = Mask(self)

		print "image label loaded for page", self.parent().page_number

	def hasPixmap(self): 

		"""
			Tells whether Image label already has a rendered pixmap.
		"""

		if self.pixmap:
			return True
		else:
			return False

class Mask(QtGui.QWidget):

	def __init__(self, parent=None):
		QtGui.QWidget.__init__(self, parent)
		print "initiating mask"
		self.image = self.parent()
		self.page = self.image.parent()
		self.document = self.page.document
		self.display = self.document.display
		self.painter = QtGui.QPainter()
		self.applied = False
		print "mask created for page"

	def isApplied(self):

		return self.applied

	def applyToPage(self):

		#print "applying mask to page", self.page.page_number

		self.applied = True
		self.show()

	def removeFromPage(self):

		#print "removing mask from page", self.page.page_number

		self.applied = False
		self.hide()

	def paintEvent(self, event):

		print "\n Mask of page", self.page.page_number, "received paint event"
		event.accept()
		print "region to paint is", event.rect()

		if self.isApplied():
			print "applying mask..."
			# make sure the mask covers the entire page
			self.setGeometry(0, 0, self.image.width(), self.image.height())

			# define the mask
			path = QtGui.QPainterPath()
			path.setFillRule(QtCore.Qt.OddEvenFill)
			path.addRect(QtCore.QRectF(0, 0, self.image.width(), self.image.height()))
			# inset focus areas
			for item in self.document.selection:
				if self.page.page_number == item['page_number']:
					print "cutting selection out of mask"
					# get area to display according to scale and page index
					rect = self.document.scaledToSelection(item['area'], self.page.page_number)
					print "mask selection", rect
					path.addRect(rect)

			# apply the mask
			self.painter.begin(self)
			self.painter.setBrush(QtGui.QBrush(QtGui.QColor(100, 100, 100, 70)))
			self.painter.setPen(QtGui.QPen(QtGui.QColor(100, 100, 100, 70)))
			self.painter.drawPath(path)
			self.painter.end()
		else:
			print "removing mask"
			pass









		
	
