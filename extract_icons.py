import os
import shutil
from PIL import Image

def ensure_dir(directory):
    """确保目录存在"""
    if not os.path.exists(directory):
        os.makedirs(directory)

def extract_icons():
    """提取和准备必要的图标"""
    # 创建图标目录
    icons_dir = "icons"
    ensure_dir(icons_dir)
    
    # 图标状态和对应文件名
    icon_states = {
        "idle": "idle.png", 
        "work": "work.png", 
        "shortRest": "shortRest.png", 
        "longRest": "longRest.png"
    }
    
    # 检查是否有图标文件
    icons_found = False
    
    # 检查 Assets 目录下的图标
    for state, filename in icon_states.items():
        # 首先检查 macOS 风格路径
        mac_path = f"Assets/BarIcon{state.title()}.imageset/icon_16x16@2x.png"
        if os.path.exists(mac_path):
            dest_path = f"{icons_dir}/{state.lower()}.png"
            print(f"拷贝 {mac_path} 到 {dest_path}")
            shutil.copy2(mac_path, dest_path)
            icons_found = True
        else:
            print(f"未找到 {mac_path}")
    
    # 如果没有找到图标，创建简单颜色图标
    if not icons_found:
        print("未找到图标文件，创建简单替代图标...")
        try:
            # 创建简单图标
            icon_colors = {
                "idle": (200, 200, 200),    # 灰色
                "work": (255, 50, 50),      # 红色
                "shortRest": (50, 200, 50), # 绿色
                "longRest": (50, 50, 200)   # 蓝色
            }
            
            for state, color in icon_colors.items():
                img = Image.new('RGBA', (32, 32), color + (255,))
                dest_path = f"{icons_dir}/{state.lower()}.png"
                img.save(dest_path)
                print(f"已创建 {dest_path}")
        except Exception as e:
            print(f"创建图标时出错: {e}")
            
    print("\n图标提取/创建完成！请重启应用以加载新图标。")

if __name__ == "__main__":
    extract_icons()
