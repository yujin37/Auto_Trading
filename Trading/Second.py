from PyQt5 import uic
from Kiwoom import *

#차트 조회를 위한
import FinanceDataReader as fdr
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

form_class2 = uic.loadUiType("second.ui")[0]
#분봉 차트 하는 것도 나중에 수정하기
#차트 조회 창
class SecondWindow(QDialog, form_class2):
    def __init__(self):
        super(SecondWindow, self).__init__()
        self.initUI()
        self.find.clicked.connect(self.plot)
        self.show()

    def initUI(self):
        self.setupUi(self)
        self.fig=plt.Figure()
        self.canvas = FigureCanvas(self.fig)
        #self.home.clicked.connect(self.Home)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.graph_layout.addWidget(self.toolbar)
        self.graph_layout.addWidget(self.canvas)


    def plot(self): #차트에 그래프 그리기
        text=self.code_num.text()
        start_date=self.dateEdit.text()
        end_date=self.dateEdit_2.text()
        df=fdr.DataReader(text,start_date, end_date)

        ax1 = self.fig.add_subplot(1, 1, 1)
        self.graph_layout.addWidget(self.canvas) #이건 x, y축이 겹치는 문제 발생

        if self.checkBox.isChecked():
            ax1.plot(df.index,df['Open'], label='Open', color='blue')
        if self.checkBox_2.isChecked():
            ax1.plot(df.index, df['Close'], label='Close', color='red')
        if self.checkBox_3.isChecked():
            ax1.plot(df.index, df['High'], label='High', color='green')
        if self.checkBox_4.isChecked():
            ax1.plot(df.index, df['Low'], label='Low', color='purple')
        self.canvas.draw()