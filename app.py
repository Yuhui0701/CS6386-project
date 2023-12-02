# -*- coding=utf8 -*-
import csv
import pandas as pd


from flask import Flask, Response, render_template
from flask import request
from flask_cors import CORS



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
def readData():
    df = pd.read_csv('Auto Sales data.csv')
    # 删除包含缺失值的行
    df.dropna(inplace=True)
    return df
def cityPrice():
    df=readData()
    product_stats = df.groupby('PRODUCTLINE').agg({'SALES': 'sum', 'ORDERNUMBER': 'count'})

    # 添加各组平均销售额列
    product_stats['AVG_SALES'] = product_stats['SALES'] / product_stats['ORDERNUMBER']
    cityPrice = {
        'title': [i for i in product_stats.index],
        'data': [int(i) for i in product_stats['ORDERNUMBER']],
        'price': [int(i) for i in product_stats['AVG_SALES']]
    }
    return  cityPrice
def inxeData():
    df=readData()
    maxPrice = df['SALES'].max()
    menPrice = round(df['SALES'].mean(), 2)
    print(maxPrice,menPrice)
    return {'maxPrice':int(maxPrice),'menPrice':int(menPrice)}

def getPie():
    df=readData()
    # 统计各地区的用人数量
    status_amounts = df.groupby('STATUS')['SALES'].sum()

    pieData = []
    for key ,value in zip(status_amounts.index,status_amounts.values):
        item={}
        item['name']=key
        item['value']=round(value, 2)
        pieData.append(item)


    return  pieData
@app.route("/api/data", methods=['GET'])
def barData():
    df = readData()
    # 计算每个客户的平均购买间隔和回购率
    df['ORDERDATE'] = pd.to_datetime(df['ORDERDATE'], dayfirst=True)

    # 计算每个客户的回购率
    df['NEXT_ORDERDATE'] = df.groupby('CUSTOMERNAME')['ORDERDATE'].shift(-1)
    df['DAYS_TO_NEXTORDER'] = df['NEXT_ORDERDATE'] - df['ORDERDATE']
    df['DAYS_TO_NEXTORDER'] = df['DAYS_TO_NEXTORDER'].dt.days

    # 计算每个客户的平均购买间隔和回购率
    cust_avg_days = df.groupby(['CUSTOMERNAME', 'PRODUCTLINE'])['DAYS_SINCE_LASTORDER'].mean()
    cust_repurchase_rate = df.groupby(['CUSTOMERNAME', 'PRODUCTLINE']).apply(
        lambda x: (x['DAYS_TO_NEXTORDER'] <= 30).sum() / len(x))

    # 分析不同产品线的平均生产间隔
    avg_days_by_produceline = df.groupby('PRODUCTLINE')['DAYS_SINCE_LASTORDER'].mean()


    cityBarMin = {
        'title': [i for i in avg_days_by_produceline.index],
        'data': [i for i in avg_days_by_produceline.values]
    }



    return {'cityBarMin':cityBarMin,'cityBarMax':cityBarMin,'pieData': getPie(),  }
@app.route("/api/data/const", methods=['GET'])
def dataConst():
    df=readData()
    country_stats = df.groupby('COUNTRY').agg({'SALES': 'sum', 'ORDERNUMBER': 'sum'})
    top_10_countries = country_stats.nlargest(10, 'SALES')
    counts=[]
    for key, value in zip(top_10_countries.index, top_10_countries['SALES']):
        item = {}
        item['name'] = key
        item['value'] = int(value)
        counts.append(item)
    return {'data':counts}
@app.route("/api/data/fiveJobs", methods=['GET'])
def fiveJobs():
    df=readData()
    product_stats = df.groupby('PRODUCTLINE').agg({'SALES': 'sum', 'ORDERNUMBER': 'count'})

    # 添加各组平均销售额列
    product_stats['AVG_SALES'] = product_stats['SALES'] / product_stats['ORDERNUMBER']

    five_jobs = {
        'title': [i for i in product_stats.index],
        'data': [int(i) for i in product_stats['SALES']]
    }

    return {'five_jobs': five_jobs, }
@app.route("/api/data/cityPrice", methods=['GET'])
def cityprice():

    return {'cityPrice': cityPrice()}



@app.route('/',methods=['GET']) # 主界面
def index():
   data=inxeData()
   print(data)
   return  render_template('index.html',data=data)




if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
