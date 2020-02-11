"""
Start creating on Fri. Jan.3, 2020
author: koharite

Customized Object for Qt for Python (PySide2)

"""

# import libraries
from PySide2.QtCore import (Qt, Signal, QLineF)
from PySide2.QtWidgets import (QGraphicsView, QGraphicsScene, QGraphicsItem)
from PySide2.QtGui import (QColor, QPen)


class GraphicsSceneForMainView(QGraphicsScene):

    def __init__(self, parent=None, window=None, mode='cursor'):
        QGraphicsScene.__init__(self, parent)
        # Set parent view area
        self.parent = parent
        # Set grand parent window
        self.window = window
        # Set action mode
        self.mode = mode

        # mouse move pixels
        self.points = []

        # added line items
        self.line_items = []
        self.lines = []

        # added line's pen attribute
        self.pens = []
        
    def set_mode(self, mode):
        self.mode = mode

    def set_img_contents(self, img_contents):
        # image data of Graphics Scene's contents
        self.img_contents = img_contents

    def clear_contents(self):
        self.points.clear()
        self.line_items.clear()
        self.lines.clear()
        self.pens.clear()
        self.img_contents = None

    def mousePressEvent(self, event):
        # For check program action
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()

        if self.mode == 'cursor':
            # Get items on cursor
            message = '(x, y)=({x}, {y}) '.format(x=int(x), y=int(y))

            for img in self.img_contents:
                # Get pixel value
                pix_val = img.pixel(x, y)
                pix_rgb = QColor(pix_val).getRgb()
                message += '(R, G, B) = {RGB} '.format(RGB=pix_rgb[:3])

            # show scene status on parent's widgets status bar
            self.window.statusBar().showMessage(message)

        if self.mode == 'pen' or self.mode == 'eraser':
            if x >= 0 and x < self.width() and y >= 0 and y < self.height():
                if len(self.points) != 0:
                    draw_color = self.window.draw_color
                    # Set transparenc value
                    draw_color.setAlpha(self.window.layer_alpha)
                    draw_size = self.window.draw_tool_size
                    pen = QPen(draw_color, draw_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    self.lines_items.append(self.addLine(QLineF(self.points[-1].x(), self.points[-1].y(), x, y), pen=pen))
                    self.lines.append(self.lines_items[-1].line())
                    self.pens.append(pen)

                self.points.append(pos)

    def mouseMoveEvent(self, event):
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()

        if self.mode == 'cursor':
            # Get items on cursor
            message = '(x, y)=({x}, {y}) '.format(x=int(x), y=int(y))
            for img in self.img_contents:
                # Get pixel value
                pix_val = img.pixel(x, y)
                pix_rgb = QColor(pix_val).getRgb()
                message += '(R, G, B) = {RGB} '.format(RGB=pix_rgb[:3])

            # show scene status on parent's widgets status bar
            self.window.statusBar().showMessage(message)

        if self.mode == 'pen' or self.mode == 'eraser':
            if x >= 0 and x < self.width() and y >= 0 and y < self.height():
                if len(self.points) != 0:
                    draw_color = self.window.draw_color
                    # Set transparenc value
                    draw_color.setAlpha(self.window.layer_alpha)
                    draw_size = self.window.draw_tool_size
                    pen = QPen(draw_color, draw_size, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    self.line_items.append(self.addLine(QLineF(self.points[-1].x(), self.points[-1].y(), x, y), pen=pen))
                    self.lines.append(self.line_items[-1].line())
                    self.pens.append(pen)

                self.points.append(pos)

    def mouseReleaseEvent(self, event):
        self.points.clear()


# Class for graphics contents of tools on main window
class GraphicsSceneForTools(QGraphicsScene):
    # Define custom signal
    img_info = Signal(QColor)

    def __init__(self, parent=None, window=None):
        QGraphicsScene.__init__(self, parent)
        # Set parent view area
        self.parent = parent
        # Set grand parent window
        self.window = window
        self.mode = 'cursor'

    def set_mode(self, mode):
        self.mode = mode

    def set_img_content(self, img_content):
        # image data of Graphics Scene's contents
        self.img_content = img_content
    
    def mousePressEvent(self, event):
        # For check program action
        pos = event.scenePos()
        x = pos.x()
        y = pos.y()

        if self.mode == 'cursor' or self.mode == 'pen':
            self.pix_rgb = self.img_content.pixelColor(x, y)
            self.img_info.emit(self.pix_rgb)
