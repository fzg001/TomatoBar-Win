import sys
import os
import json
from PySide6 import QtCore
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QWidget
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTranslator, QLocale, QObject

from timer import TBTimer
from view import TBPopoverView
from state import TBStateMachine, TBStateMachineStates
from log import logger, TBLogEventAppStart
from styles import TBStyles  # 导入样式类

class TBApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setQuitOnLastWindowClosed(False)
        self.translator = QTranslator()

        # 应用全局样式
        TBStyles.applyApplicationStyle()

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
        """显示弹出窗口"""
        pos = self.getPopoverPosition()
        self.popover.move(pos)
        self.popover.show()
        self.popover.raise_()  # 确保窗口在最前

    def closePopover(self):
        """关闭弹出窗口"""
        if self.popover.isVisible():
            self.popover.hide()

    def togglePopover(self, reason):
        """切换弹出窗口显示状态"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.popover.isVisible():
                self.closePopover()
            else:
                self.showPopover()

    def getPopoverPosition(self):
        """计算弹出窗口位置"""
        geometry = self.tray_icon.geometry()
        screen = QApplication.primaryScreen().availableGeometry()
        
        # 简化逻辑，只基于托盘图标位置计算
        if not geometry.isEmpty() and geometry.width() > 0:
            # 正常计算 - 居中对齐托盘图标
            x = geometry.x() + geometry.width() // 2 - self.popover.width() // 2
            y = geometry.y() - self.popover.height() - 5
            
            # 保留屏幕边界检查
            if x < screen.left():
                x = screen.left() + 10
            elif x + self.popover.width() > screen.right():
                x = screen.right() - self.popover.width() - 10
                
            if y < screen.top():
                y = screen.top() + 10
                
            return QtCore.QPoint(x, y)
        else:
            # 如果托盘图标信息无效，使用屏幕右下角位置
            return QtCore.QPoint(
                screen.width() - self.popover.width() - 20, 
                screen.height() - self.popover.height() - 40
            )



