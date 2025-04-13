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
        """设置图标，name可以是idle, work, shortrest, longrest"""
        # 确保图标名称为小写，与文件名完全匹配
        icon_name = name.lower()
        
        # 直接指定图标路径，确保正确找到Icons目录中的文件
        icon_path = f"Icons/{icon_name}.png"
        
        print(f"直接查找图标: {icon_path}")
        
        if os.path.exists(icon_path):
            print(f"✓ 已找到图标: {icon_path}")
            try:
                self.tray_icon.setIcon(QIcon(icon_path))
                print(f"✓ 成功设置图标")
                return
            except Exception as e:
                print(f"设置图标失败: {e}")
        else:
            print(f"✗ 图标不存在: {icon_path}")
            
            # 尝试其他备选路径
            alt_paths = [
                f"icons/{icon_name}.png",
                f"Icons/{name}.png",
                f"Assets/BarIcon{name.title()}.imageset/icon_16x16@2x.png",
            ]
            
            for path in alt_paths:
                if os.path.exists(path):
                    print(f"✓ 找到备选图标: {path}")
                    try:
                        self.tray_icon.setIcon(QIcon(path))
                        print(f"✓ 成功设置备选图标")
                        return
                    except Exception as e:
                        print(f"设置备选图标失败: {e}")
            
            print(f"警告: 无法找到任何可用图标")
    
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



