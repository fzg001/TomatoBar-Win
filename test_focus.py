from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt
import sys

class TestFocusWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        # 尝试不同的窗口标志组合
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        self.setFocusPolicy(Qt.StrongFocus)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("这是一个测试窗口"))
        layout.addWidget(QLabel("点击窗口外部应该会关闭此窗口"))
        
        closeBtn = QPushButton("关闭")
        closeBtn.clicked.connect(self.close)
        layout.addWidget(closeBtn)
        
        self.setLayout(layout)
        self.setStyleSheet("background-color: white; border: 1px solid black; padding: 10px;")
    
    def focusOutEvent(self, event):
        print("窗口失去焦点")
        self.close()
        super().focusOutEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestFocusWidget()
    window.show()
    window.raise_()
    window.activateWindow()
    sys.exit(app.exec())
