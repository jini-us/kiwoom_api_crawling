
import sys
import os
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
from config.errCode import *
from beautifultable import BeautifulTable
from PyQt5.QtTest import *


class Kiwoom(QAxWidget):
    def __init__(self, save_list=list):
        super().__init__()

        self.save_list = save_list

        # 이벤트 루프 관련 변수
        self.login_event_loop = QEventLoop()
        self.account_event_loop = QEventLoop()
        self.calculator_event_loop = QEventLoop()

        # 계좌 관련 변수
        self.account_number = None
        self.total_buy_money = None
        self.total_evaluation_money = None
        self.total_evaluation_profit_and_loss_money = None
        self.total_yield = None
        self.account_stock_dict = {}
        self.not_signed_account_dict = {}

        # 예수금 관련 변수
        self.deposit = None
        self.withdraw_deposit = None
        self.order_deposit = None

        # 종목 분석 관련 변수
        self.calculator_list = []

        # 화면 번호
        self.screen_my_account = "1000"
        self.screen_calculation_stock = "2000"

        # 초기 작업
        self.create_kiwoom_instance()
        self.event_collection()  # 이벤트와 슬롯을 메모리에 먼저 생성.
        self.login()
        #input()
        self.get_account_info()  # 계좌 번호만 얻어오기
        self.get_deposit_info()  # 예수금 관련된 정보 얻어오기
        self.get_account_evaluation_balance()  # 계좌평가잔고내역 얻어오기
        self.not_signed_account()  # 미체결내역 얻어오기
        #self.calculator()
        #self.menu()

    # COM 오브젝트 생성.
    def create_kiwoom_instance(self):
        # 레지스트리에 저장된 키움 openAPI 모듈 불러오기
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def event_collection(self):
        self.OnEventConnect.connect(self.login_slot)  # 로그인 관련 이벤트
        self.OnReceiveTrData.connect(self.tr_slot)  # 트랜잭션 요청 관련 이벤트

    def login(self):
        self.dynamicCall("CommConnect()")  # 시그널 함수 호출.
        self.login_event_loop.exec_()

    def login_slot(self, err_code):
        if err_code == 0:
            print("로그인에 성공하였습니다.")
        else:
            os.system('cls')
            print("에러 내용 :", errors(err_code)[1])
            sys.exit(0)
        self.login_event_loop.exit()

    def get_account_info(self):
        account_list = self.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        account_number = account_list.split(';')[0]
        self.account_number = account_number

    def menu(self):
        sel = ""
        while True:
            os.system('cls')
            print("1. 현재 로그인 상태 확인")
            print("2. 사용자 정보 조회")
            print("3. 예수금 조회")
            print("4. 계좌 잔고 조회")
            print("5. 미체결 내역 조회")
            print("6. 종목 리스트 조회")
            print("7. 일별 투자자별 매수 매도 종목 조회")
            print("Q. 프로그램 종료")
            print("P. Kiwoom 객체를 보존한 채로 종료")
            sel = input("=> ")

            if sel == "Q" or sel == "q":
                sys.exit(0)
            if sel == "P" or sel == "p":
                break

            if sel == "1":
                self.print_login_connect_state()
            elif sel == "2":
                self.print_my_info()
            elif sel == "3":
                self.print_get_deposit_info()
            elif sel == "4":
                self.print_get_account_evaulation_balance_info()
            elif sel == "5":
                self.print_not_signed_account()
            elif sel == "6":
                stock_list_target_market_code = input("종목 리스트를 조회할 시장을 입력해주세요.(코스닥:10)")
                if stock_list_target_market_code not in ['10']:
                    print("현재 코스닥 이외에는 지원하지 않습니다.")
                    continue
                else:
                    self.stock_list = self.get_code_list_by_market(stock_list_target_market_code)
                    self.save_list.append(self.stock_list)
                    print("save_list 에 종목 리스트를 저장하였습니다.")
            elif sel == "7":
                target_start_date = input("조회 시작일자를 입력해주세요.(YYYYMMDD)")
                target_end_date = input("조회 종료일자를 입력해주세요.(YYYYMMDD)")
                target_buy_or_sale = input("매매 구분을 입력해주세요.(매수:2, 매도:1)")
                target_market = input("조회할 시장을 입력해주세요.(001:코스피, 101:코스닥)")
                target_investor = input("조회할 투자자를 입력해주세요.(8000:개인, 9000:외국인, 1000:금융투자, 3000:투신, 5000:기타금융, 4000:은행, 2000:보험, 6000:연기금, 7000:국가, 7100:기타법인, 9999:기관계)")
                self.get_daily_buy_or_sale_of_investor(start_date=target_start_date, end_date=target_end_date, buy_or_sale=target_buy_or_sale, market_code=target_market, investor_code=target_investor)
    
    def quit(self):
        sys.exit(0)
    def print_login_connect_state(self):
        os.system('cls')
        isLogin = self.dynamicCall("GetConnectState()")
        if isLogin == 1:
            print("\n현재 계정은 로그인 상태입니다.")
        else:
            print("\n현재 계정은 로그아웃 상태입니다.")
        input()

    def print_my_info(self):
        os.system('cls')
        user_name = self.dynamicCall("GetLoginInfo(QString)", "USER_NAME")
        user_id = self.dynamicCall("GetLoginInfo(QString)", "USER_ID")
        account_count = self.dynamicCall(
            "GetLoginInfo(QString)", "ACCOUNT_CNT")

        print(f"\n이름 : {user_name}")
        print(f"ID : {user_id}")
        print(f"보유 계좌 수 : {account_count}")
        print(f"계좌번호 : {self.account_number}")
        input()

    def print_get_deposit_info(self):
        os.system('cls')
        print(f"\n예수금 : {self.deposit}원")
        print(f"출금 가능 금액 : {self.withdraw_deposit}원")
        print(f"주문 가능 금액 : {self.order_deposit}원")
        input()

    def print_get_account_evaulation_balance_info(self):
        os.system('cls')
        print("\n<싱글 데이터>")
        print(f"총 매입 금액 : {self.total_buy_money}원")
        print(f"총 평가 금액 : {self.total_evaluation_money}원")
        print(f"총 평가 손익 금액 : {self.total_evaluation_profit_and_loss_money}원")
        print(f"총 수익률 : {self.total_yield}%\n")

        table = self.make_table("계좌평가잔고내역요청")
        print("<멀티 데이터>")
        if len(self.account_stock_dict) == 0:
            print("보유한 종목이 없습니다!")
        else:
            print(f"보유 종목 수 : {len(self.account_stock_dict)}개")
            print(table)
        input()

    def make_table(self, sRQName):
        table = BeautifulTable()
        table = BeautifulTable(maxwidth=150)

        if sRQName == "계좌평가잔고내역요청":
            for stock_code in self.account_stock_dict:
                stock = self.account_stock_dict[stock_code]
                stockList = []
                for key in stock:
                    output = None

                    if key == "종목명":
                        output = stock[key]
                    elif key == "수익률(%)":
                        output = str(stock[key]) + "%"
                    elif key == "보유수량" or key == "매매가능수량":
                        output = str(stock[key]) + "개"
                    else:
                        output = str(stock[key]) + "원"
                    stockList.append(output)
                table.rows.append(stockList)
            table.columns.header = ["종목명", "평가손익",
                                    "수익률", "매입가", "보유수량", "매매가능수량", "현재가"]
            table.rows.sort('종목명')

        elif sRQName == "실시간미체결요청":
            for stock_order_number in self.not_signed_account_dict:
                stock = self.not_signed_account_dict[stock_order_number]
                stockList = [stock_order_number]
                for key in stock:
                    output = None
                    if key == "주문가격" or key == "현재가":
                        output = str(stock[key]) + "원"
                    elif '량' in key:
                        output = str(stock[key]) + "개"
                    elif key == "종목코드":
                        continue
                    else:
                        output = stock[key]
                    stockList.append(output)
                table.rows.append(stockList)
            table.columns.header = ["주문번호", "종목명", "주문구분", "주문가격", "주문수량",
                                    "미체결수량", "체결량", "현재가", "주문상태"]
            table.rows.sort('주문번호')
        return table

    def print_not_signed_account(self):
        os.system('cls')
        print()
        table = self.make_table("실시간미체결요청")
        if len(self.not_signed_account_dict) == 0:
            print("미체결 내역이 없습니다!")
        else:
            print(table)
        input()

    def get_deposit_info(self, nPrevNext=0):
        self.dynamicCall("SetInputValue(QString, QString)",
                         "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", " ")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "2")
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "예수금상세현황요청", "opw00001", nPrevNext, self.screen_my_account)

        self.account_event_loop.exec_()

    def get_account_evaluation_balance(self, nPrevNext=0):
        self.dynamicCall("SetInputValue(QString, QString)",
                         "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", " ")
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "계좌평가잔고내역요청", "opw00018", nPrevNext, self.screen_my_account)

        if not self.account_event_loop.isRunning():
            self.account_event_loop.exec_()

    def not_signed_account(self, nPrevNext=0):
        self.dynamicCall("SetInputValue(QString, QString)",
                         "계좌번호", self.account_number)
        self.dynamicCall("SetInputValue(QString, QString)", "전체종목구분", "0")
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
        self.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "실시간미체결요청", "opt10075", nPrevNext, self.screen_my_account)

        if not self.account_event_loop.isRunning():
            self.account_event_loop.exec_()

    def tr_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "예수금상세현황요청":
            deposit = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            withdraw_deposit = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.withdraw_deposit = int(withdraw_deposit)

            order_deposit = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "주문가능금액")
            self.order_deposit = int(order_deposit)
            self.cancel_screen_number(self.screen_my_account)
            self.account_event_loop.exit()

        elif sRQName == "계좌평가잔고내역요청":
            if (self.total_buy_money == None or self.total_evaluation_money == None
                    or self.total_evaluation_profit_and_loss_money == None or self.total_yield == None):
                total_buy_money = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액")
                self.total_buy_money = int(total_buy_money)

                total_evaluation_money = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액")
                self.total_evaluation_money = int(total_evaluation_money)

                total_evaluation_profit_and_loss_money = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액")
                self.total_evaluation_profit_and_loss_money = int(
                    total_evaluation_profit_and_loss_money)

                total_yield = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총수익률(%)")
                self.total_yield = float(total_yield)

            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(cnt):
                stock_code = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목번호")
                stock_code = stock_code.strip()[1:]

                stock_name = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_name = stock_name.strip()  # 필요 없는 공백 제거.

                stock_evaluation_profit_and_loss = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평가손익")
                stock_evaluation_profit_and_loss = int(
                    stock_evaluation_profit_and_loss)

                stock_yield = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "수익률(%)")
                stock_yield = float(stock_yield)

                stock_buy_money = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매입가")
                stock_buy_money = int(stock_buy_money)

                stock_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보유수량")
                stock_quantity = int(stock_quantity)

                stock_trade_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "매매가능수량")
                stock_trade_quantity = int(stock_trade_quantity)

                stock_present_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                stock_present_price = int(stock_present_price)

                if not stock_code in self.account_stock_dict:
                    self.account_stock_dict[stock_code] = {}

                self.account_stock_dict[stock_code].update({'종목명': stock_name})
                self.account_stock_dict[stock_code].update(
                    {'평가손익': stock_evaluation_profit_and_loss})
                self.account_stock_dict[stock_code].update(
                    {'수익률(%)': stock_yield})
                self.account_stock_dict[stock_code].update(
                    {'매입가': stock_buy_money})
                self.account_stock_dict[stock_code].update(
                    {'보유수량': stock_quantity})
                self.account_stock_dict[stock_code].update(
                    {'매매가능수량': stock_trade_quantity})
                self.account_stock_dict[stock_code].update(
                    {'현재가': stock_present_price})

            if sPrevNext == "2":
                self.get_account_evaluation_balance(2)
            else:
                self.cancel_screen_number(self.screen_my_account)
                self.account_event_loop.exit()

        elif sRQName == "실시간미체결요청":
            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)

            for i in range(cnt):
                stock_code = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목코드")
                stock_code = stock_code.strip()

                stock_order_number = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문번호")
                stock_order_number = int(stock_order_number)

                stock_name = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                stock_name = stock_name.strip()

                stock_order_type = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문구분")
                stock_order_type = stock_order_type.strip().lstrip('+').lstrip('-')

                stock_order_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문가격")
                stock_order_price = int(stock_order_price)

                stock_order_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문수량")
                stock_order_quantity = int(stock_order_quantity)

                stock_not_signed_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "미체결수량")
                stock_not_signed_quantity = int(stock_not_signed_quantity)

                stock_signed_quantity = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "체결량")
                stock_signed_quantity = int(stock_signed_quantity)

                stock_present_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                stock_present_price = int(
                    stock_present_price.strip().lstrip('+').lstrip('-'))

                stock_order_status = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "주문상태")
                stock_order_status = stock_order_status.strip()

                if not stock_order_number in self.not_signed_account_dict:
                    self.not_signed_account_dict[stock_order_number] = {}

                self.not_signed_account_dict[stock_order_number].update(
                    {'종목코드': stock_code})
                self.not_signed_account_dict[stock_order_number].update(
                    {'종목명': stock_name})
                self.not_signed_account_dict[stock_order_number].update(
                    {'주문구분': stock_order_type})
                self.not_signed_account_dict[stock_order_number].update(
                    {'주문가격': stock_order_price})
                self.not_signed_account_dict[stock_order_number].update(
                    {'주문수량': stock_order_quantity})
                self.not_signed_account_dict[stock_order_number].update(
                    {'미체결수량': stock_not_signed_quantity})
                self.not_signed_account_dict[stock_order_number].update(
                    {'체결량': stock_signed_quantity})
                self.not_signed_account_dict[stock_order_number].update(
                    {'현재가': stock_present_price})
                self.not_signed_account_dict[stock_order_number].update(
                    {'주문상태': stock_order_status})

            if sPrevNext == "2":
                self.not_signed_account(2)
            else:
                self.cancel_screen_number(sScrNo)
                self.account_event_loop.exit()

        elif sRQName == "주식일봉차트조회요청":
            stock_code = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
            #six_hundred_data = self.dynamicCall("GetCommDataEx(QString, QString)", sTrCode, sRQName)

            stock_code = stock_code.strip()
            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                calculator_list = []

                current_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가")
                volume = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래량")
                trade_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "거래대금")
                date = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "일자")
                start_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가")
                high_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "고가")
                low_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "저가")

                calculator_list.append("")
                calculator_list.append(int(current_price))
                calculator_list.append(int(volume))
                calculator_list.append(int(trade_price))
                calculator_list.append(int(date))
                calculator_list.append(int(start_price))
                calculator_list.append(int(high_price))
                calculator_list.append(int(low_price))
                calculator_list.append("")

                self.calculator_list.append(calculator_list.copy())

            if sPrevNext == "2":
                self.day_kiwoom_db(stock_code, None, 2)
            else:
                self.calculator_event_loop.exit()
    
        elif sRQName == "투자자별일별매매종목요청":
            
            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                calculator_list = []

                stock_code = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "종목코드")
                stock_code = stock_code.strip()

                stock_name = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "종목명")
                volume = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "순매도수량") # 단위: 백 주
                pricevolume = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "순매도금액") # 단위: 백만 원
                average_price = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "추정평균가") # 순매도금액 / 순매도수량
                # curr_price = self.dynamicCall(
                #     "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "현재가") # 쿼리 조회 시점의 가격. 사실상 활용 불가
                # compare_sign = self.dynamicCall(
                #     "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "대비기호") # 뭔지 모르겠음
                # compare_to_prev_day = self.dynamicCall(
                #     "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "전일대비") # 쿼리 조회 시점에서의 전일대비 상승가격. 사실상 활용 불가
                # compare_to_average_price = self.dynamicCall(
                #     "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "평균가대비") # 쿼리 조회 시점에서의 가격과 추정평균가의 차이. 사실상 활용 불가
                # compare_percentage = self.dynamicCall(
                #     "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "대비율") # 활용 불가
                # periodical_volume = self.dynamicCall(
                #     "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "기간거래량") # 필요 없음

                calculator_list.append("")
                calculator_list.append(stock_code)
                calculator_list.append(stock_name)
                calculator_list.append(int(volume))
                calculator_list.append(pricevolume)
                calculator_list.append(int(average_price))
                # calculator_list.append(int(curr_price))
                # calculator_list.append(compare_sign)
                # calculator_list.append(int(compare_to_prev_day))
                # calculator_list.append(compare_to_average_price)
                # calculator_list.append(compare_percentage)
                # calculator_list.append(int(periodical_volume))
                calculator_list.append("")

                self.calculator_list.append(calculator_list.copy())

            if sPrevNext == "2":
                self.get_daily_buy_or_sale_of_investor(stock_code, None, 2)
            else:
                self.calculator_event_loop.exit()

        elif sRQName == "종목별투자자기관별합계요청":
            
            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                calculator_list = []

                output_1 = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "개인투자자")
                output_2 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "외국인투자자")
                output_3 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "기관계") # 단위: 백 주
                output_4 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "금융투자") # 단위: 백만 원
                output_5 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "보험") # 순매도금액 / 순매도수량
                output_6 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "투신")
                output_7 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "기타금융")
                output_8 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "은행")
                output_9 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "연기금등")
                output_10 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "사모펀드")
                output_11 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "국가")
                output_12 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "기타법인")
                output_13 = self.dynamicCall(
                    "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "내외국인")

                calculator_list.append(output_1)
                calculator_list.append(output_2)
                calculator_list.append(output_3)
                calculator_list.append(output_4)
                calculator_list.append(output_5)
                calculator_list.append(output_6)
                calculator_list.append(output_7)
                calculator_list.append(output_8)
                calculator_list.append(output_9)
                calculator_list.append(output_10)
                calculator_list.append(output_11)
                calculator_list.append(output_12)
                calculator_list.append(output_13)

                self.calculator_list.append(calculator_list.copy())

            if sPrevNext == "2":
                print("어떡하냐")
                self.get_cummulative_buy_or_sale_of_investor_stockwise(stock_code, None, 2)
            else:
                self.calculator_event_loop.exit()
        
        elif sRQName == "주식기본정보요청":
            
            cnt = self.dynamicCall(
                "GetRepeatCnt(QString, QString)", sTrCode, sRQName)  # 최대 600일

            for i in range(cnt):
                calculator_list = []

                output_1 = self.dynamicCall(
                "GetCommData(QString, QString, int, QString)", sTrCode, sRQName, i, "시가총액")

                calculator_list.append(output_1)

                self.calculator_list.append(calculator_list.copy())

            if sPrevNext == "2":
                print("어떡하냐")
                self.get_cummulative_buy_or_sale_of_investor_stockwise(stock_code, None, 2)
            else:
                self.calculator_event_loop.exit()


    def cancel_screen_number(self, sScrNo):
        self.dynamicCall("DisconnectRealData(QString)", sScrNo)

    def get_code_list_by_market(self, market_code):
        code_list = self.dynamicCall(
            "GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(";")[:-1]
        return code_list

    def calculator(self):
        kosdaq_list = self.get_code_list_by_market("10")

        for idx, stock_code in enumerate(kosdaq_list):
            self.dynamicCall("DisconnectRealData(QString)",
                             self.screen_calculation_stock)

            print(
                f"{idx + 1} / {len(kosdaq_list)} : KOSDAQ Stock Code : {stock_code} is updating...")
            self.day_kiwoom_db(stock_code)

    def day_kiwoom_db(self, stock_code=None, date=None, nPrevNext=0):
        QTest.qWait(3600)  # 3.6초마다 딜레이

        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", stock_code)
        self.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", 1)

        if date != None:  # date가 None일 경우 date는 오늘 날짜 기준
            self.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)

        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "주식일봉차트조회요청", "opt10081", nPrevNext, self.screen_calculation_stock)

        if not self.calculator_event_loop.isRunning():
            self.calculator_event_loop.exec_()
    
    def get_daily_buy_or_sale_of_investor(self, start_date=None, end_date=None, buy_or_sale=None, market_code=None, investor_code=None):
        
        print(str(start_date) + "의 매매 데이터를 불러오는 중")
        
        QTest.qWait(3600) # 3.6초마다 딜레이
        
        self.dynamicCall("SetInputValue(QString, QString)", "시작일자",  start_date)
        self.dynamicCall("SetInputValue(QString, QString)", "종료일자",  end_date)
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분",  buy_or_sale)
        self.dynamicCall("SetInputValue(QString, QString)", "시장구분", market_code)
        self.dynamicCall("SetInputValue(QString, QString)", "투자자구분",  investor_code)
        
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "투자자별일별매매종목요청", "opt10058", 0, self.screen_calculation_stock)
        
        if not self.calculator_event_loop.isRunning():
            self.calculator_event_loop.exec_()
    
    def get_cummulative_buy_or_sale_of_investor_stockwise(self, stock_code = None, start_date=None, end_date=None, price_or_volume = None, net_or_buy_or_sale=None, unit_code=None):
        
        QTest.qWait(1000) # 1.0초마다 딜레이
        
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드",  stock_code)
        self.dynamicCall("SetInputValue(QString, QString)", "시작일자",  start_date)
        self.dynamicCall("SetInputValue(QString, QString)", "종료일자",  end_date)
        self.dynamicCall("SetInputValue(QString, QString)", "금액수량구분",  price_or_volume)
        self.dynamicCall("SetInputValue(QString, QString)", "매매구분", net_or_buy_or_sale)
        self.dynamicCall("SetInputValue(QString, QString)", "단위구분",  unit_code)
        
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "종목별투자자기관별합계요청", "opt10061", 0, self.screen_calculation_stock)
        
        if not self.calculator_event_loop.isRunning():
            self.calculator_event_loop.exec_()

    def get_basic_info_of_stock(self, stock_code = None):
        
        QTest.qWait(1000) # 1.0초마다 딜레이
        
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드",  stock_code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)",
                         "주식기본정보요청", "opt10001", 0, self.screen_calculation_stock)
        
        if not self.calculator_event_loop.isRunning():
            self.calculator_event_loop.exec_()