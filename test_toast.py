#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试toast通知功能的脚本
"""

import sys
import os

# 尝试导入不同的toast通知库
print("正在测试toast通知库...")

try:
    from winotify import Notification, audio
    print("✓ winotify 可用")
    TOAST_LIBRARY = "winotify"
except ImportError as e:
    print(f"✗ winotify 不可用: {e}")
    try:
        from win10toast_click import ToastNotifier
        print("✓ win10toast_click 可用")
        TOAST_LIBRARY = "win10toast_click"
    except ImportError as e:
        print(f"✗ win10toast_click 不可用: {e}")
        try:
            import subprocess
            print("✓ PowerShell 方式可用")
            TOAST_LIBRARY = "powershell"
        except ImportError as e:
            print(f"✗ PowerShell 方式不可用: {e}")
            TOAST_LIBRARY = "none"

def test_toast():
    """测试toast通知功能"""
    print(f"\n使用 {TOAST_LIBRARY} 进行测试...")
    
    try:
        if TOAST_LIBRARY == "winotify":
            # 获取图标路径
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'water.ico')
            if not os.path.exists(icon_path):
                icon_path = None
                print("警告：未找到water.ico文件")
            
            # 构建通知参数
            notification_params = {
                "app_id": "喝水助手测试",
                "title": "测试通知",
                "msg": "这是一个测试通知，如果你看到了这个，说明toast功能正常！",
                "duration": "short"
            }
            
            # 只有当图标存在时才添加icon参数
            if icon_path:
                notification_params["icon"] = icon_path
            
            toast = Notification(**notification_params)
            toast.set_audio(audio.Default, loop=False)
            toast.show()
            print("✓ winotify 通知已发送")
            
        elif TOAST_LIBRARY == "win10toast_click":
            toaster = ToastNotifier()
            toaster.show_toast(
                "测试通知",
                "这是一个测试通知，如果你看到了这个，说明toast功能正常！",
                duration=5,
                threaded=True
            )
            print("✓ win10toast_click 通知已发送")
            
        elif TOAST_LIBRARY == "powershell":
            ps_script = '''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

            $template = @"
            <toast>
                <visual>
                    <binding template="ToastGeneric">
                        <text>测试通知</text>
                        <text>这是一个测试通知，如果你看到了这个，说明toast功能正常！</text>
                    </binding>
                </visual>
            </toast>
"@

            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("喝水助手测试").Show($toast)
            '''
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            print("✓ PowerShell 通知已发送")
            
        else:
            print("✗ 没有可用的toast通知库")
            return False
            
        print("\n请检查是否收到了Windows系统通知。")
        print("如果没有收到通知，请检查：")
        print("1. Windows通知设置是否开启")
        print("2. 是否允许应用程序显示通知")
        print("3. 是否在专注助手模式下")
        
        return True
        
    except Exception as e:
        print(f"✗ 发送通知失败: {e}")
        return False

if __name__ == "__main__":
    print("=== Toast通知功能测试 ===")
    success = test_toast()
    
    if success:
        print("\n✓ 测试完成，请检查是否收到通知")
    else:
        print("\n✗ 测试失败，toast通知功能可能无法正常工作")
    
    input("\n按回车键退出...") 