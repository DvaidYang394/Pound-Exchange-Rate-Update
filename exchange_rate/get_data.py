from bs4 import BeautifulSoup
from urllib import request
from urllib import parse
from Exchange_Rate_App import notice_mode
import subprocess
import os
import time
import win32api,win32con,ctypes
def clear():os.system('cls')

def cui():
    # 数据初始化
    class COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]
    STD_OUTPUT_HANDLE= -11
    price = ['0' for x in range(0,300)]
    update_time = ['0' for x in range(0,300)]
    serial_max = 300
    lowest_price = 9999.9
    highest_price = 0.0
    std_out_handle = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    dwCursorPosition = COORD()
    dwCursorPosition.X = 0
    dwCursorPosition.Y = 0
    # 初始网络连接检查
    url = "http://srh.bankofchina.com/search/whpj/search.jsp"
    Form_Data = {}
    Form_Data['erectDate'] = ''
    Form_Data['nothing'] = ''
    Form_Data['pjname'] = '1314'
    data = parse.urlencode(Form_Data).encode('utf-8')
    while(1):
        try:
            html = request.urlopen(url,data).read()
            break
        except:
            user_choice = win32api.MessageBox(0, "连接超时，请检查网络连接！\n（选择“重试”将重新连接，选择“取消”将退出程序）", "汇率变动提示", win32con.MB_RETRYCANCEL)
            if(user_choice == 2):
                os._exit(0)
    # 初始数据显示
    file = open("data.dat", mode="r+")
    file.seek(0,0)
    total_serial_val = int(file.readline())
    file.seek(6,0)
    for i in range(0,total_serial_val,1):
        price[i] = file.read(6)
        file.read(3)
        update_time[i] = file.read(19)
        file.read(1)
    file.close()

    file = open("data_analysis.dat", mode="r+")
    file.seek(0,0)
    lowest_price = float(file.read(6))
    file.seek(11,0)
    highest_price = float(file.read(6))
    file.close()
    print('\t      最低价       最高价')
    print("             ","%.2f"%lowest_price,"     ","%.2f"%highest_price,"\n")
    print('  \t现汇卖出价\t       更新时间')
    for i in range(0, total_serial_val, 1):
        print('英镑    ', price[i],'\t', update_time[i])
    ctypes.windll.kernel32.SetConsoleCursorPosition(std_out_handle,dwCursorPosition)
    # 循环读取
    while(1):
        # 数据获取
        data = parse.urlencode(Form_Data).encode('utf-8')
        while(1):
            try:
                html = request.urlopen(url,data,timeout = 5).read()
                break
            except:
                user_choice = win32api.MessageBox(0, "连接超时，请检查网络连接！\n（选择“重试”将重新连接，选择“取消”将退出程序）", "汇率变动提示", win32con.MB_RETRYCANCEL)
                if(user_choice == 2):
                    os._exit(0)
        soup = BeautifulSoup(html,'html.parser')
        # 解析数据
        div = soup.find('div', attrs = {'class':'BOC_main publish'})
        table = div.find('table')
        tr = table.find_all('tr')
        td = tr[1].find_all('td')
        current_price = td[3].get_text()
        current_time = td[6].get_text()
        current_price = "%.2f"%float(current_price)
        file = open("data.dat", mode="r+")
        file.seek(0,0)
        total_serial_val = int(file.readline())
        file.seek(6,0)
        for i in range(0,total_serial_val,1):
            price[i] = file.read(6)
            file.read(3)
            update_time[i] = file.read(19)
            file.read(1)
        file.close()
        if (current_price != price[0]) and (current_time != update_time[0]):
            for i in range(serial_max - 1,0,-1):
                price[i] = price[i - 1]
                update_time[i] = update_time[i - 1]
            price[0] = current_price
            update_time[0] = current_time
            file = open("data.dat", mode="r+")
            file.seek(0,0)
            current_line_data = file.readline()
            total_serial_val = int(current_line_data)+1
            if(total_serial_val > serial_max):
                total_serial_val = serial_max
            total_serial_str = '%d' %total_serial_val
            file.seek(0,0)
            file.write(total_serial_str)
            file.close()
            file = open("data.dat", mode="r+")
            file.seek(6,0)
            for i in range(0,total_serial_val,1):
                file.writelines([price[i], "   ", update_time[i], "\n"])
            file.close()
            file = open("data_analysis.dat", mode="r+")
            file.seek(0,0)
            lowest_price = float(file.read(6))
            file.read(5)
            highest_price = float(file.read(6))
            if(float(price[0]) < lowest_price):
                lowest_price = float(price[0])
            if(float(price[0]) > highest_price):
                highest_price = float(price[0])
            file.seek(0,0)
            file.write('%.2f' %lowest_price)
            file.seek(11,0)
            file.write('%.2f' %highest_price)
            file.close()
            clear()
            print('\t      最低价       最高价')
            print("             ","%.2f"%lowest_price,"     ","%.2f"%highest_price,"\n")
            print('  \t现汇卖出价\t       更新时间')
            for i in range(0, total_serial_val, 1):
                print('英镑    ', price[i],'\t', update_time[i])
            ctypes.windll.kernel32.SetConsoleCursorPosition(std_out_handle,dwCursorPosition)
            global notice_mode
            if(notice_mode == 1):
                if(price[0]>price[1]):
                    win32api.MessageBox(0, "汇率上升至%s，时间：%s"%(price[0],update_time[0]), "汇率变动提示", win32con.MB_ICONASTERISK)
                else:
                    if(price[0]<=price[1]):
                        win32api.MessageBox(0, "汇率下降至%s，时间：%s"%(price[0],update_time[0]), "汇率变动提示", win32con.MB_ICONASTERISK)
            time.sleep(3)