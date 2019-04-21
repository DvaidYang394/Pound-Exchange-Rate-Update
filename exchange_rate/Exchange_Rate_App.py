# -*- coding: utf-8 -*-
__author__ = "Ziqi Yang"
import wx,wx.adv
import threading
import get_data
import os
import ctypes,ctypes.wintypes
import win32con,win32api,win32gui

hwnd = win32gui.GetForegroundWindow()
win32gui.SetWindowText(hwnd,"Exchange_Rate_App")
hide_mode = False
notice_mode = 0

class MyHotKey(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        user32 = ctypes.windll.user32
        while(True):
            user32.RegisterHotKey(None, 98, win32con.MOD_SHIFT|win32con.MOD_WIN,0x42)
            try:
                msg = ctypes.wintypes.MSG()
                if user32.GetMessageA(ctypes.byref(msg), None, 0, 0) != 0:
                    if msg.message == win32con.WM_HOTKEY:
                        if msg.wParam == 98:
                            global hide_mode
                            if(hide_mode == False):
                                hide_mode = True
                                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                            else:
                                hide_mode = False
                                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                                win32gui.SetActiveWindow(hwnd)
                                win32gui.SetForegroundWindow(hwnd)
                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageA(ctypes.byref(msg))
            finally:
                del msg
                user32.UnregisterHotKey(None, 98)

hotkey_task = MyHotKey(1,"hotkey_task",2)

class MyTaskGetData(threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        get_data.cui()

cui_task = MyTaskGetData(1, "MyTaskGetData", 1)
        
class MyTaskBarIcon(wx.adv.TaskBarIcon):
    ICON = "logo.ico"  # 图标地址
    ID_ABOUT = wx.NewId()  # 菜单选项“关于”的ID
    ID_EXIT = wx.NewId()  # 菜单选项“退出”的ID
    ID_CUI = wx.NewId()  # 菜单选项“显示页面”的ID
    ID_NOTICE = wx.NewId() # 菜单选项“通知开关”的ID
    TITLE = "汇率变动提示" #鼠标移动到图标上显示的文字

    def __init__(self):
        wx.adv.TaskBarIcon.__init__(self)
        self.SetIcon(wx.Icon(self.ICON), self.TITLE)  # 设置图标和标题
        self.Bind(wx.EVT_MENU, self.onAbout, id=self.ID_ABOUT)  # 绑定“关于”选项的点击事件
        self.Bind(wx.EVT_MENU, self.onNotice, id=self.ID_NOTICE)  # 绑定“关于”选项的点击事件
        self.Bind(wx.EVT_MENU, self.onExit, id=self.ID_EXIT)  # 绑定“退出”选项的点击事件
        self.Bind(wx.EVT_MENU, self.onCUI, id=self.ID_CUI)  # 绑定“显示页面”选项的点击事件
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDclick) # 绑定托盘图标双击事件

    # “显示页面”选项的事件处理器
    def onCUI(self, event):
        global hide_mode
        if(hide_mode == False):
            hide_mode = True
            win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        else:
            hide_mode = False
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            win32gui.SetActiveWindow(hwnd)
            win32gui.SetForegroundWindow(hwnd)

    def OnTaskBarLeftDclick(self,event):
        self.onCUI(event)

    # “关于”选项的事件处理器
    def onAbout(self, event):
        win32api.MessageBox(0, "程序作者：Ziqi Yang\n最后更新日期：2019-3-16", "关于", win32con.MB_ICONASTERISK)

    # “退出”选项的事件处理器
    def onExit(self, event):
        os._exit(0)

    def onNotice(self, event):
        global notice_mode
        if(notice_mode == 1):
            notice_mode = 0
        else:
            notice_mode = 1

    # 创建菜单选项
    def CreatePopupMenu(self):
        menu = wx.Menu()
        for mentAttr in self.getMenuAttrs():
            menu.Append(mentAttr[1], mentAttr[0])
        return menu

    # 获取菜单的属性元组
    def getMenuAttrs(self):
        global hide_mode
        global notice_mode
        if(hide_mode == 0):
            str_CUI = "隐藏主界面(Win+Shift+B)"
        else:
            str_CUI = "显示主界面(Win+Shift+B)"

        if(notice_mode == 1):
            str_Notice = "关闭变动通知"
        else:
            str_Notice = "开启变动通知"

        return [(str_CUI, self.ID_CUI),
                ("关于", self.ID_ABOUT),
                ("退出", self.ID_EXIT)]

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self)
        MyTaskBarIcon()#显示系统托盘图标
        cui_task.start()
        hotkey_task.start()

class MyApp(wx.App):
    def OnInit(self):
        MyFrame()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()