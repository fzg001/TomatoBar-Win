from state import TBStateMachine, TBStateMachineStates, TBStateMachineEvents

def main():
    """测试状态机转换逻辑"""
    machine = TBStateMachine(TBStateMachineStates.IDLE)
    
    # 设置与 macOS 相同的路由
    machine.addRoute(TBStateMachineEvents.START_STOP, TBStateMachineStates.IDLE, TBStateMachineStates.WORK)
    machine.addRoute(TBStateMachineEvents.START_STOP, TBStateMachineStates.WORK, TBStateMachineStates.IDLE)
    machine.addRoute(TBStateMachineEvents.START_STOP, TBStateMachineStates.REST, TBStateMachineStates.IDLE)
    machine.addRoute(TBStateMachineEvents.TIMER_FIRED, TBStateMachineStates.WORK, TBStateMachineStates.REST)
    machine.addRoute(TBStateMachineEvents.TIMER_FIRED, TBStateMachineStates.REST, TBStateMachineStates.IDLE, lambda: True)  # 模拟 stopAfterBreak
    machine.addRoute(TBStateMachineEvents.TIMER_FIRED, TBStateMachineStates.REST, TBStateMachineStates.WORK, lambda: False)  # 模拟 !stopAfterBreak
    machine.addRoute(TBStateMachineEvents.SKIP_REST, TBStateMachineStates.REST, TBStateMachineStates.WORK)
    
    # 测试完整工作流程
    print("初始状态:", machine.currentState)
    
    print("\n测试场景1: 开始工作 -> 工作完成 -> 休息 -> 休息结束回到工作")
    machine.handleEvent(TBStateMachineEvents.START_STOP)  # idle -> work
    print("状态:", machine.currentState)
    machine.handleEvent(TBStateMachineEvents.TIMER_FIRED)  # work -> rest
    print("状态:", machine.currentState)
    machine.handleEvent(TBStateMachineEvents.TIMER_FIRED)  # rest -> idle (with stopAfterBreak)
    print("状态:", machine.currentState)
    
    print("\n测试场景2: 开始工作 -> 手动停止")
    machine.handleEvent(TBStateMachineEvents.START_STOP)  # idle -> work
    print("状态:", machine.currentState)
    machine.handleEvent(TBStateMachineEvents.START_STOP)  # work -> idle
    print("状态:", machine.currentState)
    
    print("\n测试场景3: 开始工作 -> 工作完成 -> 休息 -> 跳过休息")
    machine.handleEvent(TBStateMachineEvents.START_STOP)  # idle -> work
    print("状态:", machine.currentState)
    machine.handleEvent(TBStateMachineEvents.TIMER_FIRED)  # work -> rest
    print("状态:", machine.currentState)
    machine.handleEvent(TBStateMachineEvents.SKIP_REST)  # rest -> work
    print("状态:", machine.currentState)

if __name__ == "__main__":
    main()
