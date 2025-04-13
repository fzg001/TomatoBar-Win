from enum import Enum, auto
from PySide6.QtCore import QObject
from PySide6.QtWidgets import QSystemTrayIcon
import uuid

class TBNotification:
    """通知相关的枚举和常量定义"""
    class Category(Enum):
        REST_STARTED = auto()
        REST_FINISHED = auto()
    
    class Action(Enum):
        SKIP_REST = auto()

class TBNotificationCenter(QObject):
    def __init__(self):
        super().__init__()
        self.handler = None
        
        # 检查系统是否支持通知
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("警告: 系统不支持托盘通知")
    
    def setActionHandler(self, handler):
        """设置通知动作处理器"""
        self.handler = handler
    
    def send(self, title, body, category=None):
        """发送通知"""
        # 使用 QSystemTrayIcon 显示通知，避免循环导入
        try:
            from app import TBStatusItem
            tray = TBStatusItem.shared.tray_icon if TBStatusItem.shared else None
            
            if tray:
                # 显示通知
                tray.showMessage(
                    title,
                    body,
                    QSystemTrayIcon.MessageIcon.Information,
                    5000  # 显示5秒
                )
        except Exception as e:
            print(f"发送通知失败: {e}")
