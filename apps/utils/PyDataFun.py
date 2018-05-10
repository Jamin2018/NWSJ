# -*- coding: utf-8 -*-
import os
import random
import re
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt  # 导入绘图库
import pickle


def get_df(filename, usecols = None):
    '''
    获得有用的df的数据列
    '''
    if filename[-3:] == 'csv' :
        df = pd.read_csv(filename, usecols = usecols)
    elif filename[-4:] == 'xlsx':
        df = pd.read_excel(filename, usecols=usecols)
    return (df)


def get_sku_name_list(df):
    '''
    获得sku名字列表
    '''
    df = df['sku'].dropna()
    r = r'(.*?)-'
    sku_name_set = set()
    for i in df.values:
        a = re.match(r, i).group(1)
        sku_name_set.add(a)
    return sku_name_set


def get_orderly_sku_list(sku_info_dict, transaction_type = 'Order', reverse=True , product_cost_weight = None):
    '''
    获得有序列表名
    '''
    sku_count_dict = {}
    for sku_name,sku_info in sku_info_dict.items():
        sku_useful_info = get_sku_useful_info(sku_name, sku_info, transaction_type = transaction_type,product_cost_weight= product_cost_weight)  # 获得订单单个有用信息，根据需求,处理后的sku信息
        sku_count = sku_useful_info['quantity-purchased'].sum(axis=0)
        sku_count_dict[sku_name]=sku_count

    sku_name_dict_sort = sorted(sku_count_dict.items(), key=lambda x: x[1], reverse=reverse)
    lit = []
    for sku_name in sku_name_dict_sort:
        lit.append(sku_name[0])
    return lit


def get_sku_info_dict(df,sku_name_list):
    '''
     获得所有每个系列的sku的信息字典集合
    '''
    dic = {}
    for i in sku_name_list:
        r = r'(%s)-' % i
        # print(df_csv['sku'].index)
        m = df['sku'].fillna('0')
        data = df[m.str.contains(r, na=True)]  # 分别筛选各个系列的详细数据
        dic[i] = data
    return dic


def get_sku_info(sku_name,sku_info_dict):
    '''
    通过当个sku名获得该sku信息集合
    '''
    sku_info = sku_info_dict[sku_name]
    return sku_info


def get_sku_useful_info(sku_name,sku_info,exchange_rate = 0.1589,transaction_type ='Order', product_cost_weight= None):
    '''
    获得单个有用shu数据，根据需求,处理后的sku信息
    '''
    product_cost_weight = product_cost_weight
    df_product_cost_weight = product_cost_weight[product_cost_weight['style'] == sku_name]
    sku_useful_info = sku_info[sku_info['transaction-type'] == transaction_type ]
    # 处理时间数据，生成新的CSV数据表
    sku_useful_info['posted-date'] = pd.Series(pd.to_datetime(sku_useful_info['posted-date'])).dt.date
    sku_useful_info = sku_useful_info.groupby('posted-date').sum()
    price = df_product_cost_weight.iat[0,1]
    weight = df_product_cost_weight.iat[0,2]
    sku_useful_info['product_cost_weight'] = sku_useful_info['quantity-purchased'].apply(lambda x : -x * price * weight * exchange_rate)
    return (sku_useful_info)


def get_sku_useful_info_dict(sku_name_list,sku_info_dict,product_cost_weight= None):
    '''
    传入一个想查询的列表名，获得该列表的信息字典
    '''
    sku_dict = {}
    for sku_name in sku_name_list:
        sku_info = get_sku_info(sku_name, sku_info_dict)  # 获得单个sku信息
        sku_useful_info = get_sku_useful_info(sku_name, sku_info,product_cost_weight = product_cost_weight)  # 获得单个有用信息，根据需求,处理后的sku信息
        sku_dict[sku_name] = sku_useful_info
    return sku_dict


def draw_day_sku_list(sku_useful_info_dict):
    '''
    每日订单
    '''
    sku_list = []
    for sku_name, v in sku_useful_info_dict.items():
        data = v['quantity-purchased']
        # DataFrame存入字典后取出变成series，故需要转回DataFrame，顺便设置列名
        data.name = sku_name
        data  = data.to_frame(name=sku_name)
        sku_list.append(data)
    # 合并数据
    data = pd.concat(sku_list, axis=1)
    _ = data.fillna(0, inplace=True)
    # 绘图

    path = os.getcwd()
    filepath = path + r'/static/img/data/'
    # drawing(data,title=u'每日订单数',to_imgpath = filepath)
    return (data)


def draw_day_profits_list(sku_useful_info_dict):
    '''
    获得每日利润图
    '''
    sku_list = []
    for sku_name, v in sku_useful_info_dict.items():
        # 价格合并到一起
        amount= v[[ 'price-amount', 'item-related-fee-amount','product_cost_weight']].apply(lambda x: x.sum(), axis=1)
        #     # DataFrame存入字典后取出变成series，故需要转回DataFrame，顺便设置列名
        amount.name = sku_name
        data = amount.to_frame(name=sku_name)
        sku_list.append(data)
    # 合并数据
    data = pd.concat(sku_list, axis=1)
    _ = data.fillna(0, inplace=True)
    # 绘图
    path = os.getcwd()
    filepath = path + r'/static/img/data/'
    # drawing(data, title=u'每日利润',to_imgpath=filepath)
    return (data)


def get_day_profit_price(sku_name,sku_info_dict,subplots=True, product_cost_weight_path = None):
    '''
    获得单系列每日平均售价和每日利润的关系图
    '''
    sku_info = get_sku_info(sku_name,sku_info_dict)   # 获得单个sku信息
    sku_useful_info = get_sku_useful_info(sku_name,sku_info, product_cost_weight_path = product_cost_weight_path)     # 获得单个有用信息，根据需求,处理后的sku信息
    # 获得每日利润数据
    profit_day = sku_useful_info[[ 'price-amount', 'item-related-fee-amount','product_cost_weight']].apply(lambda x: x.sum(), axis=1)
    # 获得每日均价数据
    average_price = sku_useful_info['price-amount'] / sku_useful_info['quantity-purchased']
    # Series --> DataFrame
    average_price,profit_day = average_price.to_frame(name=u'每日均价'),profit_day.to_frame(name=u'每日利润')
    data = pd.concat([average_price,profit_day], axis=1)
    return data


if __name__ == '__main__':
    file = '0211-0225bak.csv'
    product_cost_weight_path = 'product_cost_weight-sample.xlsx'
    df_csv = get_df(file,usecols =[6,7, 17, 21, 22, 24, 26])  # 获得有用数据
    sku_name_list = get_sku_name_list(df_csv)  # 获得列表名
    sku_info_dict = get_sku_info_dict(df_csv,sku_name_list) # 根据列名获取相关字典信息
    with open('test.pkl','wb') as f:
        data = pickle.dumps(sku_info_dict)
        f.write(data)
    sku_name_list_sort = get_orderly_sku_list(sku_info_dict, transaction_type = 'Order',reverse=True,product_cost_weight_path = product_cost_weight_path)

    sku_name = sku_name_list_sort[0]
    sku_info = get_sku_info(sku_name,sku_info_dict)   # 获得单个sku信息
    sku_useful_info = get_sku_useful_info(sku_name,sku_info,transaction_type = 'Order',product_cost_weight_path= product_cost_weight_path)     # 获得订单单个有用信息，根据需求,处理后的sku信息
    print sku_useful_info
    sku_useful_info.to_csv('test.csv')
    refund_sku_useful_info = get_sku_useful_info(sku_name,sku_info,transaction_type = 'Refund')     # 获得退款单个有用信息，根据需求,处理后的sku信息
    print(sku_useful_info.head(5))
    sku_useful_info_dict = get_sku_useful_info_dict(sku_name_list_sort[:5], sku_info_dict)  # 获得选择的sku字典信息
