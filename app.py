import sys
import os
import json
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QWidget
from PySide6.QtGui import QIcon, QAction, QPixmap
from PySide6.QtCore import QObject, Signal, Slot, QTranslator, QLocale

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
        if locale.startswith('zh_'):
            self.translator.load(os.path.join("localization", "zh-Hans.json"))
        else:
            self.translator.load(os.path.join("localization", "en.json"))
        self.installTranslator(self.translator)
        
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
        self.menu = QMenu()
        
        self.popover = TBPopoverView()
        self.popover.hide()
        
        self.setIcon("idle")
        self.tray_icon.activated.connect(self.togglePopover)
        self.tray_icon.show()
    
    def setIcon(self, name):
        """设置图标，name可以是idle, work, shortRest, longRest"""
        # 扩展可能的路径列表
        icon_paths = [
            f"Assets/BarIcon{name.title()}.imageset/icon_16x16@2x.png",
            f"Assets/BarIcon{name.title()}.imageset/icon_16x16.png",
            f"Assets/icons/{name.lower()}.png",
            f"icons/{name.lower()}.png",
            f"{name.lower()}.png"
        ]
        
        # 调试信息，打印所有尝试的路径
        print(f"尝试为状态 {name} 查找图标，搜索路径:")
        for path in icon_paths:
            exists = os.path.exists(path)
            print(f" - {path} {'[存在]' if exists else '[不存在]'}")
        
        # 查找第一个存在的图标文件
        icon_path = next((path for path in icon_paths if os.path.exists(path)), None)
        
        if icon_path:
            print(f"使用图标: {icon_path}")
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # 如果找不到指定图标，提供更多路径选项并使用默认图标
            default_icons = [
                "Assets/AppIcon.appiconset/icon_32x32.png", 
                "icons/tomato.png", 
                "tomato.png"
            ]
            print(f"找不到状态 {name} 的图标，尝试使用默认图标:")
            for path in default_icons:
                exists = os.path.exists(path)
                print(f" - {path} {'[存在]' if exists else '[不存在]'}")
                
            default_icon = next((path for path in default_icons if os.path.exists(path)), None)
            
            if default_icon:
                print(f"使用默认图标: {default_icon}")
                self.tray_icon.setIcon(QIcon(default_icon))
            else:
                print(f"警告: 找不到图标 {name} 也找不到默认图标")
    
    def setTitle(self, title):
        """设置托盘图标的提示文本"""
        if title:
            self.tray_icon.setToolTip(f"TomatoBar - {title}")
        else:
            self.tray_icon.setToolTip("TomatoBar")
    
    def showPopover(self, reason=None):
        """显示弹出窗口"""
        self.popover.move(self.getPopoverPosition())
        self.popover.show()
        self.popover.raise_()  # 确保窗口在最前
        self.popover.activateWindow()  # 激活窗口获取焦点
        self.popover.setFocus()  # 明确设置焦点
        
        # 调试信息
        print(f"显示弹窗，当前焦点状态: {self.popover.hasFocus()}")
    
    def closePopover(self, sender=None):
        """关闭弹出窗口"""
        print("关闭弹窗")
        # 确保窗口隐藏
        if self.popover.isVisible():
            self.popover.hide()
        else:
            print("弹窗已经隐藏")
    
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
        if not geometry.isEmpty():
            # 根据托盘图标位置计算
            return QtCore.QPoint(geometry.x() + geometry.width() // 2 - self.popover.width() // 2, 
                                geometry.y() - self.popover.height())
        else:
            # 如果获取不到位置，使用屏幕右下角
            desktop = QApplication.primaryScreen().availableGeometry()
            return QtCore.QPoint(desktop.width() - self.popover.width() - 10, 
                                desktop.height() - self.popover.height() - 10)

if __name__ == '__main__':
    app = TBApp(sys.argv)
    sys.exit(app.exec())
