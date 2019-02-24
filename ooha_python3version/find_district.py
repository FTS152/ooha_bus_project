import requests, json,dill
from xml.etree import ElementTree
from datetime import datetime
from time import mktime
import base64
from pprint import pprint
from hashlib import sha1
import hmac
from wsgiref.handlers import format_date_time
from requests import request

#appid跟key在PTX申請
app_id = 'd9d85ed532d04b4a9509c9abf08a0c6a'
app_key = '1ZBWFCnRevwkHLzYhXvUAqvZEwU'

class Auth():

    def __init__(self, app_id, app_key):
        self.app_id = app_id
        self.app_key = app_key

    def get_auth_header(self):
        xdate = format_date_time(mktime(datetime.now().timetuple()))
        hashed = hmac.new(self.app_key.encode('utf8'), ('x-date: ' + xdate).encode('utf8'), sha1)
        signature = base64.b64encode(hashed.digest()).decode()

        authorization = 'hmac username="' + self.app_id + '", ' + \
                        'algorithm="hmac-sha1", ' + \
                        'headers="x-date", ' + \
                        'signature="' + signature + '"'
        return {
            'Authorization': authorization,
            'x-date': format_date_time(mktime(datetime.now().timetuple())),
            'Accept - Encoding': 'gzip'
        }
    
headerMOTC = Auth(app_id, app_key)
Url="https://ptx.transportdata.tw/MOTC/v2/Bus/DisplayStopOfRoute/City/NewTaipei/920?$format=JSON"
a=request('get',Url,headers=headerMOTC.get_auth_header())
reqsjson = json.loads(a.text)


def busStopAndDistrict(busNum,city,direction,app_id,app_key):
    #appid在PTX申請
    #輸入：busNum車號(ex:'920') city所在縣市(ex:'NewTaipei') direction去回程（ex: 0,1）
    #輸出：站牌對應的區
    #API來源：https://ptx.transportdata.tw/MOTC/Swagger/#!/CityBusApi/CityBusApi_DisplayStopOfRoute_0
    
    ##首先拿到站牌
    Url="https://ptx.transportdata.tw/MOTC/v2/Bus/DisplayStopOfRoute/City/"+city+"/"+busNum+"?$format=JSON"
    headerMOTC = Auth(app_id, app_key)
    a=request('get',Url,headers=headerMOTC.get_auth_header())
    reqsjson = json.loads(a.text)
    stop={}
    i=0
    for reqsjson2 in reqsjson[direction]['Stops']:
        stop[i]=(reqsjson2['StopName']['Zh_tw'],reqsjson2['StopPosition']['PositionLat'],reqsjson2['StopPosition']['PositionLon'])
        i=i+1
    
    result={}
    ##找區
    for i in stop:
        latitude = stop[i][1]
        longtitude = stop[i][2]
        Url="https://api.nlsc.gov.tw/other/TownVillagePointQuery/"+str(longtitude)+"/"+str(latitude)
        a=requests.get(Url)
        tree = ElementTree.fromstring(a.content)
        result[i]=(stop[i][0],tree[3].text)
    
    with open(busNum+"_district_"+str(direction),"wb") as file:
        dill.dump(result,file)
        
    
    return (result)
 
 ##使用例子：
##ans1=busStopAndDistrict('920','NewTaipei',0,app_id,app_key)
##ans2=busStopAndDistrict('920','NewTaipei',1,app_id,app_key)
##id跟key寫在最前面

