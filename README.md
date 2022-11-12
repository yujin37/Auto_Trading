# Auto_Trading
CodeCure 개발팀 X 같이가치투자 \
주식자동매매기 개발(22.3~ 진행 중)

### 개발언어
Python

### 개발환경
Pycharm, pyqt designer

### API
키움증권 Open Api

### 개발기능
* 매매 관련
  * 수동매수
  * 자동매매기
    * 급등주 매수(거래량 기준)
    * 일정 수익 얻을 시 매도
  * 자동매매기 선정 종목 확인 및 주문
  * 잔고 현황
    * 전체 현황
    * 종목별 현황
  
* 차트조회
  * 종목 코드 검색 지원
  * 원하는 기간, 차트 종류 선택 가능
  * 그래프 개선 예정
* 개발 예정 기능
    
### 파일 소개

* 자동매매 관련
  * Kiwoom.py
  * pytrader.py
* 매수매도 관련
  * buy_list.txt
  * sell_list.txt
