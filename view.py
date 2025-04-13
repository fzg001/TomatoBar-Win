from PySide6.QtCore import (Qt, QSettings, Signal, Slot, QSize, QTimer, QPoint,
                            Property, QEasingCurve, QPropertyAnimation, QRectF)
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QSlider, QSpinBox, QCheckBox,
    QTabWidget, QFrame, QApplication, QGridLayout, QToolButton
)
from PySide6.QtGui import QKeySequence, QShortcut, QPainterPath, QPainter, QRegion, QIcon, QColor, QBrush, QPen

from timer import TBTimer

class ToggleSwitch(QWidget):
    """自定义滑动开关控件"""
    toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 26)
        self.setCursor(Qt.PointingHandCursor)
        self._checked = False

        self._bg_color_off = QColor("#CBCACB")
        self._bg_color_on = QColor("#E6291E")
        self._handle_color = QColor("#FFFFFF")

        self._handle_offset = 3
        self.animation = QPropertyAnimation(self, b"_handle_offset", self)
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

    @Property(int)
    def _handle_offset(self):
        return self.__handle_offset

    @_handle_offset.setter
    def _handle_offset(self, value):
        self.__handle_offset = value
        self.update()

    def isChecked(self):
        return self._checked

    def setChecked(self, checked, emit_signal=True):
        if self._checked != checked:
            self._checked = checked
            start_value = self._handle_offset
            end_value = self.width() - self.height() + 3 if checked else 3

            self.animation.setStartValue(start_value)
            self.animation.setEndValue(end_value)
            self.animation.start()

            if emit_signal:
                self.toggled.emit(self._checked)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setChecked(not self._checked)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        margins = 3
        track_height = self.height() - 2 * margins
        handle_diameter = track_height
        track_radius = track_height / 2.0
        handle_radius = handle_diameter / 2.0

        track_rect = QRectF(margins, margins, self.width() - 2 * margins, track_height)
        bg_color = self._bg_color_on if self._checked else self._bg_color_off
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(track_rect, track_radius, track_radius)

        handle_x = self._handle_offset
        handle_rect = QRectF(handle_x, margins, handle_diameter, handle_diameter)
        painter.setBrush(QBrush(self._handle_color))
        painter.drawEllipse(handle_rect)

    def sizeHint(self):
        return QSize(50, 26)


class TBPopoverView(QWidget):
    """主弹出窗口视图"""
    def __init__(self):
        super().__init__()

        self.setObjectName("popoverWidget")
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)

        self.timer = TBTimer()

        self.initUI()

        self.timer.timeLeftStringChanged.connect(self.updateTimeLeft)

        self.shortcut = QShortcut(QKeySequence("Ctrl+Alt+T"), self)
        self.shortcut.activated.connect(self.timer.startStop)

    def initUI(self):
        self.resize(300, 360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        self.startStopButton = QPushButton(self.tr("Start"))
        self.startStopButton.setObjectName("startStopButton")
        self.startStopButton.setFixedHeight(44)
        self.startStopButton.setStyleSheet("""
            QPushButton#startStopButton {
                background-color: rgb(237, 49, 36);
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton#startStopButton:hover {
                background-color: rgb(210, 40, 30);
            }
            QPushButton#startStopButton:pressed {
                background-color: rgb(190, 30, 20);
            }
        """)
        self.startStopButton.clicked.connect(self.onStartStopClicked)
        layout.addWidget(self.startStopButton)

        self.tabWidget = QTabWidget()
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setDocumentMode(True)
        self.tabWidget.setObjectName("mainTabWidget")
        self.tabWidget.setStyleSheet("""
            QTabWidget::pane {
                border-top: 1px solid #C2C7CB;
                margin-top: -1px;
                background-color: white;
            }
            QTabBar {
                qproperty-drawBase: 0;
                margin: 0;
                padding: 0;
                alignment: align-center;
            }
            QTabBar::tab {
                width: 85px;
                height: 15px;
                padding: 4px 0px;
                margin: 0;
                border: 1px solid #C2C7CB;
                border-radius: 4px;
                color: black;
                background-color: #DCDBDC;
            }
            QTabBar::tab:selected {
                color: white;
                background-color: #939394;
                border-bottom: 1px solid #939394;
                margin-bottom: -1px;
            }
            QTabBar::tab:!selected:hover {
                background-color: #e8e8e8;
            }
            QGroupBox#settingsContainer {
                background-color: #E2E1E2;
                border: 1px solid #D7D6D7;
                border-radius: 4px;
                margin-top: 6px;
                padding: 5px;
            }
            QGroupBox#settingsContainer::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
                color: #555;
            }
            QLabel.valueLabel {
                font-size: 9pt;
                color: #333;
                padding-top: 2px;
                padding-left: 5px;
            }
            QToolButton.spin-button {
                min-width: 18px;
                max-width: 18px;
                min-height: 11px;
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

            /* Style for Volume Sliders */
            QSlider#volumeSlider::groove:horizontal {
                border: 1px solid #bbb;
                background: #E0E0E0;
                height: 6px;
                border-radius: 3px;
                margin: 0px;
            }

            QSlider#volumeSlider::sub-page:horizontal {
                background: #D2281E;
                border: 1px solid #D2281E;
                height: 6px;
                border-radius: 3px;
            }

            QSlider#volumeSlider::add-page:horizontal {
                background: #E0E0E0;
                border: 1px solid #bbb;
                height: 6px;
                border-radius: 3px;
            }

            QSlider#volumeSlider::handle:horizontal {
                background: white;
                border: 1px solid #aaa;
                width: 16px;
                height: 16px;
                margin: -5px 0px;
                border-radius: 8px;
            }

            QSlider#volumeSlider::handle:horizontal:hover {
                background: #f0f0f0;
                border: 1px solid #888;
            }

            QSlider#volumeSlider::handle:horizontal:pressed {
                background: #ddd;
                border: 1px solid #555;
            }
        """)

        self.intervalsTab = self.createIntervalsTab()
        self.tabWidget.addTab(self.intervalsTab, self.tr("Intervals"))

        self.settingsTab = self.createSettingsTab()
        self.tabWidget.addTab(self.settingsTab, self.tr("Settings"))

        self.soundsTab = self.createSoundsTab()
        self.tabWidget.addTab(self.soundsTab, self.tr("Sounds"))

        layout.addWidget(self.tabWidget)

        bottomLayout = QHBoxLayout()
        bottomLayout.setSpacing(8)

        aboutButton = QPushButton(self.tr("About"))
        aboutButton.clicked.connect(self.showAbout)
        bottomLayout.addWidget(aboutButton)

        bottomLayout.addStretch()

        quitButton = QPushButton(self.tr("Quit"))
        quitButton.clicked.connect(self.quit)
        bottomLayout.addWidget(quitButton)

        layout.addLayout(bottomLayout)

        self.setLayout(layout)

    def _create_spin_controls(self, current_value, min_val, max_val, step, update_slot, value_label, unit=""):
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
        tab = QWidget()
        outer_layout = QVBoxLayout(tab)
        outer_layout.setContentsMargins(0, 12, 0, 10)
        outer_layout.setSpacing(10)

        settingsGroup = QGroupBox(self)
        settingsGroup.setObjectName("settingsContainer")
        groupLayout = QGridLayout(settingsGroup)
        groupLayout.setContentsMargins(10, 15, 10, 10)
        groupLayout.setVerticalSpacing(15)
        groupLayout.setHorizontalSpacing(10)

        stopAfterBreakLabel = QLabel(self.tr("Stop after break"))
        groupLayout.addWidget(stopAfterBreakLabel, 0, 0, Qt.AlignLeft | Qt.AlignVCenter)

        self.stopAfterBreakSwitch = ToggleSwitch()
        self.stopAfterBreakSwitch.setChecked(self.timer.stopAfterBreak, emit_signal=False)
        self.stopAfterBreakSwitch.toggled.connect(self.onStopAfterBreakChanged)
        groupLayout.addWidget(self.stopAfterBreakSwitch, 0, 1, Qt.AlignRight | Qt.AlignVCenter)

        showTimerLabel = QLabel(self.tr("Show timer in menu bar"))
        groupLayout.addWidget(showTimerLabel, 1, 0, Qt.AlignLeft | Qt.AlignVCenter)

        self.showTimerInMenuBarSwitch = ToggleSwitch()
        self.showTimerInMenuBarSwitch.setChecked(self.timer.showTimerInMenuBar, emit_signal=False)
        self.showTimerInMenuBarSwitch.toggled.connect(self.onShowTimerInMenuBarChanged)
        groupLayout.addWidget(self.showTimerInMenuBarSwitch, 1, 1, Qt.AlignRight | Qt.AlignVCenter)

        launchAtLoginLabel = QLabel(self.tr("Launch at login"))
        groupLayout.addWidget(launchAtLoginLabel, 2, 0, Qt.AlignLeft | Qt.AlignVCenter)

        self.launchAtLoginSwitch = ToggleSwitch()
        is_launch_at_login = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                                       QSettings.NativeFormat).contains("TomatoBar")
        self.launchAtLoginSwitch.setChecked(is_launch_at_login, emit_signal=False)
        self.launchAtLoginSwitch.toggled.connect(self.onLaunchAtLoginChanged)
        groupLayout.addWidget(self.launchAtLoginSwitch, 2, 1, Qt.AlignRight | Qt.AlignVCenter)

        groupLayout.setColumnStretch(0, 1)
        groupLayout.setColumnStretch(1, 0)

        outer_layout.addWidget(settingsGroup)
        outer_layout.addStretch(1)
        return tab

    def createSoundsTab(self):
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
        self.timer.startStop()

    def updateTimeLeft(self, timeLeft):
        if self.timer.timer:
            self.startStopButton.setText(self.tr("Stop") if self.startStopButton.underMouse() else timeLeft)
        else:
            self.startStopButton.setText(self.tr("Start"))

    def onWorkIntervalChanged(self, value):
        self.timer.workIntervalLength = value
        self.timer.settings.setValue("workIntervalLength", value)
        self.workValueLabel.setText(f"{value} {self.tr('min')}")

    def onShortRestIntervalChanged(self, value):
        self.timer.shortRestIntervalLength = value
        self.timer.settings.setValue("shortRestIntervalLength", value)
        self.shortRestValueLabel.setText(f"{value} {self.tr('min')}")

    def onLongRestIntervalChanged(self, value):
        self.timer.longRestIntervalLength = value
        self.timer.settings.setValue("longRestIntervalLength", value)
        self.longRestValueLabel.setText(f"{value} {self.tr('min')}")

    def onWorkIntervalsInSetChanged(self, value):
        self.timer.workIntervalsInSet = value
        self.timer.settings.setValue("workIntervalsInSet", value)
        self.workIntervalsValueLabel.setText(f"{value}")

    def onStopAfterBreakChanged(self, checked):
        self.timer.stopAfterBreak = checked
        self.timer.settings.setValue("stopAfterBreak", checked)

    def onShowTimerInMenuBarChanged(self, checked):
        self.timer.showTimerInMenuBar = checked
        self.timer.settings.setValue("showTimerInMenuBar", checked)
        self.timer.updateTimeLeft()

    def onLaunchAtLoginChanged(self, checked):
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run",
                           QSettings.NativeFormat)
        app_path = QApplication.applicationFilePath().replace('/', '\\')
        if checked:
            settings.setValue("TomatoBar", f'"{app_path}"')
        else:
            settings.remove("TomatoBar")

    def onWindupVolumeChanged(self, value):
        volume = value / 100.0
        self.timer.player.setWindupVolume(volume)

    def onDingVolumeChanged(self, value):
        volume = value / 100.0
        self.timer.player.setDingVolume(volume)

    def onTickingVolumeChanged(self, value):
        volume = value / 100.0
        self.timer.player.setTickingVolume(volume)

    def showAbout(self):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.about(
            self,
            "TomatoBar",
            "TomatoBar for Windows\n\n"
            "A Pomodoro timer for the Windows system tray.\n\n"
            "For learning and communication only, no commercial use, please delete within 24 hours.\n\n"
            "Based on the macOS TomatoBar by Ilya Voronin.\n"
            "https://github.com/ivoronin/TomatoBar"
        )

    def quit(self):
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def sizeHint(self):
        return QSize(300, 360)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        radius = 10.0
        pen_width = 1

        rect = self.rect().adjusted(pen_width / 2, pen_width / 2, -pen_width / 2, -pen_width / 2)

        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)

        mask_path = QPainterPath()
        mask_path.addRoundedRect(self.rect(), radius, radius)
        self.setMask(QRegion(mask_path.toFillPolygon().toPolygon()))

        painter.fillPath(path, Qt.white)

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

