import ctypes

EnumWindows = ctypes.windll.user32.EnumWindows
EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
GetWindowTextW = ctypes.windll.user32.GetWindowTextW
GetWindowTextLengthW = ctypes.windll.user32.GetWindowTextLengthW
IsWindowVisible = ctypes.windll.user32.IsWindowVisible
SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
ShowWindow = ctypes.windll.user32.ShowWindow

def foreach_window(hwnd, lParam):
    if IsWindowVisible(hwnd):
        length = GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value
        if 'Opera' in title or 'AI Logistics' in title or 'localhost' in title or 'Command Center' in title:
            ShowWindow(hwnd, 9)  # SW_RESTORE
            SetForegroundWindow(hwnd)
            print("Activated:", title)
    return True

EnumWindows(EnumWindowsProc(foreach_window), 0)
