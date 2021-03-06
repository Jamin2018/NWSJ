# -*- coding: utf-8 -*-

import os
import re
from pymongo import MongoClient
import pandas as pd
import plotly.offline as py
from plotly.graph_objs import Scatter, Layout
import plotly.graph_objs as go
import numpy as np
import random
import plotly.figure_factory as FF
from django.conf import settings

# 设置不换行
pd.set_option('expand_frame_repr', False)


def Connect_MongoDB():
    conn = MongoClient('127.0.0.1',27017)
    db = conn.nwsj
    return db


def db_get_df(db, account='.*', time_start = '1980-01-01', time_end = '2020-01-01', data_type='.*', sku = False, style='.*', color='.*', size='.*'):
    '''
    连接mongoDB选出数据
    '''
    # 这里lte小于等于并没有取到等于的日期数据，故日期需要加一天
    try:
        if not sku:
            mongoDB_data = db.order_refund_data.find(
                {'posted-date':{'$gte' : time_start , '$lte' : time_end},
                 'transaction-type': {'$regex':data_type},
                 'style': {'$regex':style},
                 'color': {'$regex':color},
                 'size': {'$regex':size},
                 'account':{'$regex':account},
                 })
        else:
            rexExp = re.compile(r'^%s' % sku)
            mongoDB_data = db.order_refund_data.find(
                {'posted-date':{'$gte' : time_start , '$lte' : time_end},
                 'transaction-type': {'$regex':data_type},
                 'sku': rexExp,
                 'account':{'$regex':account},
                 })
        df = pd.DataFrame(list(mongoDB_data))
        # print df
        # 处理时间数据，生成新的CSV数据表
        df['posted-date'] = pd.Series(pd.to_datetime(df['posted-date'])).dt.date
    except:
        df = pd.DataFrame()
    return df


def data_aggregation_table(account='.*', category = '.*',time_start = '1980-01-01', time_end = '2050-01-01', data_type='.*', sku = False, style='.*', color='.*', size='.*'):
    '''
    返回json数据
    '''
    db = Connect_MongoDB()
    aggregation_table = []  # 存最终的
    # 所有品类
    if style == '.*'and color=='.*' and size=='.*':
        # 找到所有品类名的总览
        category_sku_list = db.sku.find({'account': {'$regex': account}})
        category_name_list = []
        for i in pd.DataFrame(list(category_sku_list))['category'].drop_duplicates():
            category_name_list = category_name_list + i.split(',')
        category_name_list = set(category_name_list)   # 去重

        if category != '.*':
            category_name_list = [category]
        for category_name in category_name_list:
            category_sku_list = db.sku.find({'account': {'$regex': account},
                                             'category': {'$regex': category_name}})

            category_style_list = pd.DataFrame(list(category_sku_list)).drop_duplicates(['style'])['style']
            aggregation_table_temp = []  # 临时储存数据，根据category判断处理

            for sku_style in category_style_list:

                df = db_get_df(db, account=account, time_start=time_start, time_end=time_end, data_type=data_type,
                               sku=False,
                               style=sku_style, color=color, size=size)

                if not df.empty:
                    try:
                        order_quantity_purchased = pd.DataFrame(
                            list(df[df['transaction-type'] == 'Order']['quantity-purchased'].get_values())).sum()
                        if order_quantity_purchased.empty:
                            order_quantity_purchased = [0]

                        refund_quantity_purchased = pd.DataFrame(
                            list(df[df['transaction-type'] == 'Refund']['quantity-purchased'].get_values())).sum()
                        if refund_quantity_purchased.empty:
                            refund_quantity_purchased = [0]

                        order_price_amount = pd.DataFrame(
                            list(df[df['transaction-type'] == 'Order']['price-type'].get_values())).sum().sum()

                        refund_price_amount = pd.DataFrame(
                            list(df[df['transaction-type'] == 'Refund']['price-type'].get_values())).sum().sum()

                        freight = float(df['price'][0]) * float(df['weight'][0])  # 运费单价

                        # 退款率一般是字符串，影响下面的汇总，故要判断
                        if category != '.*':
                            refund_rate = '%.2f%%' % (
                                (refund_quantity_purchased[0] / order_quantity_purchased[0]) * 100)
                            if refund_rate == float('inf'):
                                refund_rate = '100%'
                        else:
                            refund_rate = (refund_quantity_purchased[0] / order_quantity_purchased[0]) * 100
                            if refund_rate == float('inf'):
                                refund_rate = 100

                        d =  {'type': sku_style,
                             'order_number': order_quantity_purchased[0],
                             'refund_number': refund_quantity_purchased[0],
                             'refund_rate': refund_rate,
                             'order_amount': round(order_price_amount, 2),
                             'refund_amount': round(refund_price_amount, 2),
                             'freight_cost': round(((order_quantity_purchased[0] + refund_quantity_purchased[0]) * freight), 2)
                             }


                        aggregation_table_temp.append(d)
                    except:
                        print sku_style

            if category == '.*':
                Serise = pd.DataFrame(aggregation_table_temp).sum()
                if Serise.empty:
                    continue
                Serise['refund_rate'] = '%.2f%%' % (Serise['refund_number'] / Serise['order_number'] * 100)
                df = pd.DataFrame(Serise)
                df = df.T
                df = df.drop('type', 1)
                df['type'] = category_name
                for dict_data in df.to_dict('records'):
                    dict_data['order_amount'] = round(dict_data['order_amount'],1)
                    dict_data['refund_amount'] = round(dict_data['refund_amount'],1)
                    dict_data['freight_cost'] = round(dict_data['freight_cost'],1)
                    aggregation_table.append(dict_data)
            else:
                aggregation_table = aggregation_table_temp
        # 排序后返回
        from operator import itemgetter
        aggregation_table = sorted(aggregation_table, key=itemgetter('order_number'), reverse=True)
        df = pd.DataFrame(aggregation_table)
        plotly_pivot_table_html(df)

        return aggregation_table

    else:
        sku_list = db.order_refund_data.find({'account': {'$regex': account}
                                ,'category': {'$regex': category}
                                ,'style': {'$regex': style}
                                ,'color': {'$regex': color}
                                ,'size': {'$regex': size}})

        sku_list = list(pd.DataFrame(list(sku_list)).drop_duplicates('sku')['sku'])
        print sku_list

        for sku in sku_list:
            df = db_get_df(db, account=account, time_start=time_start, time_end=time_end, data_type=data_type, sku=sku, style=sku, color=color, size=size)
            if not df.empty:
                try:
                    order_quantity_purchased = pd.DataFrame(list(df[df['transaction-type'] == 'Order']['quantity-purchased'].get_values())).sum()
                    if order_quantity_purchased.empty:
                        order_quantity_purchased= [0]
                    refund_quantity_purchased = pd.DataFrame(list(df[df['transaction-type'] == 'Refund']['quantity-purchased'].get_values())).sum()
                    if refund_quantity_purchased.empty:
                        refund_quantity_purchased = [0]
                    order_price_amount = pd.DataFrame(list(df[df['transaction-type'] == 'Order']['price-type'].get_values())).sum().sum()
                    refund_price_amount = pd.DataFrame(list(df[df['transaction-type'] == 'Refund']['price-type'].get_values())).sum().sum()

                    freight = float(df['price'][0]) * float(df['weight'][0])  # 运费单价
                    aggregation_table.append(
                        {'type':sku,
                         'order_number': order_quantity_purchased[0],
                         'refund_number': refund_quantity_purchased[0],
                         'refund_rate': '%.2f%%' % ((refund_quantity_purchased[0]/order_quantity_purchased[0]) * 100),
                         'order_amount': round(order_price_amount, 2),
                         'refund_amount': round(refund_price_amount, 2),
                         'freight_cost': round(((order_quantity_purchased[0] + refund_quantity_purchased[0]) * freight), 2)
                         })
                except Exception as e:
                    print e
                    print sku
            else:
                print sku
        # 排序后返回
        from operator import itemgetter
        aggregation_table = sorted(aggregation_table, key=itemgetter('order_number'), reverse=True)

        df = pd.DataFrame(aggregation_table)
        plotly_pivot_table_html(df)
        return aggregation_table


def plotly_pivot_table_html(df):
    '''
    绘制数据透视图
    :param df:
    :return:
    '''
    trace4 = go.Bar(
        x=df['type'],
        y=np.abs(df['order_number']),
        name='销售数量'
    )
    trace2 = go.Bar(
        x=df['type'],
        y=df['order_amount'],
        name='销售金额'
    )

    trace5 = go.Bar(
        x=df['type'],
        y=np.abs(df['refund_number']),
        name='退款数量'
    )

    trace3 = go.Bar(
        x=df['type'],
        y=np.abs(df['refund_amount']),
        name='退款金额'
    )

    trace1 = go.Bar(
        x=df['type'],
        y=np.abs(df['freight_cost']),
        name='运费成本'
    )

    data = [trace1, trace2, trace3, trace4, trace5]
    layout = go.Layout(
        barmode='group',
        xaxis=dict(title='类型'),
        yaxis=dict(type='log', title=''),
        paper_bgcolor='rgb(240, 240, 240)',
        plot_bgcolor='rgb(240, 240, 240)',
    )
    fig = go.Figure(data=data, layout=layout)
    filename = os.getcwd() + u'/templates/pivot_table_html/pivot_table.html'
    py.plot(fig, filename=filename, auto_open=False)



if __name__ == '__main__':
    # time_start = '2018-02-12'
    # time_end = '2018-02-27'
    # data_type = 'Refund'
    # color = '.*'
    # size = '.*'
    # data_aggregation_table()
    pass