import sys
import os
import json
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTranslator, QLocale, QObject, QTimer

from timer import TBTimer
from view import TBPopoverView
from state import TBStateMachine, TBStateMachineStates
from log import logger, TBLogEventAppStart


class TBApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.translator = QTranslator()



        # 加载本地化资源
        locale = QLocale.system().name()
        localization_dir = "localization"
        lang_file = "en.json"  # 默认英文
        if locale.startswith('zh_'):
            lang_file = "zh-Hans.json"

        # 尝试加载 .qm 文件（如果存在），否则加载 .json
        qm_path = os.path.join(localization_dir, lang_file.replace('.json', '.qm'))
        json_path = os.path.join(localization_dir, lang_file)

        if os.path.exists(qm_path):
            if self.translator.load(qm_path):
                self.installTranslator(self.translator)
        elif os.path.exists(json_path):
            pass  # 如果需要运行时加载 JSON，需要自定义翻译逻辑或使用其他库

        # 初始化状态栏项
        self.status_item = TBStatusItem()

        # 记录应用启动
        logger.append(event=TBLogEventAppStart())

class TBStatusItem(QObject):
    shared = None

    def __init__(self):
        super().__init__()
        TBStatusItem.shared = self

        self.tray_icon = QSystemTrayIcon()

        self.popover = TBPopoverView()
        self.popover.hide()

        self.setIcon("idle")
        self.tray_icon.activated.connect(self.togglePopover)
        self.tray_icon.show()

    def setIcon(self, name):
        """设置图标，name可以是idle, work, shortrest, longrest"""
        icon_name = name.lower()
        icon_path = f"Icons/{icon_name}.png"

        if os.path.exists(icon_path):
            try:
                self.tray_icon.setIcon(QIcon(icon_path))
                return
            except Exception as e:
                print(f"设置图标失败: {e}")
        else:
            alt_paths = [
                f"icons/{icon_name}.png",
                f"Icons/{name}.png",
            ]

            for path in alt_paths:
                if os.path.exists(path):
                    try:
                        self.tray_icon.setIcon(QIcon(path))
                        return
                    except Exception as e:
                        print(f"设置备选图标失败: {e}")

            print(f"警告: 无法找到任何可用图标 for '{name}'")

    def setTitle(self, title):
        """设置托盘图标的提示文本"""
        if title:
            self.tray_icon.setToolTip(f"TomatoBar - {title}")
        else:
            self.tray_icon.setToolTip("TomatoBar")

    def showPopover(self):

        if self.popover.isVisible():
            # print("警告: 弹出窗口已经可见，无法再次显示")
            return
        
        else:
            """显示弹出窗口"""
            pos = self.getPopoverPosition()
            self.popover.move(pos)
            self.popover.show()
            # print(f"弹出窗口位置: {pos.x()}, {pos.y()}")
            self.popover.raise_()  # 确保窗口在最前


    def closePopover(self):
        """关闭弹出窗口"""
        if self.popover.isVisible():
             self.popover.hide()


# 目前这个地方有一点小问题，只要使用QT.popup  就不可避免，暂时不处理
    def togglePopover(self, reason):
        """切换弹出窗口显示状态 (Deferred Execution)"""

        if reason == QSystemTrayIcon.ActivationReason.Trigger:
                QTimer.singleShot(50, self.showPopover)
                # print("调试: 弹出窗口显示")

    def getPopoverPosition(self):
        """计算弹出窗口位置"""
        geometry = self.tray_icon.geometry()
        screen = QApplication.primaryScreen().availableGeometry()

        popover_height = self.popover.sizeHint().height() # 使用 sizeHint
        popover_width = self.popover.sizeHint().width() # 

        # print(f"纯调试: popover sizeHint = {self.popover.sizeHint()}, tray geometry = {geometry}")
        # 简化逻辑，只基于托盘图标位置计算
        if not geometry.isEmpty() and geometry.width() > 0:
            # 正常计算 - 居中对齐托盘图标
            x = geometry.x() + geometry.width() // 2 - popover_width // 2
            y = geometry.y() - popover_height - 70

            # 保留屏幕边界检查
            if x < screen.left():
                x = screen.left() + 10
            elif x + popover_width > screen.right():
                x = screen.right() - popover_width - 10

            if y < screen.top():
                y = screen.top() + 10

            return QtCore.QPoint(x, y)
        else:
            print("警告: 托盘图标几何信息无效，使用默认位置")
            # 可能需要返回一个默认 QPoint
            return QtCore.QPoint(screen.center().x() - popover_width // 2, screen.center().y() - popover_height // 2)


