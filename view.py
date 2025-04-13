from PySide6.QtCore import Qt, QSettings, Signal, Slot, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QCheckBox,
    QTabWidget, QFrame, QApplication
)
from PySide6.QtGui import QFont, QKeySequence, QShortcut

from timer import TBTimer


class TBPopoverView(QWidget):
    """主弹出窗口视图"""
    def __init__(self):
        super().__init__()

        # 修改窗口标志：使用 Qt.Popup 替代 Qt.Tool
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        # 计时器
        self.timer = TBTimer()

        # 初始化UI
        self.initUI()

        # 连接信号
        self.timer.timeLeftStringChanged.connect(self.updateTimeLeft)

        # 添加全局快捷键
        self.shortcut = QShortcut(QKeySequence("Ctrl+Alt+T"), self)
        self.shortcut.activated.connect(self.timer.startStop)

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
        QTimer.singleShot(500, self.resetInternalOperation)

    def onShortRestIntervalChanged(self, value):
        """短休息时间变更处理"""
        self.timer.shortRestIntervalLength = value
        self.timer.settings.setValue("shortRestIntervalLength", value)
        QTimer.singleShot(500, self.resetInternalOperation)

    def onLongRestIntervalChanged(self, value):
        """长休息时间变更处理"""
        self.timer.longRestIntervalLength = value
        self.timer.settings.setValue("longRestIntervalLength", value)
        QTimer.singleShot(500, self.resetInternalOperation)

    def onWorkIntervalsInSetChanged(self, value):
        """工作间隔组数变更处理"""
        self.timer.workIntervalsInSet = value
        self.timer.settings.setValue("workIntervalsInSet", value)
        QTimer.singleShot(500, self.resetInternalOperation)

    def onStopAfterBreakChanged(self, checked):
        """休息后停止设置变更处理"""
        self.timer.stopAfterBreak = checked
        self.timer.settings.setValue("stopAfterBreak", checked)
        QTimer.singleShot(500, self.resetInternalOperation)

    def onShowTimerInMenuBarChanged(self, checked):
        """菜单栏显示计时器设置变更处理"""
        self.timer.showTimerInMenuBar = checked
        self.timer.settings.setValue("showTimerInMenuBar", checked)
        self.timer.updateTimeLeft()
        QTimer.singleShot(500, self.resetInternalOperation)

    def onLaunchAtLoginChanged(self, checked):
        """开机启动设置变更处理"""
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
        volume = value / 100.0
        self.timer.player.setWindupVolume(volume)
        QTimer.singleShot(500, self.resetInternalOperation)

    def onDingVolumeChanged(self, value):
        """叮声音量变更处理"""
        volume = value / 100.0
        self.timer.player.setDingVolume(volume)
        QTimer.singleShot(500, self.resetInternalOperation)

    def onTickingVolumeChanged(self, value):
        """滴答声音量变更处理"""
        volume = value / 100.0
        self.timer.player.setTickingVolume(volume)
        QTimer.singleShot(500, self.resetInternalOperation)

    def resetInternalOperation(self):
        """重置内部操作标志"""

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

    def sizeHint(self):
        """提供推荐大小"""
        return QSize(240, 276)

    def showEvent(self, event):
        super().showEvent(event)
        # 激活窗口，确保它能接收焦点事件，这对于 Qt.Popup 的行为可能很重要
        self.activateWindow()
        self.raise_()  # 再次确保窗口在最前

    def hideEvent(self, event):
        super().hideEvent(event)

    def closePopoverSafely(self):
        """安全地关闭弹出窗口，考虑各种状态"""
        print("尝试安全关闭弹窗")
        if not self.isVisible():
            print("弹窗已经不可见，不需要关闭")
            return
        app = QApplication.instance()
        if hasattr(app, 'status_item'):
            app.status_item.closePopover()
            print("已通过应用单例关闭弹窗")
        else:
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
                self.hide()

    def forceClosePopover(self):
        """强制关闭弹出窗口"""
        print("强制关闭弹窗")
        self.closePopoverSafely()

    def closePopover(self):
        """关闭弹出窗口"""
        self.closePopoverSafely()

