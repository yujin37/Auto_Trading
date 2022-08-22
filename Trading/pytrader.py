import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from Kiwoom import *
import time
# pymon 추가
from pandas import DataFrame
import datetime
import re
MARKET_KOSPI = 0
MARKET_KOSDAQ = 10

# ui 파일을 불러오는 코드
form_class = uic.loadUiType("pytrader.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.trade_stocks_done = False

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        self.timer2 = QTimer(self)
        self.timer2.start(1000 * 10)
        self.timer2.timeout.connect(self.timeout2)

        accouns_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")

        accounts_list = accounts.split(';')[0:accouns_num]
        self.comboBox.addItems(accounts_list)

        self.lineEdit.textChanged.connect(self.code_changed)

        self.pushButton.clicked.connect(self.send_order)  # 주문
        self.pushButton_2.clicked.connect(self.check_balance)
        self.pushButton_3.clicked.connect(self.auto_run)  # 자동매수 프로그램
        self.pushButton_6.clicked.connect(self.load_buy_sell_list)  # 자동매매 선정 리스트
        self.pushButton_7.clicked.connect(self.notTrade)  # 미체결현황
        self.pushButton_7.clicked.connect(self.Trade)  # 체결현황

        self.load_buy_sell_list()  # 기본적인 자동매매 선정리스트 세팅


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
        # time.sleep(0.5)

        df = DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                       index=self.kiwoom.ohlcv['date'])
        return df

    # 급등주 포착 알고리즘, 매수
    def check_speedy_rising_volume(self, code):
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = self.get_ohlcv(code, today)
        volumes = df['volume']

        if len(volumes) < 11:
            return False

        sum_vol20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif 1 <= i <= 10:
                sum_vol20 += vol
            else:
                break

        avg_vol20 = sum_vol20 / 10
        if today_vol > avg_vol20 * 5:
            return True

    def check_up(self):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            # time.sleep(0.5)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")
        item_count = len(self.kiwoom.opw00018_output['multi'])

        sell_list = []
        sell_lists = []
        #print('아이템 진입')
        for j in range(item_count): #이건 아이템 전체 줄
            row = self.kiwoom.opw00018_output['multi'][j]#여기는 각 줄에 대한 내용
            type_code = row[0]
            name = row[1] #종목명
            profit = row[6] #수익률

            if float(profit)>(-10.0): #이건 작동 여부 위해서 설정한 거고 필요에 따라 변경

                sell_list.append(type_code)

        for i in sell_list: #이 주식 번호에서 쉼표 제거 부분
            n = re.sub(",", "", i)
            sell_lists.append(n)

        print(sell_lists) #확인 용

        self.update_sell_list(sell_lists)
        time.sleep(0.5)
        self.trade_stocks_done = False
        self.timeout()
        return True

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

    # 자동매매 자동 호출 시스템
    def auto_run(self):
        buy_list = []
        num = len(self.kosdaq_codes)
        #sell_list = []
        for i, code in enumerate(self.kosdaq_codes):
            print(i, '/', num)
            # 매수 알고리즘
            if self.check_speedy_rising_volume(code):
                buy_list.append(code)
                # 확인 차원 출력, 나중에 삭제 예정
                print("급등주: ", code)
                print('타입', type(code))
                self.update_buy_list(buy_list)
                time.sleep(0.5)
                self.trade_stocks_done = False
                self.timeout()
            buy_list.clear()
            time.sleep(3.6)
            # 매도 알고리즘
            if self.check_up():
                print("여기") #이것도 실행 되는지 보려고

            time.sleep(3.6)


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
                # print("매수 전 진입") #정상적으로 한번 진입하는 것을 확인
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
                #print("매도 전 진입")
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
                #item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_3.setItem(j, i, item)

        # sell list
        for j in range(len(sell_list)):
            row_data = sell_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rstrip())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                #item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_3.setItem(len(buy_list) + j, i, item)

        self.tableWidget_3.resizeRowsToContents()

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

    # 타임아웃 코드
    def timeout(self):
        # 여기까지는 진입하는데.....
        market_start_time = QTime(9, 0, 0) #장오픈
        market_end_time = QTime(15, 30, 0) #장마감
        current_time = QTime.currentTime()
        if current_time > market_start_time and current_time<market_end_time and self.trade_stocks_done == False: #장시간에만
        #if current_time > market_start_time and self.trade_stocks_done == False: #이건 실험용
            self.trade_stocks()  # 여기가 안되는 것 같다.
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

    # 정보 작성?
    def check_balance(self):
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:
            # time.sleep(0.5)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i - 1])
            # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.tableWidget.setItem(0, i, item)

        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()

    # 미체결 현황 조회, nt_list.txt, 이제 주문 들어가면 미체결, 체결 알림시 삭제
    def notTrade(self):
        print('not trade 진입')

    #체결 현황 조회, t_list.txt, 체결 알림이 뜨게 되면 추가를 해줌. 날짜 다르면 삭제 기능도?
    def Trade(self):
        time.sleep(5)
        print('trade 진입')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()