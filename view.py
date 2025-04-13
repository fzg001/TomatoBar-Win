from PySide6.QtCore import Qt, QSettings, Signal, Slot, QSize, QTimer, QPoint
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QCheckBox,
    QTabWidget, QFrame, QApplication, QGridLayout, QToolButton
)
from PySide6.QtGui import QKeySequence, QShortcut, QPainterPath, QPainter, QRegion, QIcon, QColor

from timer import TBTimer


class TBPopoverView(QWidget):
    """主弹出窗口视图"""
    def __init__(self):
        super().__init__()

        # 设置对象名称用于样式表
        self.setObjectName("popoverWidget")

        # 修改窗口标志
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
        self.resize(300, 360)  # 窗口大小

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)  # macOS 风格的更大内边距
        layout.setSpacing(12)  # 增加组件间距

        # 开始/停止按钮
        self.startStopButton = QPushButton(self.tr("Start"))
        self.startStopButton.setObjectName("startStopButton")  # 设置对象名称用于样式表
        self.startStopButton.setFixedHeight(44)  # START按钮高度
        # 设置按钮样式
        self.startStopButton.setStyleSheet("""
            QPushButton#startStopButton {
                background-color: rgb(237, 49, 36);
                color: white;
                border: none; /* 可选：移除边框 */
                border-radius: 5px; /* 可选：添加圆角 */
            }
            QPushButton#startStopButton:hover {
                background-color: rgb(210, 40, 30); /* 可选：悬停时颜色变深 */
            }
            QPushButton#startStopButton:pressed {
                background-color: rgb(190, 30, 20); /* 可选：按下时颜色更深 */
            }
        """)
        self.startStopButton.clicked.connect(self.onStartStopClicked)
        layout.addWidget(self.startStopButton)

        # 选项卡
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setDocumentMode(True)  # 更接近 macOS 风格
        self.tabWidget.setObjectName("mainTabWidget")

        # 设置选项卡按钮的样式表
        self.tabWidget.setStyleSheet("""
            QTabWidget::pane { /* 选项卡内容区域 */
                border-top: 1px solid #C2C7CB; /* 可选：添加分隔线 */
                margin-top: -1px; /* 与选项卡栏重叠1像素 */
                background-color: white; /* 确保内容区域背景是白色 */
            }

            QTabBar {
                qproperty-drawBase: 0; /* 移除选项卡栏的默认背景/边框 */
                margin: 0;
                padding: 0;
                alignment: align-center; /* 尝试居中对齐 */
            }

            QTabBar::tab {
                width: 85px; /* 设置固定宽度 */
                height: 15px; /* 保持高度 */
                padding: 4px 0px; /* 调整内边距，左右设为0 */
                margin: 0; /* 移除外边距 */
                border: 1px solid #C2C7CB; /* 添加边框 */
                border-top-left-radius: 4px; /* 顶部圆角 */
                border-top-right-radius: 4px;
                border-bottom-left-radius: 4px;
                border-bottom-right-radius: 4px;

                color: black; /* 未选中时字体颜色为黑色 */
                background-color: #DCDBDC; /* 未选中时背景颜色 */
            }

            QTabBar::tab:selected {
                color: white; /* 选中时字体颜色为白色 */
                background-color: #939394; /* 选中时背景颜色 */
                border-bottom: 1px solid #939394; /* 覆盖pane的顶部边框，颜色与背景匹配 */
                margin-bottom: -1px; /* 与pane重叠 */
            }

            QTabBar::tab:!selected:hover {
                background-color: #e8e8e8;
            }

            QGroupBox#settingsContainer {
                background-color: #E2E1E2; /* 设置背景颜色 */
                border: 1px solid #D7D6D7; /* 设置边框颜色和宽度 */
                border-radius: 4px; /* 轻微圆角 */
                margin-top: 6px; /* 为标题留出空间 */
                padding: 5px; /* Add some internal padding */
            }

            QGroupBox#settingsContainer::title {
                subcontrol-origin: margin;
                subcontrol-position: top left; /* 标题位置 */
                padding: 0 5px; /* 标题内边距 */
                left: 10px; /* 标题距离左边框的距离 */
                color: #555; /* 标题颜色 (可选) */
            }

            QLabel.valueLabel {
                font-size: 9pt; /* 设置稍小的字体大小 */
                color: #333; /* 设置字体颜色 (可选) */
                padding-top: 2px; /* Add some space above */
                padding-left: 5px; /* Indent slightly */
            }

            QToolButton.spin-button {
                min-width: 18px;
                max-width: 18px;
                min-height: 11px; /* Half height */
                max-height: 11px;
                padding: 0px;
                margin: 0px;
                border: 1px solid #aaa;
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f6f6f6, stop:1 #e0e0e0);
            }
            QToolButton.spin-button:hover {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #e8e8e8, stop:1 #d0d0d0);
            }
            QToolButton.spin-button:pressed {
                background-color: #d0d0d0;
            }
            QToolButton#up-button {
                border-top-left-radius: 2px;
                border-top-right-radius: 2px;
                border-bottom: none;
            }
            QToolButton#down-button {
                 border-bottom-left-radius: 2px;
                 border-bottom-right-radius: 2px;
            }
        """)

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

    def _create_spin_controls(self, current_value, min_val, max_val, step, update_slot, value_label, unit=""):
        """Helper to create Up/Down buttons and connect signals."""
        button_layout = QVBoxLayout()
        button_layout.setSpacing(0)
        button_layout.setContentsMargins(0, 0, 0, 0)

        up_button = QToolButton()
        up_button.setObjectName("up-button")
        up_button.setProperty("class", "spin-button")
        up_button.setArrowType(Qt.UpArrow)
        up_button.clicked.connect(lambda: update_slot(min(current_value() + step, max_val)))

        down_button = QToolButton()
        down_button.setObjectName("down-button")
        down_button.setProperty("class", "spin-button")
        down_button.setArrowType(Qt.DownArrow)
        down_button.clicked.connect(lambda: update_slot(max(current_value() - step, min_val)))

        button_layout.addWidget(up_button)
        button_layout.addWidget(down_button)

        value_label.setText(f"{current_value()} {unit}".strip())

        return button_layout

    def createIntervalsTab(self):
        """创建间隔设置选项卡"""
        tab = QWidget()
        outer_layout = QVBoxLayout(tab)
        outer_layout.setContentsMargins(0, 12, 0, 10)
        outer_layout.setSpacing(10)

        intervalSettingsGroup = QGroupBox(self)
        intervalSettingsGroup.setObjectName("settingsContainer")

        gridLayout = QGridLayout(intervalSettingsGroup)
        gridLayout.setSpacing(5)
        gridLayout.setContentsMargins(10, 15, 10, 10)

        row = 0
        workLabel = QLabel(self.tr("Work interval:"))
        gridLayout.addWidget(workLabel, row, 0, Qt.AlignLeft)

        self.workValueLabel = QLabel()
        self.workValueLabel.setObjectName("valueLabel")
        self.workValueLabel.setProperty("class", "valueLabel")
        gridLayout.addWidget(self.workValueLabel, row + 1, 0, 1, 2, Qt.AlignLeft)

        work_controls = self._create_spin_controls(
            current_value=lambda: self.timer.workIntervalLength,
            min_val=1, max_val=60, step=1,
            update_slot=self.onWorkIntervalChanged,
            value_label=self.workValueLabel,
            unit=self.tr('min')
        )
        gridLayout.addLayout(work_controls, row, 2, Qt.AlignRight)

        row += 2
        shortRestLabel = QLabel(self.tr("Short rest interval:"))
        gridLayout.addWidget(shortRestLabel, row, 0, Qt.AlignLeft)

        self.shortRestValueLabel = QLabel()
        self.shortRestValueLabel.setObjectName("valueLabel")
        self.shortRestValueLabel.setProperty("class", "valueLabel")
        gridLayout.addWidget(self.shortRestValueLabel, row + 1, 0, 1, 2, Qt.AlignLeft)

        short_rest_controls = self._create_spin_controls(
            current_value=lambda: self.timer.shortRestIntervalLength,
            min_val=1, max_val=60, step=1,
            update_slot=self.onShortRestIntervalChanged,
            value_label=self.shortRestValueLabel,
            unit=self.tr('min')
        )
        gridLayout.addLayout(short_rest_controls, row, 2, Qt.AlignRight)

        row += 2
        longRestLabel = QLabel(self.tr("Long rest interval:"))
        gridLayout.addWidget(longRestLabel, row, 0, Qt.AlignLeft)

        self.longRestValueLabel = QLabel()
        self.longRestValueLabel.setObjectName("valueLabel")
        self.longRestValueLabel.setProperty("class", "valueLabel")
        gridLayout.addWidget(self.longRestValueLabel, row + 1, 0, 1, 2, Qt.AlignLeft)

        long_rest_controls = self._create_spin_controls(
            current_value=lambda: self.timer.longRestIntervalLength,
            min_val=1, max_val=60, step=1,
            update_slot=self.onLongRestIntervalChanged,
            value_label=self.longRestValueLabel,
            unit=self.tr('min')
        )
        gridLayout.addLayout(long_rest_controls, row, 2, Qt.AlignRight)

        row += 2
        workIntervalsLabel = QLabel(self.tr("Work intervals:"))
        gridLayout.addWidget(workIntervalsLabel, row, 0, Qt.AlignLeft)

        self.workIntervalsValueLabel = QLabel()
        self.workIntervalsValueLabel.setObjectName("valueLabel")
        self.workIntervalsValueLabel.setProperty("class", "valueLabel")
        gridLayout.addWidget(self.workIntervalsValueLabel, row + 1, 0, 1, 2, Qt.AlignLeft)

        work_intervals_controls = self._create_spin_controls(
            current_value=lambda: self.timer.workIntervalsInSet,
            min_val=1, max_val=10, step=1,
            update_slot=self.onWorkIntervalsInSetChanged,
            value_label=self.workIntervalsValueLabel,
            unit=""
        )
        gridLayout.addLayout(work_intervals_controls, row, 2, Qt.AlignRight)

        gridLayout.setRowStretch(row + 2, 1)
        gridLayout.setColumnStretch(1, 1)

        outer_layout.addWidget(intervalSettingsGroup)
        outer_layout.addStretch(1)
        return tab

    def createSettingsTab(self):
        """创建设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 12, 0, 10)
        layout.setSpacing(10)

        settingsGroup = QGroupBox(self)
        settingsGroup.setObjectName("settingsContainer")
        groupLayout = QVBoxLayout(settingsGroup)
        

        #快捷键以后再说吧
        # shortcutLabel = QLabel(self)
        # groupLayout.addWidget(shortcutLabel)

        self.stopAfterBreakCheck = QCheckBox(self.tr("Stop after break"))
        self.stopAfterBreakCheck.setChecked(self.timer.stopAfterBreak)
        self.stopAfterBreakCheck.toggled.connect(self.onStopAfterBreakChanged)
        groupLayout.addWidget(self.stopAfterBreakCheck)

        self.showTimerInMenuBarCheck = QCheckBox(self.tr("Show timer in menu bar"))
        self.showTimerInMenuBarCheck.setChecked(self.timer.showTimerInMenuBar)
        self.showTimerInMenuBarCheck.toggled.connect(self.onShowTimerInMenuBarChanged)
        groupLayout.addWidget(self.showTimerInMenuBarCheck)

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
        layout.setContentsMargins(0, 12, 0, 10)
        layout.setSpacing(10)

        soundsGroup = QGroupBox(self)
        soundsGroup.setObjectName("settingsContainer")
        groupLayout = QVBoxLayout(soundsGroup)
        groupLayout.setSpacing(12)

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
        self.workValueLabel.setText(f"{value} {self.tr('min')}")

    def onShortRestIntervalChanged(self, value):
        """短休息时间变更处理"""
        self.timer.shortRestIntervalLength = value
        self.timer.settings.setValue("shortRestIntervalLength", value)
        self.shortRestValueLabel.setText(f"{value} {self.tr('min')}")

    def onLongRestIntervalChanged(self, value):
        """长休息时间变更处理"""
        self.timer.longRestIntervalLength = value
        self.timer.settings.setValue("longRestIntervalLength", value)
        self.longRestValueLabel.setText(f"{value} {self.tr('min')}")

    def onWorkIntervalsInSetChanged(self, value):
        """工作间隔组数变更处理"""
        self.timer.workIntervalsInSet = value
        self.timer.settings.setValue("workIntervalsInSet", value)
        self.workIntervalsValueLabel.setText(f"{value}")

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
        """自定义绘制事件，用于实现圆角效果和边框"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 定义圆角半径和画笔宽度
        radius = 10.0
        pen_width = 3  # 改回 1 像素宽度，减少锯齿感

        # 调整矩形以适应画笔宽度，确保边框绘制在控件内部
        rect = self.rect().adjusted(pen_width / 2, pen_width / 2, -pen_width / 2, -pen_width / 2)

        # 创建圆角矩形路径
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        # 设置遮罩以实现圆角
        mask_path = QPainterPath()
        mask_path.addRoundedRect(self.rect(), radius, radius)
        self.setMask(QRegion(mask_path.toFillPolygon().toPolygon()))

        # 先填充背景色
        painter.fillPath(path, Qt.white)

        # 再绘制边框
        pen = painter.pen()
        pen.setColor(QColor("#BFBEBB"))
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.drawPath(path)

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.raise_()

    def hideEvent(self, event):
        super().hideEvent(event)

