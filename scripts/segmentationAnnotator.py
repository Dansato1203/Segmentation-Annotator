import os
import numpy as np
import cv2

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap

from magicWand import MagicWand

from segmentation_utils import remove_segment_at_point
from segmentation_utils import save_processed_image

class SegmentationAnnotator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Segmentation Annotator")
        self.showMaximized()  # GUIを全画面で表示

        self.magic_wand = MagicWand()

        self.radius = 5
        self.min_radius = 1
        self.max_radius = 100

        self.mouse_mode = "preview"
        self.original_preview_image = None
        self.processed_preview_image = None

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

        self.original_image_label.setMouseTracking(True)
        self.processed_image_label.setMouseTracking(True)

        self.original_image_label.mouseMoveEvent = self.on_original_image_mouse_move
        self.processed_image_label.mouseMoveEvent = self.on_processed_image_mouse_move

    def next_image(self):
        save_processed_image(self.image_list[self.current_image_index], self.magic_wand.segmented)
        # 次の画像に切り替える処理
        if self.image_list and self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.display_images()
            self.magic_wand.apply_color_ranges()
            self.update_processed_image()

    def prev_image(self):
        save_processed_image(self.image_list[self.current_image_index], self.magic_wand.segmented)
        # 前の画像に切り替える処理
        if self.image_list and self.current_image_index > 0:
            self.current_image_index -= 1
            self.display_images()
            self.magic_wand.apply_color_ranges()
            self.update_processed_image()

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
                 self.magic_wand.run(image_x, image_y, radius=self.radius)
                 # 処理後の画像を表示
                 self.update_processed_image()
        elif event.button() == Qt.RightButton:
              if self.magic_wand:
                 self.magic_wand.remove_color((image_x, image_y), radius=self.radius)
                 self.update_processed_image()

    def on_processed_image_mouse_press(self, event):
        if self.mouse_mode == "delete":
            self.delete_point(event)

    def on_original_image_mouse_move(self, event):
        self.update_preview(event, self.original_image_label)
        
    def on_processed_image_mouse_move(self, event):
        if self.mouse_mode == "delete":
            # 削除モードの処理
            self.delete_point(event)
        elif self.mouse_mode == "preview":
            # プレビューモードの処理
            self.update_preview(event, self.processed_image_label)

    def delete_point(self, event):
        # マウスクリック位置を取得
        widget_x = event.pos().x()
        widget_y = event.pos().y()

        # 画像のサイズを取得
        image_width = self.cv_img.shape[1]
        image_height = self.cv_img.shape[0]
    
        # 座標を変換
        image_x, image_y = self.widget_to_image_coordinates(widget_x, widget_y, image_width, image_height)  
        # セグメントの削除処理を実行
        self.magic_wand.segmented = remove_segment_at_point(self.magic_wand.segmented, (image_x, image_y), radius=self.radius)
        # 画像を更新
        self.update_processed_image()

    def update_preview(self, event, label_widget):
        # マウスクリック位置を取得
        widget_x = event.pos().x()
        widget_y = event.pos().y()

        # 画像のサイズを取得
        image_width = self.cv_img.shape[1]
        image_height = self.cv_img.shape[0]
        
        # 座標を変換
        image_x, image_y = self.widget_to_image_coordinates(widget_x, widget_y, image_width, image_height)  

        if label_widget == self.original_image_label:
            self.original_preview_image = self.qpixmap_to_cvimg(self.original_image.copy())
            cv2.circle(self.original_preview_image, (image_x, image_y), self.radius, (255, 0, 0), 1)
            self.update_displayed_image(self.original_preview_image, self.original_image_label)
        elif label_widget == self.processed_image_label:
            self.processed_preview_image = self.magic_wand.segmented.copy()
            cv2.circle(self.processed_preview_image, (image_x, image_y), self.radius, (255, 0, 0), 1)
            self.update_displayed_image(self.processed_preview_image, self.processed_image_label)

    def update_displayed_image(self, image, label_widget):
        # 画像をQPixmapに変換して表示
        qpixmap = self.cvimg_to_qpixmap(image)
        label_widget.setPixmap(qpixmap.scaled(label_widget.size(), QtCore.Qt.KeepAspectRatio))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_U:
            self.magic_wand.undo_last_change()
            self.update_processed_image()
        elif event.key() == Qt.Key_D:
            if self.mouse_mode != "delete":
                self.processed_image_label.setMouseTracking(False) 
                self.mouse_mode = "delete"  # 削除モードに切り替え
            else:
                self.processed_image_label.setMouseTracking(True)
                self.mouse_mode = "preview"  # プレビューモードに切り替え
        elif event.key() == Qt.Key_P or event.key() == Qt.Key_D:
            self.processed_image_label.setMouseTracking(True) 
            self.mouse_mode = "preview"  # プレビューモードに切り替え

    # マウスホイールイベントの処理
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.radius = min(self.radius + 1, self.max_radius)
        elif delta < 0:
            self.radius = max(self.radius - 1, self.min_radius)

    def update_processed_image(self):
        # 処理後の画像をQPixmapに変換して表示
        result_cv_img = self.magic_wand.segmented
        result_qpixmap = self.cvimg_to_qpixmap(result_cv_img)
        self.processed_image_label.setPixmap(result_qpixmap.scaled(self.original_image_label.size(), QtCore.Qt.KeepAspectRatio))

    def display_images(self):
        # 最初の画像を表示
        if self.image_list:
            self.original_image = QtGui.QPixmap(self.image_list[self.current_image_index])
            self.original_image_label.setPixmap(self.original_image.scaled(self.original_image_label.size(), QtCore.Qt.KeepAspectRatio))

            # labelsディレクトリ内のファイルをチェック
            #label_dir = os.path.join(os.path.dirname(self.image_list[self.current_image_index]), 'labels')
            #base_name = os.path.splitext(os.path.basename(self.image_list[self.current_image_index]))[0]
            #label_path = os.path.join(label_dir, f"{base_name}_label.png")
            #if os.path.exists(label_path):
                # ラベル画像が存在する場合はそれを読み込む
                # 右側に処理後の画像を表示
            #    self.cv_img = cv2.imread(label_path)
            #    self.magic_wand.preparation(self.cv_img, True)
            #else:
                # ラベル画像が存在しない場合は通常の画像を読み込む
                # 右側に処理後の画像を表示
            self.cv_img = self.qpixmap_to_cvimg(self.original_image)
            self.magic_wand.preparation(self.cv_img, False)
            self.update_displayed_image(self.cv_img, self.processed_image_label)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWin = SegmentationAnnotator()
    mainWin.show()
    sys.exit(app.exec_())

