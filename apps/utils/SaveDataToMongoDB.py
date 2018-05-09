# -*- coding: utf-8 -*-

from pymongo import MongoClient
import pandas as pd
import re

def Connect_MongoDB():
    conn = MongoClient('127.0.0.1',27017)
    db = conn.nwsj
    return db


def save_sku_to_MongoDB(df_csv, df_xlsx, account, db):
    '''
    把sku系列详细名字数据存入MongoDB
    '''
    df = df_csv[['sku']].dropna().drop_duplicates(['sku'])

    '''
    以下正则规则只适用于  style-color-size-.*{0.7}   |    style-[74023]{4}-color-size-.*{0.7}
    '''
    r = re.compile(
        r'([A-Z]{2,5}\d{2,6})-(\d{1,2}[a-zA-Z]{0,2}|[a-zA-Z]{0,2}\d{0,2})-(\d{0,2}[XSML]{0,4}\s{0,1})-{0,1}.{0,6}')
    r2 = re.compile(
        r'([A-Z]{2,5}\d{2,6})-[74023]{4}-(\d{1,2}[a-zA-Z]{0,2}|[a-zA-Z]{0,2}\d{0,2})-(\d{0,2}[XSML]{0,4}\s{0,1})-{0,1}.{0,6}')
    for sku in df['sku']:
        try:
            try:
                style = r.match(sku).group(1)
                color = r.match(sku).group(2)
                size = r.match(sku).group(3)
                sku = r.match(sku).group()



                if style == 'YSW5402':
                    category = ['shangyi']
                elif style == 'YSW1623':
                    category = ['yongyi']
                else:
                    import random
                    random_category = ['shangyi', 'xiuxianku', 'shatangku', 'yongyi', 'neiyi']
                    category = random.sample(random_category, 1)
                price = df_xlsx[df_xlsx['style'] == style]['price'].values[0]
                weight = df_xlsx[df_xlsx['style'] == style]['weight'].values[0]
                sku_dict = {'account':account,'sku':sku,'style':style,'color':color,'size':size, 'category':category,
                            'price':price,'weight':weight}


                db.sku.update({'account':account,'sku':sku,'style':style,'color':color,'size':size},
                                    {'$set': sku_dict}, True)
            except:
                style = r2.match(sku).group(1)
                color = r2.match(sku).group(2)
                size = r2.match(sku).group(3)
                sku =r2.match(sku).group()

                if style == 'YSW5402':
                    category = ['shangyi']
                elif style == 'YSW1623':
                    category = ['yongyi']
                else:
                    import random
                    random_category = ['shangyi', 'xiuxianku', 'shatangku', 'yongyi', 'neiyi']
                    category = random.sample(random_category, 1)

                price = df_xlsx[df_xlsx['style'] == style]['price'].values[0]
                weight = df_xlsx[df_xlsx['style'] == style]['weight'].values[0]
                sku_dict = {'account':account,'sku':sku,'style':style,'color':color,'size':size, 'category':category,
                            'price':price,'weight':weight}

                db.sku.update({'account':account,'sku':sku,'style':style,'color':color,'size':size},
                                    {'$set': sku_dict}, True)
        except Exception as e:
            print e


def get_data_dict(account, df):
    '''
    获得整理后的数据
    :param account:
    :param df:
    :return:
    '''
    # df_base = pd.read_csv('0211-0225bak.csv')
    df_base = df
    df_qp = df_base.iloc[:, [6, 7, 17, 21, 22]]
    df_qp = df_qp.groupby(['transaction-type', 'posted-date', 'order-id', 'sku', ],
                          as_index=False).sum()
    # 假设每个退款Refund为数量0实际为1，订单Order不可能有0的前提，处理Refund
    df_qp['quantity-purchased'] = df_qp['quantity-purchased'].replace(0, 1)
    temp_dict = {}
    # 将数量数据临时存进temp_dict
    for dict_qp in df_qp.to_dict('records'):
        dict_qp['account'] = account
        dict_qp['item-related-fee-type'] = {}
        dict_qp['price-type'] = {}
        dict_qp['promotion-type'] = {}
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


def mongoDB_createCollection():
    '''
    创建全文索引,和单键索引
    '''
    from pymongo import ASCENDING, TEXT
    db = Connect_MongoDB()
    # 单键索引
    db.order_refund_data.ensure_index([('sku', ASCENDING )])
    db.order_refund_data.ensure_index([('transaction-type', ASCENDING )])
    db.order_refund_data.ensure_index([('posted-date', ASCENDING )])
    db.order_refund_data.ensure_index([('account', ASCENDING )])
    # 全文索引
    # db.order_refund_data.create_index([('sku', TEXT )])


def save_to_mongoDB(account, df_csv, df_xlsx):
    '''
    调度器
    '''
    # # 连接MongoDB数据库
    db = Connect_MongoDB()
    # 存入账户信息
    db.account.update({'account': account}, {"$set": {'account': account}}, True)

    save_sku_to_MongoDB(df_csv, df_xlsx, account, db)
    list_data_dict = get_data_dict(account, df_csv)
    save_data_dict_to_MongoDB(list_data_dict, db)



if __name__ == '__main__':
    # 6:transaction-type  7:order-id  17:posted-date  21:sku  22:quantity-purchased
    # 23:price-type    24：price-amount
    # 25：item-related-fee-type 26: item-related-fee-amount
    # 31:promotion-type   32：promotion-amount
    # # 设置不换行
    # pd.set_option('expand_frame_repr', False)

    account = 'admin'
    df_csv = pd.read_csv('0211-0225bak.csv')
    df_xlsx = pd.read_excel('product_cost_weight-sample.xlsx')
    save_to_mongoDB(account, df_csv, df_xlsx)
