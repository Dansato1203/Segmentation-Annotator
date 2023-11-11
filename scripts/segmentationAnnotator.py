import os
import numpy as np
import cv2

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap

from magicWand import MagicWand

from segmentation_utils import remove_segment_at_point

class SegmentationAnnotator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Segmentation Annotator")
        self.showMaximized()  # GUIを全画面で表示

        self.magic_wand = MagicWand()

        self.central_widget = QtWidgets.QWidget()  # 中央のウィジェット
        self.setCentralWidget(self.central_widget)

        self.main_layout = QtWidgets.QHBoxLayout(self.central_widget)  # 水平レイアウト

        # 画像表示用のウィジェット
        self.original_image_label = QtWidgets.QLabel("Original Image")
        self.original_image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.processed_image_label = QtWidgets.QLabel("Processed Image")
        self.processed_image_label.setAlignment(QtCore.Qt.AlignCenter)

        # 画像表示エリアにスクロールバーを追加
        self.scroll_area_original = QtWidgets.QScrollArea()
        self.scroll_area_original.setWidgetResizable(True)
        self.scroll_area_original.setWidget(self.original_image_label)

        self.scroll_area_processed = QtWidgets.QScrollArea()
        self.scroll_area_processed.setWidgetResizable(True)
        self.scroll_area_processed.setWidget(self.processed_image_label)

        # 画像切り替えボタンとラベル選択ボタンのレイアウトを作成
        self.left_layout = QtWidgets.QVBoxLayout()  # 垂直レイアウト
        self.right_layout = QtWidgets.QVBoxLayout()  # 垂直レイアウト
        self.label_layout = QtWidgets.QVBoxLayout()  # 垂直レイアウト

        # 画像切り替えボタン
        self.next_button = QtWidgets.QPushButton("Next")
        self.prev_button = QtWidgets.QPushButton("Previous")
        self.next_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        self.prev_button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)

        # ラベル選択ボタン
        self.label_buttons_layout = QtWidgets.QVBoxLayout()  # 垂直レイアウト
        self.label_buttons = []  # ラベルボタンを格納するリスト
        for i in range(1, 10):  # 9つのラベルボタンを作成
            button = QtWidgets.QPushButton(f"Label {i}")
            button.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
            self.label_buttons.append(button)
            self.label_buttons_layout.addWidget(button)
            button.clicked.connect(lambda checked, label=i: self.select_label(label))

        # レイアウトにウィジェットを追加
        self.left_layout.addWidget(self.prev_button)
        self.label_layout.addLayout(self.label_buttons_layout)  # ラベルボタンのレイアウトを追加
        self.right_layout.addWidget(self.next_button)

        # メインレイアウトに画像表示エリアとサイドレイアウトを追加
        self.main_layout.addLayout(self.left_layout)  # 操作ボタンを左側に配置
        self.main_layout.addWidget(self.scroll_area_original)
        self.main_layout.addWidget(self.scroll_area_processed)
        self.main_layout.addLayout(self.label_layout)  # ラベルボタンを右側に配置
        self.main_layout.addLayout(self.right_layout)  # 操作ボタンを右側に配置

        # ボタンのシグナルをスロットに接続
        self.next_button.clicked.connect(self.next_image)
        self.prev_button.clicked.connect(self.prev_image)

        
        # 画像リスト
        self.image_list = []
        self.current_image_index = 0

        # ディレクトリ選択ダイアログを表示
        self.select_directory()

        # original_image_labelウィジェットにマウスイベントを追加
        self.original_image_label.mousePressEvent = self.on_original_image_mouse_press

        # processed_image_labelにマウスイベントを追加
        self.processed_image_label.mousePressEvent = self.on_processed_image_mouse_press
        self.processed_image_label.mouseMoveEvent = self.on_processed_image_mouse_move

    def next_image(self):
        # 次の画像に切り替える処理
        if self.image_list and self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.display_images()
            #self.magic_wand.update_update_color_range(self.magic_wand.)
            self.magic_wand.apply_color_ranges()
            self.update_processed_image()

    def prev_image(self):
        # 前の画像に切り替える処理
        if self.image_list and self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_images()

    def select_label(self, label):
        # ラベル選択時の処理
        print(f"Selected Label: {label}")

    def select_directory(self):
        # ディレクトリ選択ダイアログを表示
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Image Directory")
        if directory:
            # ディレクトリから画像ファイルのリストを取得
            self.image_list = [os.path.join(directory, f) for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            self.image_list.sort()  # ファイル名でソート
            self.display_images()

    def qpixmap_to_cvimg(self, qpixmap):
        # QPixmapをQImageに変換
        qimage = qpixmap.toImage()
        # QImageをNumPy配列に変換
        qimage = qimage.convertToFormat(QImage.Format_RGB32)
        width = qimage.width()
        height = qimage.height()
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)
        img_array = np.array(ptr).reshape(height, width, 4)  # 4チャンネルのRGBA
        # OpenCVでは3チャンネルのBGR形式を使用するため、変換
        cv_img = cv2.cvtColor(img_array, cv2.COLOR_RGBA2BGR)
        return cv_img

    def cvimg_to_qpixmap(self, cv_img):
        # OpenCVの画像をQImageに変換
        height, width, channel = cv_img.shape
        bytes_per_line = 3 * width
        qimage = QImage(cv_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
        # QImageをQPixmapに変換
        qpixmap = QPixmap.fromImage(qimage)
        return qpixmap

    def widget_to_image_coordinates(self, widget_x, widget_y, image_width, image_height):
        widget_width = self.original_image_label.width()
        widget_height = self.original_image_label.height()

        # 実際の表示サイズを計算
        scale = min(widget_width / image_width, widget_height / image_height)
        display_width = image_width * scale
        display_height = image_height * scale

        # ウィジェット内での画像の位置を計算
        x_offset = (widget_width - display_width) / 2
        y_offset = (widget_height - display_height) / 2

        # ウィジェットの座標を画像の座標に変換
        image_x = round((widget_x - x_offset) / scale)
        image_y = round((widget_y - y_offset) / scale)

        return image_x, image_y

    def on_original_image_mouse_press(self, event):
        # マウスクリック位置を取得
        widget_x = event.pos().x()
        widget_y = event.pos().y()

        # 画像のサイズを取得
        image_width = self.cv_img.shape[1]
        image_height = self.cv_img.shape[0]
    
        # 座標を変換
        image_x, image_y = self.widget_to_image_coordinates(widget_x, widget_y, image_width, image_height)  
        
        if event.button() == Qt.LeftButton:
             # MagicWandの処理を実行
             if self.magic_wand:
                 self.magic_wand.run(image_x, image_y)
                 # 処理後の画像を表示
                 self.update_processed_image()
        elif event.button() == Qt.RightButton:
              if self.magic_wand:
                 self.magic_wand.remove_color((image_x, image_y))
                 self.update_processed_image()

    def on_processed_image_mouse_press(self, event):
        # マウスクリック位置を取得
        widget_x = event.pos().x()
        widget_y = event.pos().y()

        # 画像のサイズを取得
        image_width = self.cv_img.shape[1]
        image_height = self.cv_img.shape[0]
    
        # 座標を変換
        image_x, image_y = self.widget_to_image_coordinates(widget_x, widget_y, image_width, image_height)  
        # セグメントの削除処理を実行
        self.magic_wand.segmented = remove_segment_at_point(self.magic_wand.segmented, (image_x, image_y))
        # 画像を更新
        self.update_processed_image()

    def on_processed_image_mouse_move(self, event):
        # マウスクリック位置を取得
        widget_x = event.pos().x()
        widget_y = event.pos().y()

        # 画像のサイズを取得
        image_width = self.cv_img.shape[1]
        image_height = self.cv_img.shape[0]
    
        # 座標を変換
        image_x, image_y = self.widget_to_image_coordinates(widget_x, widget_y, image_width, image_height)  
        # セグメントの削除処理を実行
        self.magic_wand.segmented = remove_segment_at_point(self.magic_wand.segmented, (image_x, image_y))
        # 画像を更新
        self.update_processed_image()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_U:
            self.magic_wand.undo_last_change()
            self.update_processed_image()

    def update_processed_image(self):
        # 処理後の画像をQPixmapに変換して表示
        result_cv_img = self.magic_wand.segmented
        result_qpixmap = self.cvimg_to_qpixmap(result_cv_img)
        self.processed_image_label.setPixmap(result_qpixmap.scaled(self.original_image_label.size(), QtCore.Qt.KeepAspectRatio))

    def display_images(self):
        # 最初の画像を表示
        if self.image_list:
            original_image = QtGui.QPixmap(self.image_list[self.current_image_index])
            self.original_image_label.setPixmap(original_image.scaled(self.original_image_label.size(), QtCore.Qt.KeepAspectRatio))

            # 右側に処理後の画像を表示
            self.cv_img = self.qpixmap_to_cvimg(original_image)
            self.magic_wand.preparation(self.cv_img)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWin = SegmentationAnnotator()
    mainWin.show()
    sys.exit(app.exec_())

