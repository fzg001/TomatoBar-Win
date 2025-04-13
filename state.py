from enum import Enum, auto
from typing import Dict, Callable, List, Optional, Tuple

class TBStateMachineStates(Enum):
    """状态机的状态"""
    IDLE = auto()
    WORK = auto()
    REST = auto()

class TBStateMachineEvents(Enum):
    """状态机的事件"""
    START_STOP = auto()
    TIMER_FIRED = auto()
    SKIP_REST = auto()

class TBStateMachineContext:
    """状态机上下文，记录状态转换信息"""
    def __init__(self, event: TBStateMachineEvents, from_state: TBStateMachineStates, to_state: TBStateMachineStates):
        self.event = event
        self.fromState = from_state
        self.toState = to_state
    
    def __str__(self):
        return f"Context(event={self.event}, from={self.fromState}, to={self.toState})"

class TBStateMachine:
    """简化版的状态机实现"""
    def __init__(self, initial_state: TBStateMachineStates):
        self.currentState = initial_state
        self.routes = {}  # Dictionary to store routes
        self.handlers = {}  # Dictionary to store handlers
        
    def addRoute(self, 
                event: TBStateMachineEvents, 
                from_state: TBStateMachineStates, 
                to_state: TBStateMachineStates,
                condition: Callable[[], bool] = None):
        """添加状态转换路由"""
        key = (event, from_state)
        if key not in self.routes:
            self.routes[key] = []
        
        self.routes[key].append((to_state, condition))
    
    def addHandler(self, 
                 from_state: Optional[TBStateMachineStates], 
                 to_state: Optional[TBStateMachineStates], 
                 handler: Callable[[TBStateMachineStates, TBStateMachineStates], None]):
        """添加状态转换处理器"""
        key = (from_state, to_state)
        if key not in self.handlers:
            self.handlers[key] = []
        self.handlers[key].append(handler)
    
    def handleEvent(self, event: TBStateMachineEvents):
        """处理事件，执行状态转换"""
        key = (event, self.currentState)
        print(f"状态机处理事件: {event}，当前状态: {self.currentState}")
        
        # 检查是否有匹配的路由
        if key not in self.routes:
            print(f"没有找到匹配的路由: {event}, {self.currentState}")
            return False
        
        # 查找符合条件的路由
        for to_state, condition in self.routes[key]:
            if condition is None or condition():
                # 匹配到路由，执行状态转换
                old_state = self.currentState
                self.currentState = to_state
                print(f"状态转换: {old_state} -> {to_state}，由事件 {event} 触发")
                
                # 创建上下文
                context = TBStateMachineContext(event, old_state, to_state)
                
                # 调用处理器
                self._callHandlers(old_state, to_state)
                
                return True
        
        print(f"没有找到符合条件的路由")
        return False
    
    def _callHandlers(self, from_state: TBStateMachineStates, to_state: TBStateMachineStates):
        """调用所有匹配的处理器"""
        print(f"调用处理器：从 {from_state} 到 {to_state}")
        
        # 调用精确匹配的处理器
        self._callMatchingHandlers((from_state, to_state), from_state, to_state)
        
        # 调用通配符处理器 (None, to_state)
        self._callMatchingHandlers((None, to_state), from_state, to_state)
        
        # 调用通配符处理器 (from_state, None)
        self._callMatchingHandlers((from_state, None), from_state, to_state)
        
        # 调用通配符处理器 (None, None)
        self._callMatchingHandlers((None, None), from_state, to_state)
    
    def _callMatchingHandlers(self, key, actual_from_state, actual_to_state):
        """调用指定键的所有处理器，传递实际的源状态和目标状态"""
        if key in self.handlers:
            for handler in self.handlers[key]:
                try:
                    # 使用实际的状态值，而不是键中可能包含的 None
                    handler(actual_from_state, actual_to_state)
                except Exception as e:
                    print(f"处理器调用错误: {e}")
