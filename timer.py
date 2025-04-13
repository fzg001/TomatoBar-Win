import time
from datetime import datetime, timedelta
import os
import json
from PySide6.QtCore import QObject, Signal, Slot, QSettings, QTimer, QElapsedTimer
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
        self.elapsedTimer = QElapsedTimer()  # 高精度计时器
        
        # 设置通知处理
        self.notificationCenter.setActionHandler(self.onNotificationAction)
    
    def getStatusItem(self):
        """获取状态栏项，避免循环导入问题"""
        try:
            # 确保不会因为循环导入失败
            from app import TBStatusItem
            if TBStatusItem.shared:
                return TBStatusItem.shared
            print("警告: TBStatusItem.shared 未初始化")
        except Exception as e:
            print(f"获取状态项失败: {e}")
        return None
    
    def setupStateMachine(self):
        """设置状态机转换规则"""
        # 清空之前的路由
        self.stateMachine = TBStateMachine(TBStateMachineStates.IDLE)
        
        print("初始化状态机路由...")
        # 从空闲开始工作 (START_STOP 按钮触发)
        self.stateMachine.addRoute(
            TBStateMachineEvents.START_STOP, 
            TBStateMachineStates.IDLE,
            TBStateMachineStates.WORK
        )
        # 从工作停止到空闲 (START_STOP 按钮触发)
        self.stateMachine.addRoute(
            TBStateMachineEvents.START_STOP, 
            TBStateMachineStates.WORK,
            TBStateMachineStates.IDLE
        )
        # 从休息停止到空闲 (START_STOP 按钮触发)
        self.stateMachine.addRoute(
            TBStateMachineEvents.START_STOP, 
            TBStateMachineStates.REST,
            TBStateMachineStates.IDLE
        )
        # 工作阶段完成后进入休息 (TIMER_FIRED 事件触发)
        self.stateMachine.addRoute(
            TBStateMachineEvents.TIMER_FIRED, 
            TBStateMachineStates.WORK,
            TBStateMachineStates.REST
        )
        # 休息完成后根据设置回到工作或停止 (TIMER_FIRED 事件触发)
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
        # 跳过休息回到工作 (SKIP_REST 事件触发)
        self.stateMachine.addRoute(
            TBStateMachineEvents.SKIP_REST, 
            TBStateMachineStates.REST,
            TBStateMachineStates.WORK
        )
        
        # 添加状态转换处理器
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
        
        # 格式化为分:秒
        total_seconds = max(0, int(time_diff.total_seconds()))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.timeLeftString = f"{minutes:02d}:{seconds:02d}"
        
        # 发出信号以更新UI
        self.timeLeftStringChanged.emit(self.timeLeftString)
        
        # 更新托盘图标标题
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
        
        # 使用高精度计时器记录开始时间
        self.elapsedTimer.start()
        
        # 使用更精确的计时器，每500毫秒检查一次
        self.timer = QTimer()
        self.timer.setInterval(200)  # 更高频率更新
        self.timer.timeout.connect(self.onTimerTick)
        self.timer.start()
        
        # 更新初始时间显示
        self.updateTimeLeft()
    
    def stopTimer(self):
        """停止计时器"""
        if self.timer:
            self.timer.stop()
            self.timer = None
        # 确保停止计时器时也停止滴答声
        print("停止计时器，停止滴答声")
        self.player.stopTicking()
        self.updateTimeLeft()
    
    def onTimerTick(self):
        """计时器滴答处理，修复状态转换逻辑"""
        self.updateTimeLeft()
        
        if not self.finishTime:
            return
        
        # 使用系统时间而不是计时器间隔，避免累积误差
        now = datetime.now()
        time_left = (self.finishTime - now).total_seconds()
        
        # 调试输出
        if int(time_left) % 10 == 0:
            print(f"倒计时: {int(time_left)} 秒, 当前状态: {self.stateMachine.currentState}")
            
        if time_left <= 0:
            print(f"时间到！当前状态: {self.stateMachine.currentState}, 时间剩余: {time_left}秒")
            # 停止当前计时器以避免重复触发
            if self.timer:
                self.timer.stop()
                self.timer = None
            # 安全处理计时器完成事件
            # 延迟触发状态转换，避免并发问题
            QTimer.singleShot(100, lambda: self.handleTimerComplete(time_left))
    
    def handleTimerComplete(self, time_left):
        """处理计时器完成事件"""
        if time_left < self.overrunTimeLimit:
            print(f"超过时间限制 {self.overrunTimeLimit}，停止计时器")
            self.stateMachine.handleEvent(TBStateMachineEvents.START_STOP)
        else:
            print(f"触发状态转换，当前状态: {self.stateMachine.currentState}")
            # 确保状态转换被正确处理
            result = self.stateMachine.handleEvent(TBStateMachineEvents.TIMER_FIRED)
            print(f"状态转换结果: {result}, 新状态: {self.stateMachine.currentState}")
    
    def onNotificationAction(self, action):
        """处理通知动作"""
        if action == TBNotification.Action.SKIP_REST and self.stateMachine.currentState == TBStateMachineStates.REST:
            self.skipRest()
    
    def onWorkStart(self, from_state, to_state):
        """工作开始处理"""
        print(f"开始工作状态: 从 {from_state} 到 {to_state}")
        status_item = self.getStatusItem()
        if status_item:
            # 明确打印图标设置操作
            print("设置工作图标")
            status_item.setIcon("work")
        self.player.playWindup()
        self.player.startTicking()
        self.startTimer(self.workIntervalLength * 60)
    
    def onWorkFinish(self, from_state, to_state):
        """工作结束处理"""
        try:
            print(f"结束工作间隔: 从 {from_state} 到 {to_state}")
            self.consecutiveWorkIntervals += 1
            self.player.playDing()
        except Exception as e:
            print(f"工作结束处理出错: {e}")
    
    def onWorkEnd(self, from_state, to_state):
        """工作状态结束处理"""
        print(f"工作状态结束: 从 {from_state} 到 {to_state}")
        self.player.stopTicking()
    
    def onRestStart(self, from_state, to_state):
        """休息开始处理"""
        try:
            print(f"开始休息状态: 从 {from_state} 到 {to_state}, 已完成工作间隔: {self.consecutiveWorkIntervals}")
            body = "It's time for a short break!"  # 默认英文
            try:
                body = QObject.tr("It's time for a short break!")  # 尝试翻译
            except:
                pass
            length = self.shortRestIntervalLength
            icon_name = "shortrest"  # 使用小写，与文件名匹配
            if self.consecutiveWorkIntervals >= self.workIntervalsInSet:
                print(f"触发长休息: 连续工作间隔 {self.consecutiveWorkIntervals} >= {self.workIntervalsInSet}")
                body = self.tr("It's time for a long break!")
                length = self.longRestIntervalLength
                icon_name = "longrest"  # 使用小写，与文件名匹配
                self.consecutiveWorkIntervals = 0
            
            # 直接尝试设置图标，不依赖 getStatusItem
            try:
                # 直接导入 TBStatusItem 并尝试设置图标
                from app import TBStatusItem
                if TBStatusItem.shared:
                    print(f"直接设置休息图标: {icon_name}")
                    TBStatusItem.shared.setIcon(icon_name)
                else:
                    print("TBStatusItem.shared 未初始化，尝试备用方法")
                    # 备用方案：使用 getStatusItem
                    status_item = self.getStatusItem()
                    if status_item:
                        print(f"通过备用方法设置图标: {icon_name}")
                        status_item.setIcon(icon_name)
                    else:
                        print("所有方法都失败，无法设置图标")
            except Exception as e:
                print(f"设置图标时出错: {e}")
                import traceback
                traceback.print_exc()
            
            self.notificationCenter.send(
                title="Time's up",
                body=body,
                category=TBNotification.Category.REST_STARTED
            )
            print(f"休息时长设置为: {length} 分钟")
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
        print("进入空闲状态，停止滴答声")
        self.player.stopTicking()  # 确保在空闲状态也停止滴答声
        self.stopTimer()
        status_item = self.getStatusItem()
        if status_item:
            # 明确打印图标设置操作
            print("设置空闲图标")
            status_item.setIcon("idle")
        self.consecutiveWorkIntervals = 0
    
    def tr(self, text):
        """翻译辅助方法"""
        return QObject.tr(self, text)