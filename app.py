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

if __name__ == '__main__':
    app = TBApp(sys.argv)
    sys.exit(app.exec())
from PySide6.QtCore import Qt, QSettings, Signal, Slot, QSize, QTimer, QEvent, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QCheckBox,
    QTabWidget, QFrame, QApplication
)
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from timer import TBTimer

class GlobalEventFilter(QObject):
    """全局事件过滤器，用于处理窗口外点击"""
    def __init__(self, popover):
        super().__init__()
        self.popover = popover
        self.mouse_pressed = False
    
    def eventFilter(self, obj, event):
        # 如果是鼠标按下事件，并且不是在弹出窗口内
        if event.type() == QEvent.MouseButtonPress:
            self.mouse_pressed = True
            if self.popover.isVisible() and not self.popover.geometry().contains(event.globalPos()):
                print("窗口外点击，关闭弹出窗口")
                QTimer.singleShot(10, self.popover.closePopover)
                return True
        # 如果是鼠标释放事件，且鼠标曾经被按下
        elif event.type() == QEvent.MouseButtonRelease and self.mouse_pressed:
            self.mouse_pressed = False
            if self.popover.isVisible() and not self.popover.geometry().contains(event.globalPos()):
                print("窗口外点击释放，关闭弹出窗口")
                QTimer.singleShot(10, self.popover.closePopover)
        return super().eventFilter(obj, event)

class TBPopoverView(QWidget):
    """主弹出窗口视图"""
    def __init__(self):
        super().__init__()
        
        # 设置无边框窗口并确保能接收焦点事件
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)  # 确保窗口显示时获取焦点
        self.setFocusPolicy(Qt.StrongFocus)  # 确保窗口可以获取强焦点
        
        # 计时器
        self.timer = TBTimer()
        
        # 初始化UI
        self.initUI()
        
        # 连接信号
        self.timer.timeLeftStringChanged.connect(self.updateTimeLeft)
        
        # 添加全局快捷键
        self.shortcut = QShortcut(QKeySequence("Ctrl+Alt+T"), self)
        self.shortcut.activated.connect(self.timer.startStop)
        
        # 添加全局事件过滤器来处理窗口外点击
        self.event_filter = GlobalEventFilter(self)
        QApplication.instance().installEventFilter(self.event_filter)
    
    def initUI(self):
        """初始化UI组件"""
        # 设置窗口大小
        self.resize(240, 276)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # 开始/停止按钮
        self.startStopButton = QPushButton(self.tr("Start"))
        self.startStopButton.setFixedHeight(40)
        self.startStopButton.clicked.connect(self.onStartStopClicked)
        layout.addWidget(self.startStopButton)
        
        # 选项卡
        self.tabWidget = QTabWidget()
        
        # 间隔选项卡
        self.intervalsTab = self.createIntervalsTab()
        self.tabWidget.addTab(self.intervalsTab, self.tr("Intervals"))
        
        # 设置选项卡
        self.settingsTab = self.createSettingsTab()
        self.tabWidget.addTab(self.settingsTab, self.tr("Settings"))
        
        # 声音选项卡
        self.soundsTab = self.createSoundsTab()
        self.tabWidget.addTab(self.soundsTab, self.tr("Sounds"))
        
        layout.addWidget(self.tabWidget)
        
        # 关于和退出按钮
        aboutButton = QPushButton(self.tr("About"))
        aboutButton.clicked.connect(self.showAbout)
        layout.addWidget(aboutButton)
        
        quitButton = QPushButton(self.tr("Quit"))
        quitButton.clicked.connect(self.quit)
        layout.addWidget(quitButton)
        
        self.setLayout(layout)
    
    def createIntervalsTab(self):
        """创建间隔设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 工作时间
        workLayout = QHBoxLayout()
        workLabel = QLabel(self.tr("Work interval:"))
        workLayout.addWidget(workLabel)
        
        self.workSpinBox = QSpinBox()
        self.workSpinBox.setRange(1, 60)
        self.workSpinBox.setValue(self.timer.workIntervalLength)
        self.workSpinBox.setSuffix(f" {self.tr('min')}")
        self.workSpinBox.valueChanged.connect(self.onWorkIntervalChanged)
        workLayout.addWidget(self.workSpinBox)
        
        layout.addLayout(workLayout)
        
        # 短休息时间
        shortRestLayout = QHBoxLayout()
        shortRestLabel = QLabel(self.tr("Short rest interval:"))
        shortRestLayout.addWidget(shortRestLabel)
        
        self.shortRestSpinBox = QSpinBox()
        self.shortRestSpinBox.setRange(1, 60)
        self.shortRestSpinBox.setValue(self.timer.shortRestIntervalLength)
        self.shortRestSpinBox.setSuffix(f" {self.tr('min')}")
        self.shortRestSpinBox.valueChanged.connect(self.onShortRestIntervalChanged)
        shortRestLayout.addWidget(self.shortRestSpinBox)
        
        layout.addLayout(shortRestLayout)
        
        # 长休息时间
        longRestLayout = QHBoxLayout()
        longRestLabel = QLabel(self.tr("Long rest interval:"))
        longRestLayout.addWidget(longRestLabel)
        
        self.longRestSpinBox = QSpinBox()
        self.longRestSpinBox.setRange(1, 60)
        self.longRestSpinBox.setValue(self.timer.longRestIntervalLength)
        self.longRestSpinBox.setSuffix(f" {self.tr('min')}")
        self.longRestSpinBox.setToolTip(self.tr("Duration of the lengthy break, taken after finishing work interval set"))
        self.longRestSpinBox.valueChanged.connect(self.onLongRestIntervalChanged)
        longRestLayout.addWidget(self.longRestSpinBox)
        
        layout.addLayout(longRestLayout)
        
        # 工作间隔组数
        workIntervalsLayout = QHBoxLayout()
        workIntervalsLabel = QLabel(self.tr("Work intervals in a set:"))
        workIntervalsLayout.addWidget(workIntervalsLabel)
        
        self.workIntervalsSpinBox = QSpinBox()
        self.workIntervalsSpinBox.setRange(1, 10)
        self.workIntervalsSpinBox.setValue(self.timer.workIntervalsInSet)
        self.workIntervalsSpinBox.setToolTip(self.tr("Number of working intervals in the set, after which a lengthy break taken"))
        self.workIntervalsSpinBox.valueChanged.connect(self.onWorkIntervalsInSetChanged)
        workIntervalsLayout.addWidget(self.workIntervalsSpinBox)
        
        layout.addLayout(workIntervalsLayout)
        
        layout.addStretch(1)
        return tab
    
    def createSettingsTab(self):
        """创建设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 快捷键设置
        shortcutLabel = QLabel(self.tr("Shortcut: Ctrl+Alt+T"))
        layout.addWidget(shortcutLabel)
        
        # 休息后停止
        self.stopAfterBreakCheck = QCheckBox(self.tr("Stop after break"))
        self.stopAfterBreakCheck.setChecked(self.timer.stopAfterBreak)
        self.stopAfterBreakCheck.toggled.connect(self.onStopAfterBreakChanged)
        layout.addWidget(self.stopAfterBreakCheck)
        
        # 在菜单栏显示计时器
        self.showTimerInMenuBarCheck = QCheckBox(self.tr("Show timer in menu bar"))
        self.showTimerInMenuBarCheck.setChecked(self.timer.showTimerInMenuBar)
        self.showTimerInMenuBarCheck.toggled.connect(self.onShowTimerInMenuBarChanged)
        layout.addWidget(self.showTimerInMenuBarCheck)
        
        # 开机启动
        self.launchAtLoginCheck = QCheckBox(self.tr("Launch at login"))
        self.launchAtLoginCheck.setChecked(QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                                                    QSettings.NativeFormat).contains("TomatoBar"))
        self.launchAtLoginCheck.toggled.connect(self.onLaunchAtLoginChanged)
        layout.addWidget(self.launchAtLoginCheck)
        
        layout.addStretch(1)
        return tab
    
    def createSoundsTab(self):
        """创建声音设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 发条声滑块
        windupLayout = QHBoxLayout()
        windupLabel = QLabel(self.tr("Windup"))
        windupLayout.addWidget(windupLabel)
        
        self.windupSlider = QSlider(Qt.Horizontal)
        self.windupSlider.setRange(0, 200)
        self.windupSlider.setValue(int(self.timer.player.windupVolume * 100))
        self.windupSlider.valueChanged.connect(self.onWindupVolumeChanged)
        windupLayout.addWidget(self.windupSlider)
        
        layout.addLayout(windupLayout)
        
        # 叮声滑块
        dingLayout = QHBoxLayout()
        dingLabel = QLabel(self.tr("Ding"))
        dingLayout.addWidget(dingLabel)
        
        self.dingSlider = QSlider(Qt.Horizontal)
        self.dingSlider.setRange(0, 200)
        self.dingSlider.setValue(int(self.timer.player.dingVolume * 100))
        self.dingSlider.valueChanged.connect(self.onDingVolumeChanged)
        dingLayout.addWidget(self.dingSlider)
        
        layout.addLayout(dingLayout)
        
        # 滴答声滑块
        tickingLayout = QHBoxLayout()
        tickingLabel = QLabel(self.tr("Ticking"))
        tickingLayout.addWidget(tickingLabel)
        
        self.tickingSlider = QSlider(Qt.Horizontal)
        self.tickingSlider.setRange(0, 200)
        self.tickingSlider.setValue(int(self.timer.player.tickingVolume * 100))
        self.tickingSlider.valueChanged.connect(self.onTickingVolumeChanged)
        tickingLayout.addWidget(self.tickingSlider)
        
        layout.addLayout(tickingLayout)
        
        layout.addStretch(1)
        return tab
    
    def onStartStopClicked(self):
        """开始/停止按钮点击处理"""
        self.timer.startStop()
        # 避免直接导入 TBStatusItem，使用 timer 中的方法
        status_item = self.timer.getStatusItem()
        if status_item:
            status_item.closePopover()
    
    def updateTimeLeft(self, timeLeft):
        """更新剩余时间显示"""
        if self.timer.timer:
            self.startStopButton.setText(self.tr("Stop") if self.startStopButton.underMouse() else timeLeft)
        else:
            self.startStopButton.setText(self.tr("Start"))
    
    def onWorkIntervalChanged(self, value):
        """工作时间变更处理"""
        self.timer.workIntervalLength = value
        self.timer.settings.setValue("workIntervalLength", value)
    
    def onShortRestIntervalChanged(self, value):
        """短休息时间变更处理"""
        self.timer.shortRestIntervalLength = value
        self.timer.settings.setValue("shortRestIntervalLength", value)
    
    def onLongRestIntervalChanged(self, value):
        """长休息时间变更处理"""
        self.timer.longRestIntervalLength = value
        self.timer.settings.setValue("longRestIntervalLength", value)
    
    def onWorkIntervalsInSetChanged(self, value):
        """工作间隔组数变更处理"""
        self.timer.workIntervalsInSet = value
        self.timer.settings.setValue("workIntervalsInSet", value)
    
    def onStopAfterBreakChanged(self, checked):
        """休息后停止设置变更处理"""
        self.timer.stopAfterBreak = checked
        self.timer.settings.setValue("stopAfterBreak", checked)
    
    def onShowTimerInMenuBarChanged(self, checked):
        """菜单栏显示计时器设置变更处理"""
        self.timer.showTimerInMenuBar = checked
        self.timer.settings.setValue("showTimerInMenuBar", checked)
        self.timer.updateTimeLeft()
    
    def onLaunchAtLoginChanged(self, checked):
        """开机启动设置变更处理"""
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                           QSettings.NativeFormat)
        
        if checked:
            import sys
            settings.setValue("TomatoBar", sys.executable)
        else:
            settings.remove("TomatoBar")
    
    def onWindupVolumeChanged(self, value):
        """发条声音量变更处理"""
        volume = value / 100.0
        self.timer.player.setWindupVolume(volume)
    
    def onDingVolumeChanged(self, value):
        """叮声音量变更处理"""
        volume = value / 100.0
        self.timer.player.setDingVolume(volume)
    
    def onTickingVolumeChanged(self, value):
        """滴答声音量变更处理"""
        volume = value / 100.0
        self.timer.player.setTickingVolume(volume)
    
    def showAbout(self):
        """显示关于对话框"""
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self, 
            "TomatoBar",
            "TomatoBar for Windows\n\n"
            "A Pomodoro timer for the Windows system tray.\n\n"
            "Based on the macOS TomatoBar by Ilya Voronin.\n"
            "https://github.com/ivoronin/TomatoBar"
        )
    
    def quit(self):
        """退出应用"""
        from PySide6.QtWidgets import QApplication
        QApplication.quit()
    
    def enterEvent(self, event):
        """鼠标进入窗口处理"""
        if self.timer.timer:
            self.startStopButton.setText(self.tr("Stop"))
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """鼠标离开窗口处理"""
        if self.timer.timer:
            self.startStopButton.setText(self.timer.timeLeftString)
        super().leaveEvent(event)
    
    def sizeHint(self):
        """提供推荐大小"""
        return QSize(240, 276)        

    def focusOutEvent(self, event):
        """当窗口失去焦点时尝试关闭弹窗"""
        super().focusOutEvent(event)
        print("弹窗失去焦点")
        
        # 使用 QTimer.singleShot 延迟关闭，避免焦点问题
        QTimer.singleShot(100, self.closePopoverSafely)
    
    def closePopoverSafely(self):
        """安全地关闭弹出窗口，考虑各种状态"""
        print("尝试安全关闭弹窗")
        
        # 如果窗口不再可见，则不需要操作
        if not self.isVisible():
            print("弹窗已经不可见，不需要关闭")
            return
        
        # 直接使用应用程序单例获取状态项
        app = QApplication.instance()
        if hasattr(app, 'status_item'):
            app.status_item.closePopover()
            print("已通过应用单例关闭弹窗")
        else:
            # 备用方法，通过 timer 获取
            try:
                status_item = self.timer.getStatusItem()
                if status_item:
                    status_item.closePopover()
                    print("已通过 timer 关闭弹窗")
                else:
                    print("无法获取状态项，尝试直接隐藏")
                    self.hide()
            except Exception as e:
                print(f"关闭弹窗时出错: {e}")
                # 最后手段，直接隐藏自己
                self.hide()
    
    def forceClosePopover(self):
        """强制关闭弹出窗口"""
        print("强制关闭弹窗")
        self.closePopoverSafely()  # 使用安全方法
    
    def closePopover(self):
        """关闭弹出窗口"""
        self.closePopoverSafely()  # 使用安全方法
    
    def showEvent(self, event):
        """窗口显示时强制捕获焦点"""
        super().showEvent(event)
        # 更强制地激活窗口并获取焦点
        self.activateWindow()
        self.setFocus(Qt.ActiveWindowFocusReason)
        QTimer.singleShot(100, lambda: self.activateWindow())
