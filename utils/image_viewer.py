import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QAction, QFileDialog, QSizePolicy, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QFont
from PyQt5.QtCore import Qt


class BaseImageViewer(QMainWindow):
    """图片浏览器抽象基类"""

    def __init__(self, width, height, title="图片浏览器"):
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.current_image = None

        # 初始化UI
        self.setWindowTitle(title)
        self.create_widgets()
        self.create_layout()
        self.create_menu()

        # 调整窗口大小
        menu_height = self.menuBar().sizeHint().height()
        self.setFixedSize(width, height + menu_height + self.extra_height())

    def extra_height(self):
        """子类可重写此方法添加额外高度（如状态栏）"""
        return 0

    def create_widgets(self):
        """创建界面控件（由子类实现）"""
        pass

    def create_layout(self):
        """创建布局（由子类实现）"""
        pass

    def create_menu(self):
        """创建菜单栏（公共实现）"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")

        open_action = QAction("打开图片", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_image(self):
        """打开图片文件对话框（公共实现）"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择图片", "",
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        if file_path:
            self.load_image(file_path)

    def load_image(self, file_path):
        """加载图片（由子类实现具体逻辑）"""
        pass

    def get_scaled_pixmap(self, image):
        """缩放图片到合适尺寸（公共方法）"""
        pixmap = QPixmap.fromImage(image)
        return pixmap.scaled(
            self.width, self.height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )


class SlidePuzzleImageViewer(BaseImageViewer):
    """模拟滑块验证的图片浏览器"""

    def __init__(self, width=276, height=172):
        super().__init__(width, height, "图片显示器")

        # 添加底部边距
        self.setFixedSize(width, height + self.menuBar().sizeHint().height() + 20)

    def extra_height(self):
        """添加底部边距"""
        return 20

    def create_widgets(self):
        """创建控件"""
        self.image_label = QLabel()
        self.image_label.setFixedSize(self.width, self.height)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0;")

    def create_layout(self):
        """创建布局"""
        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.image_label)

    def load_image(self, file_path):
        """加载图片的具体实现"""
        image = QImage(file_path)
        if not image.isNull():
            scaled_pixmap = self.get_scaled_pixmap(image)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.clear()
            self.image_label.setText("无法加载图片")
            self.image_label.setStyleSheet(
                "background-color: #f0f0f0; color: red; font: bold;"
            )


class NineGridImageViewer(BaseImageViewer):
    """带状态描述的图片浏览器"""

    def __init__(self, width=330, height=330):
        super().__init__(width, height, "图片浏览器 - 330x330")

    def create_widgets(self):
        """创建控件"""
        self.status_label = QLabel("请选择一张图片")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 9))

        self.image_label = QLabel()
        self.image_label.setFixedSize(self.width, self.height)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("""
            background-color: #f0f0f0;
            border: 2px dashed #cccccc;
            border-radius: 5px;
        """)

    def create_layout(self):
        """创建布局"""
        central_widget = QWidget()
        central_widget.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.status_label)
        layout.addWidget(self.image_label)

    def load_image(self, file_path):
        """加载图片的具体实现"""
        filename = file_path.split('/')[-1]
        self.status_label.setText(f"正在加载: {filename}")

        image = QImage(file_path)
        if not image.isNull():
            scaled_pixmap = self.get_scaled_pixmap(image)
            self.image_label.setPixmap(scaled_pixmap)
            self.status_label.setText(f"已加载: {filename}")
        else:
            self.image_label.clear()
            self.status_label.setText("无法加载图片")
            self.image_label.setText("图片加载失败")
            self.image_label.setStyleSheet("""
                background-color: #f0f0f0;
                border: 2px dashed #ff0000;
                color: red;
                font: bold 12px;
            """)


if __name__ == "__main__":
    # 确保高DPI屏幕适配
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    viewer = NineGridImageViewer()
    viewer.show()
    sys.exit(app.exec_())
