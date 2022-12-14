import sys
from PyQt5.QtWidgets import *
#from PyQt5.QtCore import *
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from Kiwoom import *
import time
# pymon 추가
from pandas import DataFrame
from datetime import datetime, timedelta,date
import re
import pandas as pd
MARKET_KOSPI = 0
MARKET_KOSDAQ = 10
from Second import *
from Third import *
import csv


# ui 파일을 불러오는 코드
form_class = uic.loadUiType("pytrader.ui")[0]

#메인 창
class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.trade_stocks_done = False

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()
        self.Search()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        self.timer2 = QTimer(self)
        self.timer2.start(1000 * 10)
        self.timer2.timeout.connect(self.timeout2)
        #조건식 타이머
        self.timer3 = QTimer(self)
        self.timer3.start(500)
        self.timer3.timeout.connect(self.timeout3)

        accouns_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")

        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox.addItems(accounts_list)

        self.lineEdit.textChanged.connect(self.code_changed)

        self.pushButton.clicked.connect(self.send_order)  # 주문
        self.pushButton_2.clicked.connect(self.check_balance)
        self.pushButton_3.clicked.connect(self.clear_line) #내용 초기화
        self.pushButton_4.clicked.connect(self.Chart) #차트 조회
        self.pushButton_5.clicked.connect(self.Search) #조건검색 새로고침
        self.pushButton_6.clicked.connect(self.load_buy_sell_list)  # 자동매매 선정 리스트
        self.pushButton_7.clicked.connect(self.Join_search) #조건검색 후 주문 적용
        self.pushButton_8.clicked.connect(self.Code_info)
        self.pushButton_9.clicked.connect(self.check_volume) #과거 데이터 계산
        self.pushButton_10.clicked.connect(self.Candle) #캔들스틱 차트 창 이동
        self.pushButton_11.clicked.connect(self.percent_buy)
        self.pushButton_12.clicked.connect(self.percent_sell)

        self.load_buy_sell_list()  # 기본적인 자동매매 선정리스트 세팅


        self.textch=""

    # 코드 리스트 받아오기
    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}

        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                       index=self.kiwoom.ohlcv['date'])
        return df

    def update_buy_list(self, buy_list):
        f = open("buy_list.txt", "a+", encoding='utf-8')
        for code in buy_list:
            line = "매수;" + code + ";시장가;1;0;매수전" + "\n"
            f.writelines(line)
        f.close()
    def update_sell_list(self, sell_list):
        f = open("sell_list.txt", "a+", encoding='utf-8')
        for code in sell_list:
            line = "매도;" + code + ";시장가;1;0;매도전" + "\n"
            f.writelines(line)
        f.close()

    # 트레이딩 관련 텍스트 파일 읽어주기
    def trade_stocks(self):
        # print('here1')
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        f = open("buy_list.txt", 'rt', encoding='utf-8')
        buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", 'rt', encoding='utf-8')
        sell_list = f.readlines()
        f.close()

        # account
        account = self.comboBox.currentText()

        # buy list
        for row_data in buy_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]
            buy = split_row_data[5].strip()
            time.sleep(0.5)
            if buy == '매수전':
                self.kiwoom.send_order("send_order_req", "0101", account, 1, code, num, price, hoga_lookup[hoga], "")
        # sell list
        for row_data in sell_list:
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]
            sell = split_row_data[5].strip()
            time.sleep(0.5)

            if sell == '매도전':
                self.kiwoom.send_order("send_order_req", "0101", account, 2, code, num, price, hoga_lookup[hoga], "")
        # buy list
        for i, row_data in enumerate(buy_list):
            buy_list[i] = buy_list[i].replace("매수전", "주문완료")
            self.trade_stocks_done = False
        #sell list
        for i, row_data in enumerate(sell_list):
            sell_list[i] = sell_list[i].replace("매도전", "주문완료")
            self.trade_stocks_done = False

        # file update
        f = open("buy_list.txt", 'wt', encoding='utf-8')
        for row_data in buy_list:
            f.write(row_data)
        f.close()

        # file update
        f = open("sell_list.txt", 'wt', encoding='utf-8')
        for row_data in sell_list:
            f.write(row_data)
        f.close()

    # 트레이딩 관련 파일 로드
    def load_buy_sell_list(self):
        f = open("buy_list.txt", 'rt', encoding='utf-8')
        buy_list = f.readlines()
        f.close()

        f = open("sell_list.txt", 'rt', encoding='utf-8')
        sell_list = f.readlines()
        f.close()

        row_count = len(buy_list) + len(sell_list)
        self.tableWidget_3.setRowCount(row_count)

        for j in range(len(buy_list)):
            row_data = buy_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rsplit())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                self.tableWidget_3.setItem(j, i, item)
        time.sleep(0.5)

        # sell list
        for j in range(len(sell_list)):
            row_data = sell_list[j]

            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1])

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                self.tableWidget_3.setItem(len(buy_list) + j, i, item)

        self.tableWidget_3.resizeRowsToContents()
    #수동주문관련 도움
    def code_changed(self):
        code = self.lineEdit.text()
        name = self.kiwoom.get_master_code_name(code)
        self.lineEdit_2.setText(name)

    # 주문 전송
    def send_order(self):
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4}
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()
        code = self.lineEdit.text()
        hoga = self.comboBox_3.currentText()
        num = self.spinBox.value()
        price = self.spinBox_2.value()

        self.kiwoom.send_order("send_order_req", "0101", account, order_type_lookup[order_type], code, num, price,
                               hoga_lookup[hoga], "")

    # 주문하는동안 확인
    def timeout(self):
        market_start_time = QTime(9, 0, 0) #장오픈
        market_end_time = QTime(15, 30, 0) #장마감
        current_time = QTime.currentTime()

        if current_time > market_start_time and current_time<market_end_time and self.trade_stocks_done == False: #장시간에만
            self.trade_stocks()
            self.trade_stocks_done = True

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

    # 체크박스 타임아웃
    def timeout2(self):
        if self.checkBox.isChecked():
            self.check_balance()
    #잔고조회 스레드 라인
    def check_balance(self):
        time.sleep(0.5)
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        self.tableWidget.setItem(0, 0, item)
        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
            self.tableWidget.setItem(0, i, item)

        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])

                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()

    def GetCommRealData(self, code, fid):
        data = self.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid)
        return data

    def Chart(self): #차트 조회를 위한 새 창 열기
        self.second=SecondWindow()
    #조건식 검색
    def Search(self):
        print("pytrader.py [load_condition_list]")
        cond_list=[]
        try:
            self.kiwoom.GetConditionLoad()
            dic = self.kiwoom.condition

            for key in dic.keys():
                cond_list.append("{};{}".format(key, dic[key]))
            self.comboBox_4.addItems(cond_list)
        except Exception as e:
            print(e)


    #조건식 실제 매수매도 진행시 able, enable
    def Join_search(self):
        c_index = self.comboBox_4.currentText().split(';')[0]
        c_name = self.comboBox_4.currentText().split(';')[1]
        if self.pushButton_7.text() == '적용':
            try:
                self.kiwoom.sendCondition("0", c_name, int(c_index), 1)
                self.pushButton_7.setText('해제')
                self.comboBox_4.setEnabled(False)
                self.checkBox_2.setEnabled(False)
                self.checkBox_3.setEnabled(False)
                print("{} activiated".format(c_name))
            except Exception as e:
                print(e)
        else:
            self.kiwoom.sendConditionStop("0",c_name, c_index)
            self.comboBox_4.setEnabled(True)
            self.checkBox_2.setEnabled(True)
            self.checkBox_3.setEnabled(True)
            self.pushButton_7.setText('적용')
    #조건식 진행시 사용하는 타임아웃
    def timeout3(self):
        if self.kiwoom.msg:
            self.textEdit.append(self.kiwoom.msg)
            self.kiwoom.msg = ""
            get = self.kiwoom.msg_line
            if self.checkBox_2.isChecked():
                self.update_sell_list(get)
            elif self.checkBox_3.isChecked():
                self.update_buy_list(get)
            else:
                pass
            get.clear()
            time.sleep(0.5)
            self.trade_stocks_done = False
            self.timeout()
    #조건식 관련해서 출력내용 지우기
    def clear_line(self):
        self.textEdit.clear()
    #종목 검색 후 정보 출력
    def Code_info(self):
        name = self.lineEdit_3.text()
        print(name)
        code = 0
        file = open('code_name.csv','r', encoding='utf-8')
        rdr = csv.reader(file)
        for line in rdr:
            if name == line[1]:
                code = line[0]
        print(code)
        self.textEdit_2.clear()
        if code == 0:
            self.textch += "해당 종목의 코드가 없습니다."
            self.textEdit_2.append(self.textch)
            self.textch = ""
        else:
            self.textEdit_2.append(code)

            weekday=date.today().weekday()
            days=['월','화','수','목','금','토','일']
            if weekday==5:
                todays=date.today()-timedelta(days=1)
            elif weekday==6:
                todays = date.today() - timedelta(days=2)
            else:
                todays = date.today()
            todays=str(todays)
            todays2=datetime.strptime(todays,"%Y-%m-%d")
            weekday=days[todays2.weekday()]
            print(todays, weekday)
            self.textEdit_2.append('오늘의 날짜(장 날짜 기준)\n'+ str(todays) + ' ' + weekday)
            df = fdr.DataReader(str(code), str(todays), str(todays))
            print(df) #현재 장 정보 확인
            text1 = df.loc[str(todays),'Open']
            text1=str(int(text1))
            self.textEdit_2.append('오픈가: '+text1)
            text2 = df.loc[str(todays), 'High']
            text2 = str(int(text2))
            self.textEdit_2.append('최고가: ' + text2)
            text3 = df.loc[str(todays), 'Low']
            text3 = str(int(text3))
            self.textEdit_2.append('최저가: ' + text3)
            text4 = df.loc[str(todays), 'Volume']
            text4 = str(int(text4))
            self.textEdit_2.append('거래량: ' + text4)
            text5 = df.loc[str(todays), 'Change']
            text5 = str(int(text5*100))
            self.textEdit_2.append('변동율: ' + text5 + ' %')
    def percent_buy(self):
        code = self.lineEdit_4.text()
        percent = self.lineEdit_5.text()
        price = self.lineEdit_8.text()
        size = self.lineEdit_9.text()
        result = int(price) + int(price)*(int(percent)/100) #매수 가격 정하기
        f = open("buy_list.txt", "a+", encoding='utf-8')
        line = "매수;" + code + ";지정가;"+size+";"+str(int(result))+";매수전" + "\n"
        f.writelines(line)
        f.close()
        time.sleep(0.5)
        self.trade_stocks_done = False
        self.timeout()
        print(line)


    def percent_sell(self):
        code = self.lineEdit_4.text()
        percent = self.lineEdit_5.text()
        size = self.lineEdit_9.text()
        print(code, percent)
        #수익률 가져오기
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")
        while self.kiwoom.remained_data:
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")


        item_count = len(self.kiwoom.opw00018_output['multi'])
        earn=0
        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            if code == row[0]:
                earn = row[6] #이걸로 접근되면 해서
                break
            else:
                earn = 0
        if earn == 0:
            print('존재하지 않음.')
            print(code, earn)
        else:

            if int(percent) <= int(earn): #기준점 넘었으면 현재가로 주문 넣기
                f = open("sell_list.txt", "a+", encoding='utf-8')
                line = "매도;" + code + ";시장가;" + size + ";" + "0" + ";매도전" + "\n"
                f.writelines(line)
                f.close()
                time.sleep(0.5)
                self.trade_stocks_done = False
                self.timeout()
                #print(line)
            else: #만약 기준점 안넘은 상태면 원하는 이익률로 주문 넣기
                price = int(row[3]) + int(row[3])*(int(percent)/100) #매수 가격 정하기
                f = open("sell_list.txt", "a+", encoding='utf-8')
                line = "매도;" + code + ";지정가;" + size + ";" + str(price) + ";매도전" + "\n"
                f.writelines(line)
                f.close()
                time.sleep(0.5)
                self.trade_stocks_done = False
                self.timeout()

            print('여긴 주문영역')

        print(code, earn)

    #거래량을 이용한 매매 동향 파악 VR(Volume Ratio)
    def check_volume(self):
        code = self.lineEdit_6.text()
        date_cnt = self.lineEdit_10.text()
        #날짜 가져오기
        todays1 = date.today()-timedelta(days=int(date_cnt))
        todays2 = date.today()
        df = fdr.DataReader(str(code), str(todays1), str(todays2))

        up = 0 #상승장
        down = 0 #하락장

        before = df.iloc[0, 3]
        sets = df['Close'].count()

        for i in range(1, sets):
            st = df.iloc[i, 3]
            if int(before) < int(st):
                up += int(st)
            else:
                down += int(st)
            before = st

        vr = (up/down)*100
        vr = round(vr,2)
        self.textEdit_3.append("결과: " + (str(vr)) + " %")

        if vr >= 350:
            self.textEdit_3.append("과열 상태. 무리한 매수 금지")
        elif vr <= 70:
            self.textEdit_3.append("하락장, 매수 고려")
        elif vr >= 100:
            self.textEdit_3.append("상승장")
        else:
            self.textEdit_3.append("하락장")
    #캔들 스틱 차트 조회
    def Candle(self):
        self.third = ThirdWindow()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()