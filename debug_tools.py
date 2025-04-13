"""TomatoBar 调试工具，用于检查和修复常见问题"""

import os
import sys
from PIL import Image

def check_translation_files():
    """检查翻译文件是否存在和格式是否正确"""
    print("检查翻译文件...")
    
    files_to_check = [
        "localization/zh-Hans.json",
        "localization/en.json"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✓ 文件存在: {file_path}")
            # 可以添加更多检查，如JSON格式验证
        else:
            print(f"✗ 文件不存在: {file_path}")

def create_default_icons():
    """创建默认图标文件"""
    print("创建默认图标...")
    
    icons_dir = "icons"
    if not os.path.exists(icons_dir):
        os.makedirs(icons_dir)
    
    icon_settings = {
        "idle.png": (200, 200, 200),    # 灰色
        "work.png": (255, 50, 50),      # 红色
        "shortRest.png": (50, 200, 50), # 绿色
        "longRest.png": (50, 50, 200)   # 蓝色
    }
    
    for filename, color in icon_settings.items():
        path = os.path.join(icons_dir, filename)
        try:
            img = Image.new('RGBA', (32, 32), color + (255,))
            img.save(path)
            print(f"✓ 已创建图标: {path}")
        except Exception as e:
            print(f"✗ 创建图标失败: {path} - {e}")

def fix_common_issues():
    """修复常见问题"""
    print("开始修复常见问题...")
    
    check_translation_files()
    create_default_icons()
    
    print("修复完成。请重启应用以应用更改。")

if __name__ == "__main__":
    fix_common_issues()
