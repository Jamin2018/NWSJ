# -*- coding: utf-8 -*-
import os
import pickle
import pandas as pd
import plotly.offline as py
from plotly.graph_objs import Scatter, Layout
import plotly.graph_objs as go
import PyDataFun
import random
import plotly.figure_factory as FF


def draw_day_order_refund(df,sku_name = None):
    '''
    订单-退款-实际
    :param df:
    :param sku_name:
    :return:
    '''
    py.init_notebook_mode(connected=True)
    trace1 = go.Scatter(
        x= df.index,
        y=df[u'订单金额'],
        mode='lines+markers',
        name='订单金额',
        line=dict(
            shape='spline'
        )
    )

    trace2 = go.Scatter(
        x= df.index,
        y=df[u'退款金额'],
        mode='lines+markers',
        name='退款金额',
        line=dict(
            shape='spline'
        )
    )

    trace3 = go.Scatter(
        x= df.index,
        y=df[u'实际订单金额'],
        mode='lines+markers',
        name='实际订单金额',
        line=dict(
            shape='spline'
        )
    )
    sku_name = sku_name.encode('utf-8')
    title = sku_name+ '系列订单-退款'
    layout = dict(title = title,
                  xaxis = dict(title = '时间'),
                  yaxis = dict(title = '美元'),
                  )
    data = [trace1, trace2,trace3]
    fig = dict(data=data, layout=layout)

    filename = os.getcwd() + r'/templates/line_chart_html/order_refund_' + sku_name


    py.plot(fig, filename=filename)


def dict_line_day_sku_list():
    '''
    为绘制每日订单数提供数据
    :return:
    '''
    with open(os.getcwd()+'/media/data/data.pkl', 'rb') as f:
        data = f.read()
        data_dict = pickle.loads(data)
        sku_useful_info_dict = data_dict['sku_useful_info_dict']
        sku_name_list_sort = data_dict['sku_name_list_sort']

    sku_list = []
    for sku_name, v in sku_useful_info_dict.items():
        data = v['quantity-purchased']
        # DataFrame存入字典后取出变成series，故需要转回DataFrame，顺便设置列名
        data.name = sku_name
        data = data.to_frame(name=sku_name)
        sku_list.append(data)
        # 合并数据
    data = pd.concat(sku_list, axis=1)
    _ = data.fillna(0, inplace=True)
    # 绘图
    dic = {'sku_name_list_sort':sku_name_list_sort,'data':data}
    return dic

def draw_line_day_sku_list(dic):
    '''
    每日订单数
    :param dic:
    :return:
    '''
    sku_name_list_sort = dic['sku_name_list_sort']
    df = dic['data']
    data = []
    for i in sku_name_list_sort[:8]:
        line = go.Scatter(
            x=df.index,
            y=df[u'%s' % i],
            mode='lines',
            name=i,
            line=dict(
                shape='spline'
            ),
        )
        data.append(line)

    layout = dict(title = '每日订单数',
                  xaxis = dict(title = '日期'),
                  yaxis = dict(title = '个数'),

                  )
    fig = dict(data=data, layout=layout)

    filename = os.getcwd() + u'/templates/index_chart_html/2_每日订单数'
    py.plot(fig, filename=filename)



def dict_bar_sku_count():
    # 解析数据
    with open(os.getcwd()+'/media/data/data.pkl', 'rb') as f:
        data = f.read()
        data_dict = pickle.loads(data)
        sku_useful_info_dict = data_dict['sku_useful_info_dict']
        sku_name_list_sort = data_dict['sku_name_list_sort']

    sku_list = []
    for sku_name, v in sku_useful_info_dict.items():
        data = v['quantity-purchased']
        # DataFrame存入字典后取出变成series，故需要转回DataFrame，顺便设置列名
        data.name = sku_name
        data = data.to_frame(name=sku_name)
        sku_list.append(data)
        # 合并数据
    data = pd.concat(sku_list, axis=1)
    data = data.T.sum(axis = 1)
    # _ = data.fillna(0, inplace=True)
    # 绘图
    dic = {'sku_name_list_sort':sku_name_list_sort,'data':data}
    return dic

def draw_bar_sku_count(dic):
    sku_name_list_sort = dic['sku_name_list_sort']
    Sr = dic['data']

    df = Sr.to_frame(name='count')
    n = df.sum()
    df =  df.loc[sku_name_list_sort]


    df.insert(0,'sku', df.index)
    # 设置color颜色集合
    color_list = []
    for i in range(len(df)):
        r = random.randint(0,255)
        b = random.randint(0,255)
        a = random.randint(0,255)
        color_str = 'rgba(%s,%s,%s,0.7)' % (r,b,a)
        color_list.append(color_str)
    # 生成百分比
    df['proportion'] = df['count'].apply(lambda x:'总占比：'+str(round((x/n)*100,3))+'%')
    text = df['proportion']

    data = [go.Bar(
        x = df.index,
        y = df['count'],
        text = text,
        marker = dict(
            color = color_list
        )
    )]
    layout = dict(title = 'SKU系列前%s订单数' % len(df),
                  xaxis = dict(title = '系列名'),
                  yaxis = dict(type='log',title = '个数'),
                  paper_bgcolor='rgb(240, 240, 240)',
                  plot_bgcolor='rgb(240, 240, 240)',
                  )

    fig = dict(data=data, layout=layout)

    filename = os.getcwd() + u'/templates/index_chart_html/1_SKU系列前几订单数'

    sample_data_table = FF.create_table(df)
    print df.head(5)
    py.plot(sample_data_table, filename='sample-data-table')

    py.plot(fig,filename = filename)

def dict_pie_count_profits():
    with open(os.getcwd()+'/media/data/data.pkl', 'rb') as f:
        data = f.read()
        data_dict = pickle.loads(data)
        sku_useful_info_dict = data_dict['sku_useful_info_dict']
        sku_name_list_sort = data_dict['sku_name_list_sort']

    dic = {}
    all_profits_list = []
    all_count_list = []
    for sku_name in sku_name_list_sort:
        sku_useful_info = sku_useful_info_dict[sku_name]
        sku_useful_info['profits'] = sku_useful_info['price-amount'] + sku_useful_info['item-related-fee-amount'] + sku_useful_info['product_cost_weight']
        dic[sku_name] = sku_useful_info
        all_profits_list.append(sku_useful_info['profits'].sum())
        all_count_list.append(sku_useful_info['quantity-purchased'].sum())
    all_profits = sum(all_profits_list)
    all_count = sum(all_count_list)
    return {'sku_useful_info_dict':dic,'sku_name_list_sort':sku_name_list_sort,'all_profits':all_profits,'all_count':all_count}


def draw_pie_count_profits(dic):
    sku_useful_info_dict = dic['sku_useful_info_dict']
    sku_name_list_sort = dic['sku_name_list_sort']
    all_profits = dic['all_profits']
    all_count = dic['all_count']
    sku_count_values = []
    sku_profits_values = []
    sku_labels = []
    for sku_name in sku_name_list_sort[:9]:
        sku_useful_info = sku_useful_info_dict[sku_name]
        sku_useful_info = sku_useful_info.sum()
        sku_count_values.append(sku_useful_info['quantity-purchased'])
        sku_profits_values.append(sku_useful_info['profits'])
        sku_labels.append(sku_name)
    sku_count_values.append(all_count - sum(sku_count_values))
    sku_profits_values.append(all_profits - sum(sku_profits_values))
    sku_labels.append('其他')

    fig = {
        "data": [
            {
                "values": sku_count_values,
                "labels": sku_labels,
                "domain": {"x": [0, .48]},
                "name": "订单总占比",
                "hoverinfo": "label+percent+name",
                "hole": .4,
                "type": "pie"
            },
            {
                "values": sku_profits_values,
                "labels": sku_labels,
                "text": "CO2",
                "textposition": "inside",
                "domain": {"x": [.52, 1]},
                "name": "利润总占比",
                "hoverinfo": "label+percent+name",
                "hole": .4,
                "type": "pie"
            }],
        "layout": {
            'paper_bgcolor' : 'rgb(240, 240, 240)',
            'plot_bgcolor' : 'rgb(240, 240, 240)',
            "title": "订单-利润",
            "annotations": [
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": '订单总量：%s'% int(all_count),
                    "x": 0.20,
                    "y": 1.1
                },
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": '总利润：%s美元'% round(all_profits,2),
                    "x": 0.82,
                    "y": 1.1
                }
            ]
        }
    }
    filename = os.getcwd() + u'/templates/index_chart_html/3_订单利润总占比'
    py.plot(fig, filename = filename)



def test():
    import plotly.offline as off

    import pandas as pd

    off.init_notebook_mode(connected=False)

    df = pd.read_csv("https://plot.ly/~public.health/17.csv")

    print df['date'].head(5)

if __name__ == '__main__':
    test()
    # df = test()
    # draw_day_order_refund(df)dd
    # print df_day_sku_list()