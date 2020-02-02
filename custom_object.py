"""
Start creating on Wed. Jan.3, 2020
author: koharite

Customized Object for Qt for Python (PySide2)

"""

# import libraries

from PySide2.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem)
from PySide2.QtGui import QColor


class GraphicsSceneForMouseAction(QGraphicsScene):

    def __init__(self, parent=None, window=None, mode='cursor'):
        QGraphicsScene.__init__(self, parent)
        # Set parent view area
        self.parent = parent
        # Set grand parent window
        self.window = window
        # Set action mode
        self.mode = mode
        
    def set_mode(self, mode):
        self.mode = mode

    def set_img_contents(self, img_contents):
        # image data of Graphics Scene's contents
        self.img_contents = img_contents
    
    def mousePressEvent(self, event):
        # For check program action
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()

        if self.mode == 'cursor':
            # Get items on cursor
            #items = self.itemAt(pos, QTransform)
            #items = self.itemAt(pos, self.parent.viewportTransform())
            #img_val = [[0 for j in range(4)] for i in range(len(items))]
            #img_val = []
            #print('items:{items}'.format(items=items))
            message = '(x, y)=({x}, {y}) '.format(x=int(x), y=int(y))
            #for i, item in enumerate(items):
            #for item in items:
            for img in self.img_contents:
                #item_pixmap = items.pixmap()
                # Get pixel value
                #pix_val = item_pixmap.pixel(pos.x(), pos.y())
                pix_val = img.pixel(x, y)
                pix_rgb = QColor(pix_val).getRgb()
                #img_val.append(pix_rgb)
                #print('pix_rgb size={size}'.format(size=len(pix_rgb)))
                message += '(R, G, B) = {RGB} '.format(RGB=pix_rgb[:3])


            # show scene status on parent's widgets status bar
            self.window.statusBar().showMessage(message)


class GraphicsViewForMouseAction(QGraphicsView):

    def __init__(self, parent=None, mode='cursor'):
        QGraphicsView.__init__(self, parent)
        # Set parent widget(window)
        self.parent = parent
        # Set action mode
        self.mode = mode
    
    def set_mode(self, mode):
        self.mode = mode

    def mousePressEvent(self, event):
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()

        if self.mode == 'cursor':
            item = self.itemAt(x, y)