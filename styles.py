from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor, QFont

class TBStyles:
    """TomatoBar 样式管理类"""
    
    # macOS 颜色定义
    ACCENT_COLOR = "#FF3B30"  # 番茄红色
    BACKGROUND_COLOR = "#FFFFFF"
    TEXT_COLOR = "#000000"
    SECONDARY_TEXT_COLOR = "#737373"
    BORDER_COLOR = "#D1D1D1"
    CONTAINER_BG_COLOR = "#F8F8F8"  # 添加容器背景色
    
    @staticmethod
    def applyApplicationStyle():
        """应用全局应用程序样式"""
        # 设置应用程序样式表
        app = QApplication.instance()
        if app:
            # 设置字体
            font = QFont("SF Pro", 10)  # macOS 默认字体
            app.setFont(font)
            
            # 设置全局样式表
            app.setStyleSheet("""
                QWidget {
                    font-family: "SF Pro", "Segoe UI", "Microsoft YaHei", sans-serif;
                    color: #000000;
                }
                
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D1D1;
                    border-radius: 6px;
                    padding: 5px 10px;
                    min-height: 25px;
                }
                
                QPushButton:hover {
                    background-color: #F5F5F5;
                }
                
                QPushButton:pressed {
                    background-color: #EBEBEB;
                }
                
                QTabWidget::pane {
                    border: 1px solid #D1D1D1;
                    border-radius: 6px;
                    top: -1px;
                }
                
                QTabBar::tab {
                    background-color: #F0F0F0;
                    border: 1px solid #D1D1D1;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 6px 10px;
                    margin-right: 2px;
                }
                
                QTabBar::tab:selected {
                    background-color: #FFFFFF;
                    border-bottom-color: #FFFFFF;
                }
                
                QTabBar::tab:!selected {
                    margin-top: 2px;
                }
                
                QCheckBox {
                    spacing: 8px;
                }
                
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                    border-radius: 3px;
                    border: 1px solid #D1D1D1;
                }
                
                QCheckBox::indicator:checked {
                    background-color: """ + TBStyles.ACCENT_COLOR + """;
                    border-color: """ + TBStyles.ACCENT_COLOR + """;
                    image: url(Icons/check.png);
                }
                
                QSpinBox {
                    border: 1px solid #D1D1D1;
                    border-radius: 4px;
                    padding: 3px;
                }
                
                QSlider::groove:horizontal {
                    height: 4px;
                    background: #D1D1D1;
                    border-radius: 2px;
                }
                
                QSlider::handle:horizontal {
                    background: """ + TBStyles.ACCENT_COLOR + """;
                    border: none;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }
                
                QSlider::add-page:horizontal {
                    background: #D1D1D1;
                    border-radius: 2px;
                }
                
                QSlider::sub-page:horizontal {
                    background: """ + TBStyles.ACCENT_COLOR + """;
                    border-radius: 2px;
                }
            """)

    @staticmethod
    def applyPopoverStyle(widget):
        """应用 macOS 风格的 Popover 样式到窗口"""
        # 设置窗口背景和圆角
        widget.setStyleSheet("""
            QWidget#popoverWidget {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #D1D1D1;
            }
            
            QPushButton#startStopButton {
                background-color: """ + TBStyles.ACCENT_COLOR + """;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px;
                min-height: 40px;
                border: none;
            }
            
            QPushButton#startStopButton:hover {
                background-color: #E02E24;
            }
            
            QPushButton#startStopButton:pressed {
                background-color: #C32A20;
            }
            
            QGroupBox {
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 10px;
                background-color: """ + TBStyles.CONTAINER_BG_COLOR + """;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
                color: #666666;
            }
            
            QTabWidget::pane {
                border: 1px solid #D1D1D1;
                border-radius: 6px;
                top: -1px;
            }

            QTabBar::tab {
                background-color: #F0F0F0;
                border: 1px solid #D1D1D1;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 20.495px;  /* 恢复标准水平填充 */
                margin-right: 3.489px; /* 保留标签之间的间距 */
            }
   
            QTabBar::tab:selected {
                background-color: #FFFFFF;
                border-bottom-color: #FFFFFF;
            }
            
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
            
            QSpinBox#settingSpinBox {
                border: 1px solid #D1D1D1;
                border-radius: 4px;
                padding: 3px 5px;
                background-color: white;
                min-width: 70px;
            }
            
            QSpinBox#settingSpinBox::up-button {
                width: 16px;
                border-left: 1px solid #D1D1D1;
                border-bottom: 1px solid #D1D1D1;
                border-top-right-radius: 3px;
                subcontrol-position: top right;
                subcontrol-origin: border;
            }
            
            QSpinBox#settingSpinBox::down-button {
                width: 16px;
                border-left: 1px solid #D1D1D1;
                border-top: 1px solid #D1D1D1;
                border-bottom-right-radius: 3px;
                subcontrol-position: bottom right;
                subcontrol-origin: border;
            }
            
            QSpinBox#settingSpinBox::up-button:hover,
            QSpinBox#settingSpinBox::down-button:hover {
                background-color: #F5F5F5;
            }
            
            QSpinBox#settingSpinBox::up-button:pressed,
            QSpinBox#settingSpinBox::down-button:pressed {
                background-color: #EBEBEB;
            }
            
            QSlider#volumeSlider::groove:horizontal {
                height: 6px;
                background: #D1D1D1;
                border-radius: 3px;
            }
            
            QSlider#volumeSlider::handle:horizontal {
                background: """ + TBStyles.ACCENT_COLOR + """;
                border: none;
                width: 18px;
                height: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            
            QSlider#volumeSlider::add-page:horizontal {
                background: #D1D1D1;
                border-radius: 3px;
            }
            
            QSlider#volumeSlider::sub-page:horizontal {
                background: """ + TBStyles.ACCENT_COLOR + """;
                border-radius: 3px;
            }
        """)

    @staticmethod
    def applyMacShadow(widget):
        """应用 macOS 风格的阴影效果"""
        # 在 PySide6 中需要使用 QGraphicsDropShadowEffect
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 50))
        shadow.setOffset(0, 2)
        widget.setGraphicsEffect(shadow)

    @staticmethod
    def getPopoverArrowSize():
        """获取 Popover 箭头大小"""
        return 12

    @staticmethod
    def isDarkMode():
        """检测系统是否处于深色模式"""
        # 这是一个简化实现，在 Windows 上需要通过注册表或其他方式检测
        settings = QSettings("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize", 
                           QSettings.NativeFormat)
        return settings.value("AppsUseLightTheme", 1) == 0
