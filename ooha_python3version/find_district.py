import requests, json,dill
from xml.etree import ElementTree


def busStopAndDistrict(busNum,city,direction):
    #輸入：busNum車號(ex:'920') city所在縣市(ex:'NewTaipei') direction去回程（ex: 0,1）
    #輸出：站牌對應的區
    #API來源：https://ptx.transportdata.tw/MOTC/Swagger/#!/CityBusApi/CityBusApi_DisplayStopOfRoute_0
    
    ##首先拿到站牌
    Url="https://ptx.transportdata.tw/MOTC/v2/Bus/DisplayStopOfRoute/City/"+city+"/"+busNum+"?$format=JSON"
    header1={'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_7; da-dk) AppleWebKit/533.21.1 (KHTML, like Gecko) Version/5.0.5 Safari/533.21.1'}
    a=requests.get(Url,headers=header1)
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
        print(Url)
        a=requests.get(Url,headers=header1)
        tree = ElementTree.fromstring(a.content)
        result[i]=(stop[i][0],tree[3].text)
    
    with open(busNum+"_district_"+str(direction),"wb") as file:
        dill.dump(result,file)
        
   
    
    return ('ok')
 
 ##使用例子：
##ans1=busStopAndDistrict('920','NewTaipei',0)
##ans2=busStopAndDistrict('920','NewTaipei',1)


