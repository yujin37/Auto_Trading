from PyQt5 import uic
from matplotlib import ticker

from Kiwoom import *
import finplot as fplt
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mplfinance.original_flavor import candlestick2_ohlc
form_class3 = uic.loadUiType("third.ui")[0]


#차트 조회 창
class ThirdWindow(QDialog, form_class3):
    def __init__(self):
        super(ThirdWindow, self).__init__()
        self.kiwoom = Kiwoom()
        self.initUI()
        self.Search.clicked.connect(self.can_graph)
        self.show()

    def initUI(self):
        self.setupUi(self)
        self.fig = plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        # self.home.clicked.connect(self.Home)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.candle_layout.addWidget(self.toolbar)
        self.candle_layout.addWidget(self.canvas)

    def candle_day(self):
        code = self.lineEdit.text()
        date1 = self.dateEdit.text()
        date2 = self.dateEdit_2.text()

        df = fdr.DataReader(code, date1, date2)
        df['MA3']=df['Close'].rolling(3).mean()
        df['MA5'] = df['Close'].rolling(5).mean()
        df['MA10'] = df['Close'].rolling(10).mean()
        df['MA20'] = df['Close'].rolling(20).mean()
        #print(df)
        ax = self.fig.add_subplot(1, 1, 1)
        #ax.axes.xaxis.set_visible(False)
        #ax.axes.yaxis.set_visible(False)
        self.candle_layout.addWidget(self.canvas)  # 이건 x, y축이 겹치는 문제 발생
        index = df.index.astype('str')  # 캔들스틱 x축이 str로 들어감

        # 이동평균선 그리기
        ax.plot(index, df['MA3'], label='MA3', linewidth=0.7)
        ax.plot(index, df['MA5'], label='MA5', linewidth=0.7)
        ax.plot(index, df['MA10'], label='MA10', linewidth=0.7)

        ax.xaxis.set_major_locator(ticker.MaxNLocator(5))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(5))
        candlestick2_ohlc(ax, df['Open'], df['High'],df['Low'], df['Close'],width=0.5, colorup='r', colordown='b')
        ax.legend()
        self.canvas.draw()

    def candle_min(self):
        print("분봉 진입")
        #self.kiwoom.set_input_value("종목코드", code)
        #self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        code = self.lineEdit.text()
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("틱범위", 1)
        self.kiwoom.set_input_value("수정주가구분", 0)
        self.kiwoom.comm_rq_data("opt10080_req", "opt10080", 0, "0102")
        #result = self.kiwoom.opt10080.min_data
        #print(result)
        for i in range(50):
            time.sleep(0.2)
            self.set_input_value("종목코드", code)
            self.set_input_value("틱범위", 1)
            self.set_input_value("수정주가구분", 0)
            self.comm_rq_data("opt10080_req", "opt10080", 2, "1999")

    def can_graph(self):
        if self.radioButton.isChecked():
            self.candle_day()
        elif self.radioButton_2.isChecked():
            self.candle_min()