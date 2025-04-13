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
        
        # 添加内部操作状态标志，用于判断是否应该关闭窗口
        self.internal_operation = False
        
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
        # 不再自动关闭窗口
    
    def updateTimeLeft(self, timeLeft):
        """更新剩余时间显示"""
        if self.timer.timer:
            self.startStopButton.setText(self.tr("Stop") if self.startStopButton.underMouse() else timeLeft)
        else:
            self.startStopButton.setText(self.tr("Start"))
    
    def onWorkIntervalChanged(self, value):
        """工作时间变更处理"""
        self.internal_operation = True
        self.timer.workIntervalLength = value
        self.timer.settings.setValue("workIntervalLength", value)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onShortRestIntervalChanged(self, value):
        """短休息时间变更处理"""
        self.internal_operation = True
        self.timer.shortRestIntervalLength = value
        self.timer.settings.setValue("shortRestIntervalLength", value)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onLongRestIntervalChanged(self, value):
        """长休息时间变更处理"""
        self.internal_operation = True
        self.timer.longRestIntervalLength = value
        self.timer.settings.setValue("longRestIntervalLength", value)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onWorkIntervalsInSetChanged(self, value):
        """工作间隔组数变更处理"""
        self.internal_operation = True
        self.timer.workIntervalsInSet = value
        self.timer.settings.setValue("workIntervalsInSet", value)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onStopAfterBreakChanged(self, checked):
        """休息后停止设置变更处理"""
        self.internal_operation = True
        self.timer.stopAfterBreak = checked
        self.timer.settings.setValue("stopAfterBreak", checked)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onShowTimerInMenuBarChanged(self, checked):
        """菜单栏显示计时器设置变更处理"""
        self.internal_operation = True
        self.timer.showTimerInMenuBar = checked
        self.timer.settings.setValue("showTimerInMenuBar", checked)
        self.timer.updateTimeLeft()
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onLaunchAtLoginChanged(self, checked):
        """开机启动设置变更处理"""
        self.internal_operation = True
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                           QSettings.NativeFormat)
        
        if checked:
            import sys
            settings.setValue("TomatoBar", sys.executable)
        else:
            settings.remove("TomatoBar")
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onWindupVolumeChanged(self, value):
        """发条声音量变更处理"""
        self.internal_operation = True
        volume = value / 100.0
        self.timer.player.setWindupVolume(volume)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onDingVolumeChanged(self, value):
        """叮声音量变更处理"""
        self.internal_operation = True
        volume = value / 100.0
        self.timer.player.setDingVolume(volume)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def onTickingVolumeChanged(self, value):
        """滴答声音量变更处理"""
        self.internal_operation = True
        volume = value / 100.0
        self.timer.player.setTickingVolume(volume)
        QTimer.singleShot(500, self.resetInternalOperation)
    
    def resetInternalOperation(self):
        """重置内部操作标志"""
        self.internal_operation = False
    
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
        
        # 如果正在进行内部操作，不关闭窗口
        if self.internal_operation:
            print("内部操作中，不关闭弹窗")
            return
        
        # 检查焦点是否还在窗口内部的某个控件上
        focused_widget = QApplication.focusWidget()
        if focused_widget and self.isAncestorOf(focused_widget):
            print("焦点仍在窗口内部控件上，不关闭弹窗")
            return
            
        # 使用 QTimer.singleShot 延迟关闭，避免焦点问题
        QTimer.singleShot(200, self.checkAndClosePopover)
    
    def checkAndClosePopover(self):
        """检查焦点状态并决定是否关闭弹窗"""
        # 再次检查是否有内部操作或焦点在窗口内
        if self.internal_operation:
            return
            
        focused_widget = QApplication.focusWidget()
        if focused_widget and self.isAncestorOf(focused_widget):
            return
            
        print("确认无内部操作且焦点不在窗口内，关闭弹窗")
        self.closePopoverSafely()
    
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
