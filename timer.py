import time
from datetime import datetime, timedelta
import os
import json
from PySide6.QtCore import QObject, Signal, Slot, QSettings, QTimer
from PySide6.QtWidgets import QMessageBox

from state import TBStateMachine, TBStateMachineStates, TBStateMachineEvents
from player import TBPlayer
from notifications import TBNotificationCenter, TBNotification

class TBTimer(QObject):
    timeLeftStringChanged = Signal(str)
    stateChanged = Signal(str)

    def __init__(self):
        super().__init__()
        self.settings = QSettings("TomatoBar", "TomatoBar")

        # 配置项
        self.stopAfterBreak = self.settings.value("stopAfterBreak", False, bool)
        self.showTimerInMenuBar = self.settings.value("showTimerInMenuBar", True, bool)
        self.workIntervalLength = self.settings.value("workIntervalLength", 25, int)
        self.shortRestIntervalLength = self.settings.value("shortRestIntervalLength", 5, int)
        self.longRestIntervalLength = self.settings.value("longRestIntervalLength", 15, int)
        self.workIntervalsInSet = self.settings.value("workIntervalsInSet", 4, int)
        self.overrunTimeLimit = self.settings.value("overrunTimeLimit", -60.0, float)

        # 初始化状态机
        self.stateMachine = TBStateMachine(TBStateMachineStates.IDLE)
        self.setupStateMachine()

        # 初始化音频播放器
        self.player = TBPlayer()

        # 初始化变量
        self.consecutiveWorkIntervals = 0
        self.notificationCenter = TBNotificationCenter()
        self.finishTime = None
        self.timer = None  # 定时器
        self.timeLeftString = ""

        # 设置通知处理
        self.notificationCenter.setActionHandler(self.onNotificationAction)

    def getStatusItem(self):
        """获取状态栏项，避免循环导入问题"""
        try:
            from app import TBStatusItem
            if TBStatusItem.shared:
                return TBStatusItem.shared
        except Exception as e:
            print(f"获取状态项失败: {e}")
        return None

    def setupStateMachine(self):
        """设置状态机转换规则"""
        self.stateMachine = TBStateMachine(TBStateMachineStates.IDLE)

        self.stateMachine.addRoute(
            TBStateMachineEvents.START_STOP, 
            TBStateMachineStates.IDLE,
            TBStateMachineStates.WORK
        )
        self.stateMachine.addRoute(
            TBStateMachineEvents.START_STOP, 
            TBStateMachineStates.WORK,
            TBStateMachineStates.IDLE
        )
        self.stateMachine.addRoute(
            TBStateMachineEvents.START_STOP, 
            TBStateMachineStates.REST,
            TBStateMachineStates.IDLE
        )
        self.stateMachine.addRoute(
            TBStateMachineEvents.TIMER_FIRED, 
            TBStateMachineStates.WORK,
            TBStateMachineStates.REST
        )
        self.stateMachine.addRoute(
            TBStateMachineEvents.TIMER_FIRED, 
            TBStateMachineStates.REST,
            TBStateMachineStates.IDLE,
            lambda: self.stopAfterBreak
        )
        self.stateMachine.addRoute(
            TBStateMachineEvents.TIMER_FIRED, 
            TBStateMachineStates.REST,
            TBStateMachineStates.WORK,
            lambda: not self.stopAfterBreak
        )
        self.stateMachine.addRoute(
            TBStateMachineEvents.SKIP_REST, 
            TBStateMachineStates.REST,
            TBStateMachineStates.WORK
        )

        self.stateMachine.addHandler(None, TBStateMachineStates.WORK, self.onWorkStart)
        self.stateMachine.addHandler(TBStateMachineStates.WORK, TBStateMachineStates.REST, self.onWorkFinish)
        self.stateMachine.addHandler(TBStateMachineStates.WORK, None, self.onWorkEnd)
        self.stateMachine.addHandler(None, TBStateMachineStates.REST, self.onRestStart)
        self.stateMachine.addHandler(TBStateMachineStates.REST, TBStateMachineStates.WORK, self.onRestFinish)
        self.stateMachine.addHandler(None, TBStateMachineStates.IDLE, self.onIdleStart)

    def startStop(self):
        """启动或停止计时器"""
        self.stateMachine.handleEvent(TBStateMachineEvents.START_STOP)

    def skipRest(self):
        """跳过休息"""
        self.stateMachine.handleEvent(TBStateMachineEvents.SKIP_REST)

    def updateTimeLeft(self):
        """更新剩余时间显示"""
        if not self.finishTime:
            self.timeLeftString = ""
            return

        now = datetime.now()
        time_diff = self.finishTime - now

        total_seconds = max(0, int(time_diff.total_seconds()))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.timeLeftString = f"{minutes:02d}:{seconds:02d}"

        self.timeLeftStringChanged.emit(self.timeLeftString)

        status_item = self.getStatusItem()
        if status_item and self.timer and self.showTimerInMenuBar:
            status_item.setTitle(self.timeLeftString)
        elif status_item:
            status_item.setTitle(None)

    def startTimer(self, seconds):
        """启动计时器"""
        self.finishTime = datetime.now() + timedelta(seconds=seconds)

        if self.timer:
            self.timer.stop()

        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.onTimerTick)
        self.timer.start()

        self.updateTimeLeft()

    def stopTimer(self):
        """停止计时器"""
        if self.timer:
            self.timer.stop()
            self.timer = None
        self.player.stopTicking()
        self.updateTimeLeft()

    def onTimerTick(self):
        """计时器滴答处理，修复状态转换逻辑"""
        self.updateTimeLeft()

        if not self.finishTime:
            return

        now = datetime.now()
        time_left = (self.finishTime - now).total_seconds()

        if time_left <= 0:
            if self.timer:
                self.timer.stop()
                self.timer = None
            QTimer.singleShot(100, lambda: self.handleTimerComplete(time_left))

    def handleTimerComplete(self, time_left):
        """处理计时器完成事件"""
        if time_left < self.overrunTimeLimit:
            self.stateMachine.handleEvent(TBStateMachineEvents.START_STOP)
        else:
            self.stateMachine.handleEvent(TBStateMachineEvents.TIMER_FIRED)

    def onNotificationAction(self, action):
        """处理通知动作"""
        if action == TBNotification.Action.SKIP_REST and self.stateMachine.currentState == TBStateMachineStates.REST:
            self.skipRest()

    def onWorkStart(self, from_state, to_state):
        """工作开始处理"""
        status_item = self.getStatusItem()
        if status_item:
            status_item.setIcon("work")
        self.player.playWindup()
        self.player.startTicking()
        self.startTimer(self.workIntervalLength * 60)

    def onWorkFinish(self, from_state, to_state):
        """工作结束处理"""
        try:
            self.consecutiveWorkIntervals += 1
            self.player.playDing()
        except Exception as e:
            print(f"工作结束处理出错: {e}")

    def onWorkEnd(self, from_state, to_state):
        """工作状态结束处理"""
        self.player.stopTicking()

    def onRestStart(self, from_state, to_state):
        """休息开始处理"""
        try:
            body = self.tr("It's time for a short break!")
            length = self.shortRestIntervalLength
            icon_name = "shortrest"
            if self.consecutiveWorkIntervals >= self.workIntervalsInSet:
                body = self.tr("It's time for a long break!")
                length = self.longRestIntervalLength
                icon_name = "longrest"
                self.consecutiveWorkIntervals = 0

            try:
                from app import TBStatusItem
                if TBStatusItem.shared:
                    TBStatusItem.shared.setIcon(icon_name)
                else:
                    status_item = self.getStatusItem()
                    if status_item:
                        status_item.setIcon(icon_name)
            except Exception as e:
                print(f"设置图标时出错: {e}")
                import traceback
                traceback.print_exc()

            self.notificationCenter.send(
                title=self.tr("Time's up"),
                body=body,
                category=TBNotification.Category.REST_STARTED
            )
            self.player.stopTicking()
            self.startTimer(length * 60)
        except Exception as e:
            print(f"休息开始处理出错: {e}")
            import traceback
            traceback.print_exc()

    def onRestFinish(self, from_state, to_state):
        """休息结束处理"""
        if from_state == TBStateMachineStates.REST and to_state == TBStateMachineStates.WORK:
            self.notificationCenter.send(
                title=self.tr("Break is over"),
                body=self.tr("Keep up the good work!"),
                category=TBNotification.Category.REST_FINISHED
            )

    def onIdleStart(self, from_state, to_state):
        """空闲状态开始处理"""
        self.player.stopTicking()
        self.stopTimer()
        status_item = self.getStatusItem()
        if status_item:
            status_item.setIcon("idle")
        self.consecutiveWorkIntervals = 0