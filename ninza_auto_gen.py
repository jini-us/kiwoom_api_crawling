# 이 코드의 목적
# 이제부터 daily 연기금 매수/매도 데이터를 쌓아나갈 것

# 거래일을 가져오는 과정

import FinanceDataReader as fdr
import pandas as pd
import numpy as np
import datetime

import sys
from PyQt5.QtWidgets import *
from kiwoom.kiwoom_auto import *
import pickle

def auto_gen(gen_idx, list_idx, target_year):


    full_date_df = fdr.DataReader('KQ11', target_year)

    raw_tradingdays = list(full_date_df.index.values)

    tradingdays = [int(pd.to_datetime(td).strftime('%Y%m%d')) for td in raw_tradingdays]

    app = QApplication(sys.argv)
    
    save_list = []
    
    sum_start_date = tradingdays[gen_idx]
    sum_end_date = tradingdays[gen_idx]
    
    print(str(sum_start_date) + "의 매매 데이터 수집 시작")
    for dict_idx in [list_idx]:
        stockwise_dict = {}
        kiwoom = Kiwoom(save_list)
        target_start_date = sum_start_date
        target_end_date = sum_end_date
        target_price_or_volume = 1 # 금액: 1, 수량: 2
        target_net_or_buy_or_sale = 0 # 순매수: 0, 매수: 1, 매도: 2
        target_unit_code = 1 # 0: 천 주, 1: 단 주
        stock_code_list = kiwoom.get_code_list_by_market('10') # '10'이 코스닥
        for idx, target_stock_code in enumerate(stock_code_list):
            if dict_idx==1:
                if idx>=800:
                    break
            else:
                if idx<800:
                    continue
            print(str(idx) + '/' + str(len(stock_code_list)) + ' 현재 ' + str(target_stock_code) + '의 매매 데이터를 불러오는 중')
            kiwoom.calculator_list = []
            kiwoom.get_cummulative_buy_or_sale_of_investor_stockwise(stock_code=target_stock_code, start_date = target_start_date, end_date = target_end_date, price_or_volume = target_price_or_volume, net_or_buy_or_sale = target_net_or_buy_or_sale, unit_code = target_unit_code)
            raw_data = kiwoom.calculator_list[0]
            parsed_data = [int(rd.strip()) for rd in raw_data]
            stockwise_dict[target_stock_code] = parsed_data
        with open('./daily_stockwise_dict/'+target_year+'/daily_stockwise_dict_' + str(sum_start_date) +'_'+str(dict_idx)+'.pickle', 'wb') as f:
            pickle.dump(stockwise_dict, f)
        #kiwoom.quit()

def main(gen_idx, list_idx, target_year):
    auto_gen(gen_idx=int(gen_idx), list_idx=int(list_idx), target_year= target_year)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])