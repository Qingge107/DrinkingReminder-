import sys
import json
import os
import winreg
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSpinBox, QMessageBox, QCheckBox
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon

# 尝试导入不同的toast通知库
try:
    from winotify import Notification, audio
    TOAST_LIBRARY = "winotify"
except ImportError:
    try:
        from win10toast_click import ToastNotifier
        TOAST_LIBRARY = "win10toast_click"
    except ImportError:
        try:
            import subprocess
            TOAST_LIBRARY = "powershell"
        except:
            TOAST_LIBRARY = "none"

DATA_FILE = os.path.join(os.path.dirname(sys.argv[0]), "water_data.json")

class WaterReminder(QWidget):
    def __init__(self):
        super().__init__()
        self.toaster = None
        self.init_toaster()
        self.initUI()
        self.load_data()
        self.init_timer()
    
    def init_toaster(self):
        """初始化 Toast 通知器"""
        try:
            if TOAST_LIBRARY == "winotify":
                icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'water.ico')
                if not os.path.exists(icon_path):
                    icon_path = None
                self.toaster = {"type": "winotify", "icon": icon_path}
            elif TOAST_LIBRARY == "win10toast_click":
                self.toaster = {"type": "win10toast_click", "instance": ToastNotifier()}
            elif TOAST_LIBRARY == "powershell":
                self.toaster = {"type": "powershell"}
            else:
                self.toaster = None
                print("警告：未找到可用的toast通知库")
        except Exception as e:
            print(f"Toast 初始化失败: {str(e)}")
            self.toaster = None

    def show_toast_safe(self, title, message, duration=5):
        """安全地显示 Toast 通知"""
        try:
            if self.toaster is None:
                self.init_toaster()
            
            if self.toaster is None:
                QMessageBox.information(self, title, message)
                return
            
            if self.toaster["type"] == "winotify":
                # winotify 只接受 'short' 或 'long'
                duration_str = "long" if duration and duration >= 8 else "short"
                
                # 构建通知参数
                notification_params = {
                    "app_id": "喝水助手",
                    "title": title,
                    "msg": message,
                    "duration": duration_str
                }
                
                # 只有当图标存在时才添加icon参数
                if self.toaster["icon"]:
                    notification_params["icon"] = self.toaster["icon"]
                
                toast = Notification(**notification_params)
                toast.set_audio(audio.Default, loop=False)
                toast.show()
                
            elif self.toaster["type"] == "win10toast_click":
                self.toaster["instance"].show_toast(
                    title,
                    message,
                    duration=duration,
                    threaded=True
                )
                
            elif self.toaster["type"] == "powershell":
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
                [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

                $template = @"
                <toast>
                    <visual>
                        <binding template="ToastGeneric">
                            <text>{title}</text>
                            <text>{message}</text>
                        </binding>
                    </visual>
                </toast>
"@

                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($template)
                $toast = New-Object Windows.UI.Notifications.ToastNotification $xml
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("喝水助手").Show($toast)
                '''
                subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
                
        except Exception as e:
            print(f"显示通知失败: {str(e)}")
            try:
                QMessageBox.information(self, title, message)
            except:
                pass

    def initUI(self):
        self.setWindowTitle("喝水助手")
        self.resize(600, 400)
        
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'water.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        layout = QVBoxLayout()

        self.target_label = QLabel("今日目标 (ml):")
        self.target_spin = QSpinBox()
        self.target_spin.setRange(100, 50000)
        self.target_spin.setValue(2000)

        self.interval_label = QLabel("提醒间隔 (分钟):")
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(5, 180)
        self.interval_spin.setValue(30)

        self.progress_label = QLabel("已喝水: 0 ml")
        self.drink_btn = QPushButton("喝水 +200ml")
        self.drink_btn.clicked.connect(self.drink_water)
        self.drink_btn.clicked.connect(self.notice)

        self.save_btn = QPushButton("保存设置")
        self.save_btn.clicked.connect(self.save_settings)

        # 新增重置按钮
        self.reset_btn = QPushButton("重置目标和喝水量")
        self.reset_btn.clicked.connect(self.reset_data)

        # 添加开机自启动选项
        self.autostart_checkbox = QCheckBox("开机自动启动")
        self.autostart_checkbox.setChecked(self.is_autostart_enabled())
        self.autostart_checkbox.stateChanged.connect(self.toggle_autostart)

        layout.addWidget(self.target_label)
        layout.addWidget(self.target_spin)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_spin)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.drink_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.reset_btn)  # 添加重置按钮到布局
        layout.addWidget(self.autostart_checkbox)
        self.setLayout(layout)

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.show_notification)
        self.timer.start(self.interval_spin.value() * 60 * 1000)

    def show_notification(self):
        self.show_toast_safe(
            "喝水提醒",
            "该喝水啦！保持健康哦~"
        )

    def drink_water(self):
        self.data["drank"] += 200
        self.progress_label.setText(f"已喝水: {self.data['drank']} ml")
        self.save_data()
        
        if self.data["drank"] >= self.data["target"]:
            QMessageBox.information(self, "恭喜", "今日喝水目标已达成！")
            self.show_toast_safe("恭喜", "今日喝水目标已达成！")

    def notice(self):
        self.show_toast_safe(
            "今日喝水",
            f"今日喝水量:{self.data['drank']}ml"
        )

    def save_settings(self):
        self.data["target"] = self.target_spin.value()
        self.data["interval"] = self.interval_spin.value()
        self.save_data()
        self.timer.start(self.data["interval"] * 60 * 1000)
        self.show_toast_safe(
            "喝水助手",
            f"今日喝水目标已设定为 {self.data['target']} ml，间隔 {self.data['interval']} 分钟。"
        )
        QMessageBox.information(self, "保存成功", "设置已保存！")

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        else:
            self.data = {"target": 2000, "drank": 0, "interval": 30}
        self.target_spin.setValue(self.data["target"])
        self.interval_spin.setValue(self.data["interval"])
        self.progress_label.setText(f"已喝水: {self.data['drank']} ml")

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False)

    def is_autostart_enabled(self):
        """检查是否已启用开机自启动"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ
            )
            winreg.QueryValueEx(key, "喝水助手")
            winreg.CloseKey(key)
            return True
        except WindowsError:
            return False

    def toggle_autostart(self, state):
        """切换开机自启动状态"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_ALL_ACCESS
            )

            if state:
                # 获取当前程序的完整路径
                app_path = os.path.abspath(sys.argv[0])
                if app_path.endswith('.py'):
                    # 如果是 .py 文件，使用 pythonw 来运行（无控制台窗口）
                    command = f'pythonw "{app_path}"'
                else:
                    # 如果是可执行文件，直接运行
                    command = f'"{app_path}"'
                
                winreg.SetValueEx(key, "喝水助手", 0, winreg.REG_SZ, command)
                QMessageBox.information(self, "成功", "已添加到开机启动项！")
            else:
                winreg.DeleteValue(key, "喝水助手")
                QMessageBox.information(self, "成功", "已从开机启动项移除！")

            winreg.CloseKey(key)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"设置开机自启动失败：{str(e)}")

        self.autostart_checkbox.setChecked(self.is_autostart_enabled())
    
    def reset_data(self):
        """重置喝水目标和喝水量"""
        self.data = {"target": 2000, "drank": 0, "interval": 30}
        self.target_spin.setValue(self.data["target"])
        self.interval_spin.setValue(self.data["interval"])
        self.progress_label.setText(f"已喝水: {self.data['drank']} ml")
        self.save_data()
        self.show_toast_safe("重置成功", "喝水目标和喝水量已重置！")
        QMessageBox.information(self, "重置成功", "喝水目标和喝水量已重置！")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WaterReminder()
    window.show()
    sys.exit(app.exec_())