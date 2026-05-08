import tkinter as tk
import random
import math
import time
import threading

# 全局变量：控制窗口实例、返回速度配置
control_root = None
RETURN_STEPS = 20  # 返回步数（越小越快，建议10-50）
STEP_INTERVAL = 0.008  # 每步间隔（越小越快，建议0.005-0.02）

def get_heart_points(count, screen_width, screen_height, scale=25):
    points = []
    for i in range(count):
        ratio = i / (count - 1)
        if ratio < 0.5:
            t = math.pi * (2 * ratio) ** 1.2
        else:
            t = math.pi + math.pi * (2 * (ratio - 0.5)) ** 0.8
        x = 16 * math.pow(math.sin(t), 3)
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        center_x = screen_width // 2
        center_y = screen_height // 2
        point_x = center_x + x * scale
        point_y = center_y - (y + 2) * scale
        points.append((int(point_x), int(point_y)))
    return points

def show_warm_tip(pos, root, window_list):
    window = tk.Toplevel(root)
    window.update_idletasks()
    x, y = pos
    window_width = 200
    window_height = 40
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = max(0, min(x, screen_width - window_width))
    y = max(0, min(y, screen_height - window_height))
    window.title('温馨提示')
    window.geometry(f"{window_width}x{window_height}+{x}+{y}")
    tips = [
        '多喝水哦~', '保持微笑呀', '每天都要元气满满',
        '记得吃水果', '保持好心情', '好好爱自己', '我想你了',
        '梦想成真', '期待下一次见面', '金榜题名',
        '顺顺利利', '早点休息', '愿所有烦恼都消失',
        '别熬夜', '今天过得开心嘛', '天冷了，多穿衣服'
    ]
    tip = random.choice(tips)
    bg_colors = [
        'lightpink', 'skyblue', 'lightgreen', 'lavender',
        'lightyellow', 'plum', 'coral', 'bisque', 'aquamarine'
    ]
    bg = random.choice(bg_colors)
    label = tk.Label(
        window,
        text=tip,
        bg=bg,
        font=('微软雅黑', 14),
        width=20,
        height=2
    )
    label.pack()
    label.update_idletasks()
    window.attributes('-topmost', True)
    window_list.append((window, x, y))  # 存储：窗口实例、初始x、初始y
    return window

def spread_windows_instantly(window_list, screen_width, screen_height):
    time.sleep(1)
    window_width = 200
    window_height = 40
    for window, _, _ in window_list:
        target_x = random.randint(0, screen_width - window_width)
        target_y = random.randint(0, screen_height - window_height)
        window.geometry(f"{window_width}x{window_height}+{target_x}+{target_y}")
        window.update()

def return_windows_smoothly(window_list):
    """可调速的平滑返回功能"""
    for step in range(RETURN_STEPS):
        for window, orig_x, orig_y in window_list:
            if window.winfo_exists():  # 确保窗口未被关闭
                curr_geo = window.geometry().split('+')
                curr_x = int(curr_geo[1])
                curr_y = int(curr_geo[2])
                move_x = (orig_x - curr_x) / RETURN_STEPS
                move_y = (orig_y - curr_y) / RETURN_STEPS
                new_x = int(curr_x + move_x)
                new_y = int(curr_y + move_y)
                window.geometry(f"200x40+{new_x}+{new_y}")
                window.update()
        time.sleep(STEP_INTERVAL)

def clear_all_windows(window_list):
    """一键清空所有提示窗口"""
    for window, _, _ in window_list[:]:  # 遍历副本，避免删除时索引异常
        if window.winfo_exists():
            window.destroy()
    window_list.clear()  # 清空列表

def create_control_window(window_list):
    """控制窗口：包含返回、清空按钮"""
    global control_root
    control_root = tk.Tk()
    control_root.title('控制中心')
    control_root.geometry('220x120')
    control_root.attributes('-topmost', True)
    
    # 手动返回按钮
    return_btn = tk.Button(
        control_root,
        text='返回爱心形状',
        font=('微软雅黑', 12),
        bg='lightcoral',
        fg='white',
        command=lambda: threading.Thread(
            target=return_windows_smoothly,
            args=(window_list,),
            daemon=True
        ).start()
    )
    return_btn.pack(pady=5)
    
    # 一键清空按钮
    clear_btn = tk.Button(
        control_root,
        text='一键清空窗口',
        font=('微软雅黑', 12),
        bg='lightblue',
        fg='white',
        command=lambda: clear_all_windows(window_list)
    )
    clear_btn.pack(pady=5)
    
    control_root.mainloop()

def exit_program(root, window_list):
    """ESC键退出：关闭所有窗口"""
    clear_all_windows(window_list)  # 复用清空功能
    if control_root:
        control_root.destroy()
    root.destroy()
    exit()

if __name__ == "__main__":
    num_windows = 110
    root = tk.Tk()
    root.withdraw()
    
    # 绑定ESC键退出
    root.bind('<Escape>', lambda e: exit_program(root, window_list))
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    heart_points = get_heart_points(num_windows, screen_width, screen_height)
    window_list = []

    # 创建爱心窗口
    for i, pos in enumerate(heart_points):
        show_warm_tip(pos, root, window_list)
        time.sleep(0.08)
        if i % 5 == 0:
            root.update()

    # 启动散开线程
    spread_thread = threading.Thread(
        target=spread_windows_instantly,
        args=(window_list, screen_width, screen_height),
        daemon=True
    )
    spread_thread.start()

    # 启动控制窗口
    control_thread = threading.Thread(
        target=create_control_window,
        args=(window_list,),
        daemon=True
    )
    control_thread.start()

    root.mainloop()