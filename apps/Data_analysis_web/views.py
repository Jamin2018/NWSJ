# -*- coding: utf-8 -*-

import os
import time
from django.shortcuts import render,HttpResponse,redirect
from utils import PyDataFun
from utils import PyPlotly
import json
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from utils.SaveDataToMongoDB import *
from utils import SaveDataToMongoDB, PivotTable
import pandas as pd


def DataIndexView(request):
    '''
    获得本地图表html文件名
    '''
    chart_path = os.getcwd() + r'/templates/index_chart_html/'
    chart_name_list = []
    for root, dirs, files in os.walk(chart_path):
        for file_name in files:
            chart_name_list.append(file_name.decode('GB2312').encode('utf-8'))
    return render(request, 'index.html', {'chart_name_list':chart_name_list, })


@csrf_exempt
def DataInputView(request):
    '''
    接收csv文件，将数据上传到mongoDB数据库
    '''
    if request.method == 'POST':
        # account = request.POST.get('account1')
        file_csv =request.FILES.get('file_csv')
        file_xlsx =request.FILES.get('file_xlsx')
        file_sku =request.FILES.get('file_sku')
        # try:
        #     if not file_csv or not file_xlsx :
        #         if not file_csv:
        #             time.sleep(1)
        #             return HttpResponse(json.dumps({"err": -1, "msg": "请选择csv文件"}), content_type='application/json')
        #         elif not file_xlsx:
        #             time.sleep(1)
        #             return HttpResponse(json.dumps({"err": -1, "msg": "请选择xlsx文件"}), content_type='application/json')
        #     elif file_csv.name[-3:] != 'csv' or file_xlsx.name[-4:] != 'xlsx':
        #         if file_csv.name[-3:] != 'csv':
        #             time.sleep(1)
        #             return HttpResponse(json.dumps({"err": -1, "msg": "请传入正确的csv数据"}),content_type='application/json')
        #         elif file_xlsx.name[-4:] != 'xlsx':
        #             time.sleep(1)
        #             return HttpResponse(json.dumps({"err": -1, "msg": "请传入正确的运费数据"}),content_type='application/json')
        # except:
        #     time.sleep(1)
        #     return HttpResponse(json.dumps({"err": -1, "msg": "请选择正确的文件"}), content_type='application/json')

        try:
            if file_csv.name[-3:] == 'csv':
                df_csv = pd.read_csv(file_csv)
            else:
                df_csv = pd.read_excel(file_csv)


            df_xlsx = pd.read_excel(file_xlsx)
            df_sku = pd.read_excel(file_sku)
            # 存储数据到MongoDB
            SaveDataToMongoDB.save_to_mongoDB(df_csv, df_xlsx, df_sku)
            return HttpResponse(json.dumps({"err": 0, "msg": "数据上传完毕"}),content_type='application/json')
        except Exception as e:
            print (e)
            time.sleep(1)
            return HttpResponse(json.dumps({"err": -1, "msg": "数据上传失败"}),content_type='application/json')


@csrf_exempt
def DataAutoDrawView(request):
    '''
    一键构图
    :param request:
    :return:
    '''
    if request.method == 'POST':
        chart_type = request.POST.getlist('chart_type[]','')
        if chart_type:
            import shutil
            # 防止文件被占用，先强制删除文件夹，再重新建同名文件夹
            dir_path = os.getcwd() + '/templates/index_chart_html/'
            shutil.rmtree(dir_path)
            os.mkdir(dir_path)
            for chart_name in chart_type:
                if chart_name == 'draw_line_day_sku_list':
                    line_dict= PyPlotly.dict_line_day_sku_list()
                    PyPlotly.draw_line_day_sku_list(line_dict)
                if chart_name == 'draw_bar_sku_count':
                    bar_dict = PyPlotly.dict_bar_sku_count()
                    PyPlotly.draw_bar_sku_count(bar_dict)
                if chart_name == 'draw_pie_count_profits':
                    pie_dict = PyPlotly.dict_pie_count_profits()
                    PyPlotly.draw_pie_count_profits(pie_dict)

            return HttpResponse(json.dumps({"err": 0, "msg": "OK"}), content_type='application/json')
        else:
            return HttpResponse(json.dumps({"err": -1, "msg": "请选择图表类型"}), content_type='application/json')


@csrf_exempt
def SkuNameListUpdateView(request):
    '''
    系列名列表显示
    :param request:
    :return:
    '''
    try:
        db = SaveDataToMongoDB.Connect_MongoDB()
        mongoDB_data = db.sku.find()
        sku_name_list = pd.DataFrame(list(mongoDB_data)).drop_duplicates(['style'])['style'].tolist()
        print sku_name_list
        return HttpResponse(json.dumps({"err": 0, "msg": sku_name_list}), content_type='application/json')
    except:
        time.sleep(1)
        return HttpResponse(json.dumps({"err": -1, "msg": '数据包不存在'}),content_type='application/json')



@csrf_exempt
def ChooseSkuDrawView(request):
    '''
    选择系列构图
    '''
    return HttpResponse(json.dumps({"err": 0, "msg": 'OK'}), content_type='application/json')

def SkuChartView(request):
    '''
    SKU系列页面
    :param request:
    :return:
    '''
    chart_path = os.getcwd() + r'/templates/line_chart_html/'
    chart_name_list = []
    for root, dirs, files in os.walk(chart_path):
        for file_name in files:
            chart_name_list.append(file_name.decode('GB2312').encode('utf-8'))
    print chart_name_list
    return render(request, 'chart.html', {'chart_name_list':chart_name_list, })




def PivotTableView(request):
    '''
    数据透视页面
    :param request:
    :return:
    '''
    # pivot_table_path = os.getcwd() + r'/templates/pivot_table_html/'
    # pivot_table_name_list = []
    # for root, dirs, files in os.walk(pivot_table_path):
    #     for file_name in files:
    #         pivot_table_name_list.append(file_name.decode('GB2312').encode('utf-8'))


    return render(request, 'pivot_table.html', {})


@csrf_exempt
def PivotTableJsonDataView(request):
    '''
    JSON接口，获得数据透视表的JSON数据
    '''
    limit = int(request.GET.get('limit', 15))
    page = int (request.GET.get('page', 1))
    date = request.GET.get('date','1980-01-01 00:00:00 - 2050-01-01 00:00:00')
    if len(date) < 1:date = '1980-01-01 00:00:00 - 2050-01-01 00:00:00'
    time_start = date[:(len(date)/2)].strip()
    time_end = date[(len(date)/2) +1:].strip()
    account = request.GET.get('account','.*')
    category = request.GET.get('category', '.*')
    style = request.GET.get('style','.*')
    color = request.GET.get('color','.*')
    size = request.GET.get('size','.*')

    all_data = PivotTable.data_aggregation_table(account, category, time_start=time_start, time_end=time_end,
                                                 data_type='.*', style=style, color=color, size=size)
    start_data = (page - 1) * limit
    end_data = page * limit
    data = all_data[start_data:end_data]

    return HttpResponse(json.dumps({"code": 0, "msg": 'OK', "count":len(all_data), "data":data}), content_type='application/json')

def AccountListView(request):
    '''
    从setting中获得账户名,
    '''
    from copy import deepcopy
    account_list = deepcopy(settings.ACCOUNT_LIST)
    return HttpResponse(json.dumps({"err": 0,
                                    "msg": 'OK',
                                    'account_list':account_list,
                                    }), content_type='application/json')


def StyleListView(request):
    '''
    从数据库中获得sku的style列表
    '''
    account = request.GET.get('account','.*')
    category = request.GET.get('category','.*')
    db = SaveDataToMongoDB.Connect_MongoDB()
    data = db.sku.find({'account':{'$regex':account},
                        'category': {'$regex': category}, })
    data= pd.DataFrame(list(data))
    data_style = data.drop_duplicates(['style'])['style'].tolist()
    return HttpResponse(json.dumps({"code": 0, "msg": 'OK',"data_style":data_style}),
                        content_type='application/json')



def ColorSizeListView(request):
    '''
    从数据库中获得sku的color,size列表
    '''
    account = request.GET.get('account','.*')
    style = request.GET.get('style','.*')
    print account
    print style
    db = SaveDataToMongoDB.Connect_MongoDB()
    data = db.sku.find({'account':{'$regex':account},
                        'style': {'$regex': style}})
    data= pd.DataFrame(list(data))
    data_color = data.drop_duplicates(['color'])['color'].tolist()
    data_size = data.drop_duplicates(['size'])['size'].tolist()
    print len(data_color)
    print len(data_size)
    return HttpResponse(json.dumps({"code": 0, "msg": 'OK', "data_color": data_color,"data_size":data_size}),
                        content_type='application/json')


@csrf_exempt
def PivotTableHtmlView(request):
    '''

    :param request:
    :return:
    '''
    chart_path = os.getcwd() + r'/templates/pivot_table_html/'
    with open(chart_path+'pivot_table.html' ,'rb') as f:
        html = f.read()
    return HttpResponse(json.dumps({"code": 0, "msg": 'OK','html':html}),
                        content_type='application/json')












#  ---------------websocket长连接测试---------------------
from dwebsocket import require_websocket
def socket_test(request):
    return render(request, 'socket_test.html')

@require_websocket
def echo_once(request):
    message = request.websocket.wait()
    request.websocket.send('你好')
    time.sleep(5)
    request.websocket.send('5秒后，你好')
    time.sleep(5)
    request.websocket.send('10秒后，你好')


from dwebsocket.decorators import accept_websocket,require_websocket
def socket_test2(request):
    return render(request, 'socket_test2.html')

@accept_websocket
def echo(request):
    if not request.is_websocket():#判断是不是websocket连接
        try:#如果是普通的http方法
            message = request.GET['message']
            return HttpResponse(message)
        except:
            return render(request, 'index.html')
    else:
        n = 1
        for message in request.websocket:
            request.websocket.send('第%s次' % n)#发送消息到客户端
            n +=1
            #  ---------------websocket长连接测试---------------------