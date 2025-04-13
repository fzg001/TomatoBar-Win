import sys
import os
from PySide6.QtWidgets import QApplication


def main():

        # 导入应用类并启动
    from app import TBApp
    app = TBApp(sys.argv)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
