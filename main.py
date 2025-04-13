import sys
import os
from PySide6.QtWidgets import QApplication

def check_icons_exist():
    """检查图标文件是否存在，并打印路径信息"""
    print("检查图标文件...")
    icon_names = ["idle", "work", "shortrest", "longrest"]
    icon_dirs = ["Icons", "icons"]
    
    icons_ok = True
    for dir_name in icon_dirs:
        if os.path.exists(dir_name):
            print(f"找到图标目录: {dir_name}")
            for icon_name in icon_names:
                path = f"{dir_name}/{icon_name}.png"
                if os.path.exists(path):
                    print(f"  ✓ 找到图标: {path}")
                else:
                    print(f"  ✗ 缺少图标: {path}")
                    icons_ok = False
        else:
            print(f"图标目录不存在: {dir_name}")
            icons_ok = False
    return icons_ok

def main():
    # 导入并运行图标检查
    icons_ok = check_icons_exist()
    if not icons_ok:
        print("警告: 图标检查失败，但仍尝试启动应用")
    
    # 当前目录
    print(f"当前工作目录: {os.getcwd()}")
    
    # 列出 Icons 目录内容
    icons_dir = "Icons"
    if os.path.exists(icons_dir):
        print(f"\n{icons_dir} 目录中的文件:")
        for file in os.listdir(icons_dir):
            print(f"  - {os.path.join(icons_dir, file)}")
    else:
        print(f"\n错误: {icons_dir} 目录不存在!")
    
    # 导入应用类并启动
    from app import TBApp
    app = TBApp(sys.argv)
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
