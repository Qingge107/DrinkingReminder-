#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试主程序toast通知功能
"""

from DrinkReminder import WaterReminder
from PyQt5.QtWidgets import QApplication
import sys

def test_main_toast():
    """测试主程序的toast通知功能"""
    app = QApplication(sys.argv)
    
    # 创建主程序实例
    reminder = WaterReminder()
    
    print("测试主程序toast通知功能...")
    
    # 测试toast通知
    reminder.show_toast_safe("测试通知", "这是主程序的测试通知！")
    
    print("✓ 主程序toast通知测试完成")
    print("请检查是否收到了Windows系统通知")
    
    # 关闭程序
    app.quit()

if __name__ == "__main__":
    test_main_toast() 