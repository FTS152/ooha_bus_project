import requests, json,dill
from selenium import webdriver
import time


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
        
    #再把站牌經緯度對應到地址最後取出區
    #這裡用了"http://itman123.com/show-google-map-latlng.html"的功能，因為google api使用要付費
    
    driver = webdriver.Chrome() 
    driver.get("http://itman123.com/show-google-map-latlng.html")
    result={}
    num=0
    for i in stop:
        print(stop[i][0])
        latitude = stop[i][1]
        longtitude = stop[i][2]
        driver.find_element_by_id("lat2").send_keys(str(latitude))
        driver.find_element_by_id("lng2").send_keys(str(longtitude))
        driver.find_element_by_xpath("//input[@value='經緯度查地址']").click()
        ##要停一下不然短時間要太多會被強制跳出
        time.sleep(2)
        ##address存單個站牌的完整地址
        address=driver.find_element_by_xpath("//input[@id='address2']").get_attribute("value")
        driver.find_element_by_id("lat2").clear()
        driver.find_element_by_id("lng2").clear()
        
        ##從完整地址擷取區
        j=0
        district=""
        for k in address:
            if (k=='區'):
                district=address[j-2]+address[j-1]+k
                break
            j=j+1
            
        
        result[i]=(stop[i][0],district)

        print(address)
        print(district)
        num=i
    
    with open(busNum+"_district_"+str(direction),"wb") as file:
        dill.dump(result,file)

    return ('ok')
 
 ##使用例子：
##ans1=busStopAndDistrict('920','NewTaipei',0)
##ans2=busStopAndDistrict('920','NewTaipei',1)


