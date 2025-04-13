from PySide6.QtCore import Qt, QSettings, Signal, Slot, QSize, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QCheckBox,
    QTabWidget, QFrame, QApplication
)
from PySide6.QtGui import QKeySequence, QShortcut, QPainterPath, QPainter, QRegion

from timer import TBTimer
from styles import TBStyles  # 导入样式类

class TBPopoverView(QWidget):
    """主弹出窗口视图"""
    def __init__(self):
        super().__init__()

        # 设置对象名称用于样式表
        self.setObjectName("popoverWidget")

        # 修改窗口标志
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # 应用 macOS 样式
        TBStyles.applyPopoverStyle(self)
        

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
        self.resize(300, 360)  # 略微增加窗口大小以容纳更美观的布局

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)  # macOS 风格的更大内边距
        layout.setSpacing(12)  # 增加组件间距

        # 开始/停止按钮
        self.startStopButton = QPushButton(self.tr("Start"))
        self.startStopButton.setObjectName("startStopButton")  # 设置对象名称用于样式表
        self.startStopButton.setFixedHeight(44)  # macOS 风格的更高按钮
        self.startStopButton.clicked.connect(self.onStartStopClicked)
        layout.addWidget(self.startStopButton)

        # 选项卡
        self.tabWidget = QTabWidget()
        # self.tabWidget.tabBar().setExpanding(True) # 确保此行被移除或注释掉
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setDocumentMode(True)  # 更接近 macOS 风格
        self.tabWidget.setObjectName("mainTabWidget")

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

        # 底部按钮布局
        bottomLayout = QHBoxLayout()
        bottomLayout.setSpacing(8)

        # 关于按钮
        aboutButton = QPushButton(self.tr("About"))
        aboutButton.clicked.connect(self.showAbout)
        bottomLayout.addWidget(aboutButton)

        # 添加伸缩项
        bottomLayout.addStretch()

        # 退出按钮
        quitButton = QPushButton(self.tr("Quit"))
        quitButton.clicked.connect(self.quit)
        bottomLayout.addWidget(quitButton)

        layout.addLayout(bottomLayout)

        self.setLayout(layout)

    def createIntervalsTab(self):
        """创建间隔设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        # 将左右边距设置为 0
        layout.setContentsMargins(0, 12, 0, 10) # 修改: 左右边距改为 0
        layout.setSpacing(10)

        # 创建一个浅灰色容器来包含所有设置
        intervalSettingsGroup = QGroupBox(self.tr("Time Intervals"))
        intervalSettingsGroup.setObjectName("settingsContainer")
        groupLayout = QVBoxLayout(intervalSettingsGroup)
        groupLayout.setSpacing(12)

        # 工作时间
        workLayout = QHBoxLayout()
        workLabel = QLabel(self.tr("Work interval:"))
        workLabel.setMinimumWidth(120)
        workLayout.addWidget(workLabel)
        workLayout.addStretch()

        self.workSpinBox = QSpinBox()
        self.workSpinBox.setRange(1, 60)
        self.workSpinBox.setValue(self.timer.workIntervalLength)
        self.workSpinBox.setSuffix(f" {self.tr('min')}")
        self.workSpinBox.valueChanged.connect(self.onWorkIntervalChanged)
        self.workSpinBox.setMinimumWidth(70)
        self.workSpinBox.setObjectName("settingSpinBox")
        workLayout.addWidget(self.workSpinBox)

        groupLayout.addLayout(workLayout)

        # 短休息时间
        shortRestLayout = QHBoxLayout()
        shortRestLabel = QLabel(self.tr("Short rest interval:"))
        shortRestLabel.setMinimumWidth(120)
        shortRestLayout.addWidget(shortRestLabel)
        shortRestLayout.addStretch()

        self.shortRestSpinBox = QSpinBox()
        self.shortRestSpinBox.setRange(1, 60)
        self.shortRestSpinBox.setValue(self.timer.shortRestIntervalLength)
        self.shortRestSpinBox.setSuffix(f" {self.tr('min')}")
        self.shortRestSpinBox.valueChanged.connect(self.onShortRestIntervalChanged)
        self.shortRestSpinBox.setMinimumWidth(70)
        self.shortRestSpinBox.setObjectName("settingSpinBox")
        shortRestLayout.addWidget(self.shortRestSpinBox)

        groupLayout.addLayout(shortRestLayout)

        # 长休息时间
        longRestLayout = QHBoxLayout()
        longRestLabel = QLabel(self.tr("Long rest interval:"))
        longRestLabel.setMinimumWidth(120)
        longRestLayout.addWidget(longRestLabel)
        longRestLayout.addStretch()

        self.longRestSpinBox = QSpinBox()
        self.longRestSpinBox.setRange(1, 60)
        self.longRestSpinBox.setValue(self.timer.longRestIntervalLength)
        self.longRestSpinBox.setSuffix(f" {self.tr('min')}")
        self.longRestSpinBox.setToolTip(self.tr("Duration of the lengthy break, taken after finishing work interval set"))
        self.longRestSpinBox.valueChanged.connect(self.onLongRestIntervalChanged)
        self.longRestSpinBox.setMinimumWidth(70)
        self.longRestSpinBox.setObjectName("settingSpinBox")
        longRestLayout.addWidget(self.longRestSpinBox)

        groupLayout.addLayout(longRestLayout)

        # 工作间隔组数
        workIntervalsLayout = QHBoxLayout()
        workIntervalsLabel = QLabel(self.tr("Work intervals:"))
        workIntervalsLabel.setMinimumWidth(120)
        workIntervalsLayout.addWidget(workIntervalsLabel)
        workIntervalsLayout.addStretch()

        self.workIntervalsSpinBox = QSpinBox()
        self.workIntervalsSpinBox.setRange(1, 10)
        self.workIntervalsSpinBox.setValue(self.timer.workIntervalsInSet)
        self.workIntervalsSpinBox.setToolTip(self.tr("Number of working intervals in the set, after which a lengthy break taken"))
        self.workIntervalsSpinBox.valueChanged.connect(self.onWorkIntervalsInSetChanged)
        self.workIntervalsSpinBox.setMinimumWidth(70)
        self.workIntervalsSpinBox.setObjectName("settingSpinBox")
        workIntervalsLayout.addWidget(self.workIntervalsSpinBox)

        groupLayout.addLayout(workIntervalsLayout)

        # 将GroupBox添加到主布局
        layout.addWidget(intervalSettingsGroup)
        layout.addStretch(1)
        return tab

    def createSettingsTab(self):
        """创建设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        # 将左右边距设置为 0
        layout.setContentsMargins(0, 12, 0, 10) # 修改: 左右边距改为 0
        layout.setSpacing(10)

        # 创建一个浅灰色容器
        settingsGroup = QGroupBox(self.tr("Application Settings"))
        settingsGroup.setObjectName("settingsContainer")
        groupLayout = QVBoxLayout(settingsGroup)

        # 快捷键设置
        shortcutLabel = QLabel(self.tr("Shortcut: Ctrl+Alt+T"))
        groupLayout.addWidget(shortcutLabel)

        # 休息后停止
        self.stopAfterBreakCheck = QCheckBox(self.tr("Stop after break"))
        self.stopAfterBreakCheck.setChecked(self.timer.stopAfterBreak)
        self.stopAfterBreakCheck.toggled.connect(self.onStopAfterBreakChanged)
        groupLayout.addWidget(self.stopAfterBreakCheck)

        # 在菜单栏显示计时器
        self.showTimerInMenuBarCheck = QCheckBox(self.tr("Show timer in menu bar"))
        self.showTimerInMenuBarCheck.setChecked(self.timer.showTimerInMenuBar)
        self.showTimerInMenuBarCheck.toggled.connect(self.onShowTimerInMenuBarChanged)
        groupLayout.addWidget(self.showTimerInMenuBarCheck)

        # 开机启动
        self.launchAtLoginCheck = QCheckBox(self.tr("Launch at login"))
        self.launchAtLoginCheck.setChecked(QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                                                    QSettings.NativeFormat).contains("TomatoBar"))
        self.launchAtLoginCheck.toggled.connect(self.onLaunchAtLoginChanged)
        groupLayout.addWidget(self.launchAtLoginCheck)

        layout.addWidget(settingsGroup)
        layout.addStretch(1)
        return tab

    def createSoundsTab(self):
        """创建声音设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        # 将左右边距设置为 0
        layout.setContentsMargins(0, 12, 0, 10)  # 修改: 左右边距改为 0
        layout.setSpacing(10)

        # 创建一个浅灰色容器
        soundsGroup = QGroupBox(self.tr("Sound Settings"))
        soundsGroup.setObjectName("settingsContainer")
        groupLayout = QVBoxLayout(soundsGroup)
        groupLayout.setSpacing(12)

        # 发条声滑块
        windupLayout = QHBoxLayout()
        windupLabel = QLabel(self.tr("Windup"))
        windupLabel.setMinimumWidth(60)
        windupLayout.addWidget(windupLabel)

        self.windupSlider = QSlider(Qt.Horizontal)
        self.windupSlider.setRange(0, 200)
        self.windupSlider.setValue(int(self.timer.player.windupVolume * 100))
        self.windupSlider.valueChanged.connect(self.onWindupVolumeChanged)
        self.windupSlider.setObjectName("volumeSlider")
        windupLayout.addWidget(self.windupSlider)

        groupLayout.addLayout(windupLayout)

        # 叮声滑块
        dingLayout = QHBoxLayout()
        dingLabel = QLabel(self.tr("Ding"))
        dingLabel.setMinimumWidth(60)
        dingLayout.addWidget(dingLabel)

        self.dingSlider = QSlider(Qt.Horizontal)
        self.dingSlider.setRange(0, 200)
        self.dingSlider.setValue(int(self.timer.player.dingVolume * 100))
        self.dingSlider.valueChanged.connect(self.onDingVolumeChanged)
        self.dingSlider.setObjectName("volumeSlider")
        dingLayout.addWidget(self.dingSlider)

        groupLayout.addLayout(dingLayout)

        # 滴答声滑块
        tickingLayout = QHBoxLayout()
        tickingLabel = QLabel(self.tr("Ticking"))
        tickingLabel.setMinimumWidth(60)
        tickingLayout.addWidget(tickingLabel)

        self.tickingSlider = QSlider(Qt.Horizontal)
        self.tickingSlider.setRange(0, 200)
        self.tickingSlider.setValue(int(self.timer.player.tickingVolume * 100))
        self.tickingSlider.valueChanged.connect(self.onTickingVolumeChanged)
        self.tickingSlider.setObjectName("volumeSlider")
        tickingLayout.addWidget(self.tickingSlider)

        groupLayout.addLayout(tickingLayout)

        layout.addWidget(soundsGroup)
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

    def sizeHint(self):
        """提供推荐大小"""
        return QSize(300, 360)  # 调整为更大的尺寸以适应美观布局

    def paintEvent(self, event):
        """自定义绘制事件，用于实现圆角效果"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 设置圆角路径
        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 10, 10)
        
        # 设置窗口遮罩，这样窗口外的内容不会显示
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))
        
        super().paintEvent(event)

    def showEvent(self, event):
        super().showEvent(event)
        # 激活窗口，确保它能接收焦点事件
        self.activateWindow()
        self.raise_()  # 确保窗口在最前

    def hideEvent(self, event):
        super().hideEvent(event)

