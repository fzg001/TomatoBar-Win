import os
import json
from datetime import datetime
from PySide6.QtCore import QObject, QStandardPaths

# 全局日志记录器
logger = None

class TBLogEvent:
    """日志事件基类"""
    def __init__(self, type_name):
        self.type = type_name
        self.timestamp = datetime.now().timestamp()
    
    def to_dict(self):
        return {
            "type": self.type,
            "timestamp": self.timestamp
        }

class TBLogEventAppStart(TBLogEvent):
    """应用启动事件"""
    def __init__(self):
        super().__init__("appstart")

class TBLogEventTransition(TBLogEvent):
    """状态转换事件"""
    def __init__(self, context):
        super().__init__("transition")
        self.event = str(context.event)
        self.fromState = str(context.fromState)
        self.toState = str(context.toState)
    
    def to_dict(self):
        data = super().to_dict()
        data.update({
            "event": self.event,
            "fromState": self.fromState,
            "toState": self.toState
        })
        return data

class TBLogger:
    """日志记录器"""
    def __init__(self):
        # 确定日志文件路径
        cache_dir = QStandardPaths.writableLocation(QStandardPaths.CacheLocation)
        if not cache_dir:
            cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "TomatoBar")
        
        # 确保目录存在
        os.makedirs(cache_dir, exist_ok=True)
        
        self.log_path = os.path.join(cache_dir, "TomatoBar.log")
    
    def append(self, event):
        """添加日志事件"""
        try:
            # 转换事件为JSON
            event_json = json.dumps(event.to_dict(), sort_keys=True)
            
            # 追加到日志文件
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(event_json + "\n")
        except Exception as e:
            print(f"日志记录失败: {e}")

# 初始化全局日志记录器
logger = TBLogger()
