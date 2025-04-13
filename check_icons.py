"""检查图标是否存在，如果不存在则报告错误"""

import os
import sys

def check_icons_exist():
    """检查必要的图标文件是否存在"""
    required_icons = [
        "Icons/idle.png", 
        "Icons/work.png",
        "Icons/shortrest.png",
        "Icons/longrest.png"
    ]
    
    missing = []
    for icon_path in required_icons:
        if not os.path.exists(icon_path):
            missing.append(icon_path)
    
    if missing:
        print("错误: 以下必要的图标文件缺失:")
        for path in missing:
            print(f"  - {path}")
        print("\n请确保这些图标文件位于正确的位置，或运行以下命令复制示例图标:")
        print("\npython debug_tools.py")
        return False
    else:
        print("所有必要的图标文件都已找到!")
        return True

if __name__ == "__main__":
    if not check_icons_exist():
        sys.exit(1)
