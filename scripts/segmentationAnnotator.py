import os
from PyQt5 import QtWidgets, QtGui, QtCore

class SegmentationAnnotator(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Segmentation Annotator")
        self.showMaximized()  # GUIを全画面で表示

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

    def next_image(self):
        # 次の画像に切り替える処理
        if self.image_list and self.current_image_index < len(self.image_list) - 1:
            self.current_image_index += 1
            self.display_images()

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

    def display_images(self):
        # 最初の画像を表示
        if self.image_list:
            original_image = QtGui.QPixmap(self.image_list[self.current_image_index])
            self.original_image_label.setPixmap(original_image.scaled(self.original_image_label.size(), QtCore.Qt.KeepAspectRatio))

            # 右側に黒い画像を表示
            black_image = QtGui.QPixmap(self.original_image_label.size())
            black_image.fill(QtCore.Qt.black)
            self.processed_image_label.setPixmap(black_image)

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    mainWin = SegmentationAnnotator()
    mainWin.show()
    sys.exit(app.exec_())

