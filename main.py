"""
Start creating on Tue. Jan. 2, 2020
author: koharite

Image Editor Software using Qt for Python (PySide2)

Software has viewer function of image and editor funciton of layer image.

"""

# import libraries
from PySide2.QtCore import (QRect, QLineF, QPoint, QPointF, QRectF, Qt, QSize)
from PySide2.QtWidgets import (QMainWindow, QApplication, QWidget, QMessageBox, QFileDialog, \
    QHBoxLayout, QVBoxLayout, QFormLayout, QSizePolicy, QStyle, \
    QLabel, QLineEdit, QPushButton, QComboBox, QSlider, QAction, QActionGroup, QButtonGroup, \
    QGraphicsScene, QGraphicsView, QGraphicsPixmapItem)
from PySide2.QtGui import(QIcon, QImage, QPixmap, QPainter, QColor, QPen)

import sys
import os
import json
import pprint
import numpy as np

import colormap
from custom_object import GraphicsSceneForMouseAction

# Main Window components
class MainWindow(QMainWindow):

    def __init__(self):

        # load setting json file
        with open('setting.json') as f:
            self.app_setting = json.load(f)


        # Status of window
        super().__init__()
        self.title = 'Image Editor'
        self.left = 70
        self.top = 70
        self.width = 800
        self.height = 700

        # Status of view image
        self.org_qimg = None
        self.org_img_width = 0
        self.org_img_height = 0

        self.layer_pixmap = None
        self.layer_width = 0
        self.layer_height = 0
        self.layer_alpha = 50.0

        # Prepare color bar data
        self.colormap_gain = self.app_setting["SoftwareSetting"]["process"]["colormap"]["gain"]
        self.colormap_offset_x = self.app_setting["SoftwareSetting"]["process"]["colormap"]["offset_x"]
        self.colormap_offset_green = self.app_setting["SoftwareSetting"]["process"]["colormap"]["offset_green"]

        self.colormap_data = [colormap.colorBarRGB(x * 0.001, self.colormap_offset_x, self.colormap_offset_green, self.colormap_gain) for x in range(1000)]

        self.img_edit_mode = 'cursor'

        # setup user interface components
        self.setup_ui()
        

    # Setup user interface components
    def setup_ui(self):
        # Set main window title
        self.setWindowTitle(self.title)
        # Set main wiodow initial position
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Set up mainWindow's layout
        self.mainWidget = QWidget(self) # Note not to forget this code.
        self.main_layout = QVBoxLayout()

        # Set menu for main window
        self.main_menu = self.menuBar()
        self.file_menu = self.main_menu.addMenu('File')
        self.edit_menu = self.main_menu.addMenu('Edit')
        self.option_menu = self.main_menu.addMenu('Option')
        self.help_menu = self.main_menu.addMenu('Help')

        self.main_layout.addWidget(self.main_menu)

        # Set "Original Image Open" menu
        self.org_img_open_button = QAction(self.style().standardIcon(getattr(QStyle, 'SP_FileDialogStart')), 'Orginal Image Open', self)
        self.org_img_open_button.setShortcut('Ctrl+O')
        self.org_img_open_button.triggered.connect(self.open_org_img_dialog)
        self.file_menu.addAction(self.org_img_open_button)

        
        # Set "exit software" menu
        self.exit_button = QAction(self.style().standardIcon(getattr(QStyle, 'SP_DialogCloseButton')), 'Exit', self)
        self.exit_button.setShortcut('Ctrl-Q')
        self.exit_button.setStatusTip('Exit software')
        self.exit_button.triggered.connect(self.close)
        self.file_menu.addAction(self.exit_button)

        
        self.upper_layout = QHBoxLayout()
        self.main_layout.addLayout(self.upper_layout)

        # Set image display area
        self.gview_left = 20
        self.gview_top = 40
        self.gview_default_size = 500
        self.graphics_view = QGraphicsView()
        self.graphics_view.setFixedSize(self.gview_default_size, self.gview_default_size)
        self.upper_layout.addWidget(self.graphics_view)

        self.img_status_layout = QVBoxLayout()
        self.upper_layout.addLayout(self.img_status_layout)

        # Set tranparency value of layer image
        self.transparency_title_label = QLabel('layer transparency value')
        self.img_status_layout.addWidget(self.transparency_title_label)

        transparency = round((1.0 - self.layer_alpha/255.0)*100)
        self.img_transparency_edit = QLineEdit(str(transparency))

        self.img_transparency_sld = QSlider(Qt.Horizontal)
        self.img_transparency_sld.setFocusPolicy(Qt.NoFocus)
        self.img_transparency_sld.setRange(0, 100)
        self.img_transparency_sld.setValue(transparency)

        self.transparency_layout = QFormLayout()
        self.transparency_layout.addRow(self.img_transparency_sld, self.img_transparency_edit)
        self.img_status_layout.addLayout(self.transparency_layout)

        # Signal of transparency value changed
        self.img_transparency_sld.valueChanged.connect(self.transparency_change_sld)
        self.img_transparency_edit.textChanged.connect(self.transparency_change_edit)

        self.img_editor_layout = QVBoxLayout()
        self.img_status_layout.addLayout(self.img_editor_layout)
        
        # Set attention map editor tool
        self.img_editor_tool1_layout = QHBoxLayout()
        self.img_editor_layout.addLayout(self.img_editor_tool1_layout)
        self.tool_button_size = 64

        # Set Mouse cursor
        self.mouse_cursor_button = QPushButton()
        self.mouse_cursor_button.setIcon(QIcon('icon/cursor.png'))
        self.mouse_cursor_button.setCheckable(True)
        self.mouse_cursor_button.setIconSize(QSize(self.tool_button_size, self.tool_button_size))
        self.img_editor_tool1_layout.addWidget(self.mouse_cursor_button)
        
        # Set Pen
        self.pen_button = QPushButton()
        self.pen_button.setIcon(QIcon('icon/pen.png'))
        self.pen_button.setCheckable(True)
        self.pen_button.setIconSize(QSize(self.tool_button_size, self.tool_button_size))
        self.img_editor_tool1_layout.addWidget(self.pen_button)

        # Set Eraser
        self.eraser_button = QPushButton()
        self.eraser_button.setIcon(QIcon('icon/eraser.png'))
        self.eraser_button.setCheckable(True)
        self.eraser_button.setIconSize(QSize(self.tool_button_size, self.tool_button_size))
        self.img_editor_tool1_layout.addWidget(self.eraser_button)

        # Group button of mouse cursor, pen, eraser
        self.img_editor_tool1_group1 = QButtonGroup()
        self.img_editor_tool1_group1.addButton(self.mouse_cursor_button, 1)
        self.img_editor_tool1_group1.addButton(self.pen_button, 2)
        self.img_editor_tool1_group1.addButton(self.eraser_button, 3)

        # Set signal-slot of image editor button 
        self.mouse_cursor_button.toggled.connect(self.mouse_cursor_button_toggled)
        self.pen_button.toggled.connect(self.pen_button_toggled)
        self.eraser_button.toggled.connect(self.eraser_button_toggled)


        # Set color bar
        self.color_bar_width = 64
        self.color_bar_height = 256
        self.color_bar_view = QGraphicsView()
        self.color_bar_view.setFixedSize(self.color_bar_width+3, self.color_bar_height+3)
        self.color_bar_scene = QGraphicsScene()

        for i in range(self.color_bar_height):
            # Set drawing pen for colormap 
            ii = round(i * (1000/256))
            pen = QPen(QColor(self.colormap_data[ii][0], self.colormap_data[ii][1], self.colormap_data[ii][2]), 1, Qt.SolidLine, \
                Qt.RoundCap, Qt.RoundJoin)
            self.color_bar_scene.addLine(0, self.color_bar_height - i-1, self.color_bar_width, self.color_bar_height - i-1, pen)

        self.color_bar_view.setScene(self.color_bar_scene)

        self.img_editor_tool1_layout.addWidget(self.color_bar_view)


        # Set thickness of Pen or Eraser

        self.graphics_view.setObjectName("imageDisplayArea")

        # Set display area of selected file path
        self.org_img_path_title_label = QLabel('original image file: ')
        self.org_img_path_label = QLabel('')

        self.file_path_layout = QFormLayout()
        self.file_path_layout.addRow(self.org_img_path_title_label, self.org_img_path_label)

        self.bottom_layout = QVBoxLayout()
        self.bottom_layout.addLayout(self.file_path_layout)
        self.main_layout.addLayout(self.bottom_layout)

        self.mainWidget.setLayout(self.main_layout)
        self.setCentralWidget(self.mainWidget)


        # image display area's contents
        self.scene = GraphicsSceneForMouseAction(self.graphics_view, self)
        self.imgs_pixmap = []
        self.imgs = []
        

    # Original image select Function
    def open_org_img_dialog(self):
        options = QFileDialog.Options()
        org_img_default_path = self.app_setting["SoftwareSetting"]["file_path"]["org_img_dir"]
        self.org_img_file_path, selected_filter = QFileDialog.getOpenFileName(self, 'Select original image', org_img_default_path, \
            'Image files(*.jpg *jpeg *.png)', options=options)
        
        org_img_dir_path, org_img_file = os.path.split(self.org_img_file_path)
        org_img_bare_name, org_img_ext = os.path.splitext(org_img_file)

        self.org_img_path_label.setText(self.org_img_file_path)
        
        self.set_image_on_viewer()

    def set_image_on_viewer(self):
        # Delete existing image item
        if len(self.imgs_pixmap) != 0:
            for item in self.imgs_pixmap:
                self.scene.removeItem(item)
                
        self.imgs_pixmap.clear()
        self.imgs.clear()

        # load original image
        self.org_qimg = QImage(self.org_img_file_path)
        self.org_pixmap = QPixmap.fromImage(self.org_qimg)
        org_img_size = self.org_qimg.size()
        self.org_img_width = org_img_size.width()
        self.org_img_height = org_img_size.height()

        # Set layer image
        self.layer_qimg = QImage(self.org_img_width, self.org_img_height, QImage.Format_RGBA8888)
        self.layer_qimg.fill(QColor(0, 0, 0, self.layer_alpha))
        self.layer_pixmap = QPixmap.fromImage(self.layer_qimg)

        self.imgs.append(self.org_qimg)
        self.imgs.append(self.layer_qimg)
        # Set image to scene
        self.imgs_pixmap.append(QGraphicsPixmapItem(self.org_pixmap))
        self.scene.addItem(self.imgs_pixmap[-1])
        self.imgs_pixmap.append(QGraphicsPixmapItem(self.layer_pixmap))
        self.scene.addItem(self.imgs_pixmap[-1])

        self.scene.set_img_contents(self.imgs)

        # Set scene to graphics view
        self.graphics_view.setScene(self.scene)
        self.graphics_view.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self.show()

    # Slot function of transparency slider changed
    def transparency_change_sld(self, value):
        self.img_transparency_edit.setText(str(value))
        self.layer_alpha = int(255*(1.0-(value/100)))

        # Change layer image's transparency(alpha value)
        for y in range(self.org_img_height):
            for x in range(self.org_img_width):
                self.layer_qimg.setPixelColor(QPoint(x, y), QColor(0, 0, 0, self.layer_alpha))
                
        self.layer_pixmap = QPixmap.fromImage(self.layer_qimg)

        # remove previous attention map image
        self.scene.removeItem(self.imgs_pixmap[-1])
        self.imgs_pixmap.pop(-1)

        # add new attention map image to scene
        self.imgs_pixmap.append(QGraphicsPixmapItem(self.layer_pixmap))
        self.scene.addItem(self.imgs_pixmap[-1])

        self.show()

        # Slot function of transparency text edit changed
    def transparency_change_edit(self, value):
        if int(value) < 0 or int(value) > 100:
            return

        self.img_transparency_sld.setValue(int(value))
        self.layer_alpha = int(255*(1.0-(int(value)/100.0)))

         # Change layer image's transparency(alpha value)
        for y in range(self.org_img_height):
            for x in range(self.org_img_width):
                self.layer_qimg.setPixelColor(QPoint(x, y), QColor(0, 0, 0, self.layer_alpha))
                
        self.layer_pixmap = QPixmap.fromImage(self.layer_qimg)

        # remove previous attention map image
        self.scene.removeItem(self.imgs_pixmap[-1])
        self.imgs_pixmap.pop(-1)

        # add new attention map image to scene
        self.imgs_pixmap.append(QGraphicsPixmapItem(self.layer_pixmap))
        self.scene.addItem(self.imgs_pixmap[-1])

        self.show()

    # slot(receiver of signal) of mouse_cursor_button toggled 
    def mouse_cursor_button_toggled(self, checked):
        if checked:
            self.img_edit_mode = 'cursor'
            self.scene.set_mode(self.img_edit_mode)

    # slot(receiver of signal) of pen_button toggled 
    def pen_button_toggled(self, checked):
        if checked:
            self.img_edit_mode = 'pen'
            self.scene.set_mode(self.img_edit_mode)

    # slot(receiver of signal) of eraser_button toggled 
    def eraser_button_toggled(self, checked):
        if checked:
            self.img_edit_mode = 'eraser'
            self.scene.set_mode(self.img_edit_mode)
        
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
