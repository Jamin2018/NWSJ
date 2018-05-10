# -*- coding: utf-8 -*-

from pymongo import MongoClient
import pandas as pd
import re

def Connect_MongoDB():
    conn = MongoClient('127.0.0.1',27017)
    db = conn.nwsj
    return db


def save_sku_to_MongoDB(df_xlsx, df_sku, db):
    '''
    把sku系列详细名字数据存入MongoDB
    '''
    for dic in df_sku.to_dict('records'):
        try:
            dic['price'] = df_xlsx[df_xlsx['style'] == dic['style']]['price'].values[0]
            dic['weight'] = df_xlsx[df_xlsx['style'] == dic['style']]['weight'].values[0]
            # 注意将数字转成字符串，不然在取数据的时候用正则匹配不到
            dic['size'] = str(dic['size'])
            dic['color'] = str(dic['color'])

            db.sku.update({'account':dic['account'],'sku':dic['sku'],'style':dic['style'],'color':dic['color'],'size':dic['size']},
                                {'$set': dic}, True)
        except Exception as e:
            print e


def get_data_dict(df_csv, df_xlsx, df_sku, db):
    '''
    获得整理后的数据
    :param account:
    :param df:
    :return:
    '''

    # 处理订单/退款数据
    df_base = df_csv
    df_qp = df_base.iloc[:, [6, 7, 17, 21, 22]]
    df_qp = df_qp.groupby(['transaction-type', 'posted-date', 'order-id', 'sku', ],
                          as_index=False).sum()
    # 假设每个退款Refund为数量0实际为1，订单Order不可能有0的前提，处理Refund
    df_qp['quantity-purchased'] = df_qp['quantity-purchased'].replace(0, 1)
    temp_dict = {}
    # 将数量数据临时存进temp_dict
    for dict_qp in df_qp.to_dict('records'):
        dict_qp['item-related-fee-type'] = {}
        dict_qp['price-type'] = {}
        dict_qp['promotion-type'] = {}

        # 将sku详细数据存入，若sku数据不全，则会报错
        try:
            sku_dic = db.sku.find_one({'sku': dict_qp['sku']})
            dict_qp['account'] = sku_dic['account']
            dict_qp['category'] = sku_dic['category']
            dict_qp['style'] = sku_dic['style']
            dict_qp['color'] = sku_dic['color']
            dict_qp['size'] = sku_dic['size']
            dict_qp['weight'] = sku_dic['weight']
            dict_qp['price'] = sku_dic['price']
        except Exception as e:
            pass
            # print '缺少sku数据：'+ dict_qp['sku']
        temp_dict[dict_qp['transaction-type'] + dict_qp['order-id'] + dict_qp['posted-date'] + dict_qp['sku']] = dict_qp

    # 获得获得price_type数据
    df_price_type = df_base.iloc[:,[6, 7, 17, 21 , 23, 24]]
    df_price_type = df_price_type.groupby(['transaction-type', 'posted-date', 'order-id', 'sku','price-type'],
                        as_index=False).sum()
    # 将temp_dict 中数据更新
    for dict_data in df_price_type.to_dict('records'):
        temp_dict.get(dict_data['transaction-type'] + dict_data['order-id'] + dict_data['posted-date'] +
                      dict_data['sku'])['price-type'][dict_data['price-type']] = dict_data['price-amount']

    # 获得item-related-fee-type数据
    df_irft = df_base.iloc[:, [6, 7, 17, 21, 25, 26]]
    df_irft = df_irft.groupby(['transaction-type', 'posted-date', 'order-id', 'sku', 'item-related-fee-type'],
                              as_index=False).sum()
    # 将temp_dict 中数据更新
    for dict_data in df_irft.to_dict('records'):
        temp_dict.get(dict_data['transaction-type'] + dict_data['order-id'] + dict_data['posted-date'] +
                      dict_data['sku'])['item-related-fee-type'][dict_data['item-related-fee-type']] = dict_data['item-related-fee-amount']

    #获得获得promotion-type数据
    df_promotion_type = df_base.iloc[:,[6, 7, 17, 21 , 31, 32]]
    df_promotion_type = df_promotion_type.groupby(['transaction-type', 'posted-date', 'order-id', 'sku','promotion-type'],
                        as_index=False).sum()
    # 将temp_dict 中数据更新
    for dict_data in df_promotion_type.to_dict('records'):
        temp_dict.get(dict_data['transaction-type'] + dict_data['order-id'] + dict_data['posted-date'] +
                      dict_data['sku'])['promotion-type'][dict_data['promotion-type']] = dict_data['promotion-amount']

    return temp_dict.values()

def save_data_dict_to_MongoDB(list_data_dict, db):
    '''
    将整理好的数据存入MongoDB
    '''
    for dict_data in list_data_dict:
        db.order_refund_data.update({'transaction-type': dict_data['transaction-type'],
                                      'posted-date': dict_data['posted-date'],
                                      'order-id': dict_data['order-id'],
                                      'sku': dict_data['sku']},
                                     {"$set": dict_data}, True)


def save_to_mongoDB(df_csv, df_xlsx, df_sku):
    '''
    调度器
    '''
    # # 连接MongoDB数据库
    db = Connect_MongoDB()
    # 存入账户信息
    # db.account.update({'account': account}, {"$set": {'account': account}}, True)
    save_sku_to_MongoDB(df_xlsx, df_sku, db)
    list_data_dict = get_data_dict(df_csv, df_xlsx, df_sku, db)
    save_data_dict_to_MongoDB(list_data_dict, db)


def mongoDB_createCollection():
    '''
    创建全文索引,和单键索引
    '''
    from pymongo import ASCENDING, TEXT
    db = Connect_MongoDB()
    # 单键索引
    db.sku.ensure_index([('sku', ASCENDING )])
    db.order_refund_data.ensure_index([('sku', ASCENDING )])
    db.order_refund_data.ensure_index([('transaction-type', ASCENDING )])
    db.order_refund_data.ensure_index([('posted-date', ASCENDING )])
    db.order_refund_data.ensure_index([('account', ASCENDING )])
    # 全文索引
    # db.order_refund_data.create_index([('sku', TEXT )])

if __name__ == '__main__':
    # 6:transaction-type  7:order-id  17:posted-date  21:sku  22:quantity-purchased
    # 23:price-type    24：price-amount
    # 25：item-related-fee-type 26: item-related-fee-amount
    # 31:promotion-type   32：promotion-amount
    # # 设置不换行
    # pd.set_option('expand_frame_repr', False)

    mongoDB_createCollection()
    print 'text2'
