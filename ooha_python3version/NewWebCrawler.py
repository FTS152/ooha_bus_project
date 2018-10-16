from selenium import webdriver
import pandas as pd 

driver = webdriver.Chrome()

driver.get("https://weather.com/zh-TW/weather/hourbyhour/l/TWXX0021:1:TW")

time=driver.find_elements_by_class_name('dsx-date')

temperature= driver.find_elements_by_class_name("temp")

rain= driver.find_elements_by_xpath("//td[@class='precip']")

time2 = []
temp2 = []
rain2 = []

for i in range(0,16):
    time2.append(time[i].text)
    temp2.append(temperature[i].text[:-1])
    rain2.append(rain[i].text[:-1])
    
temp2.append(temperature[16].text[:-1])

del temp2[0]

data = {'time':time2,'temperature':temp2,'rain':rain2}
weather = pd.DataFrame(data)

with open('weather.csv','w') as file:
    weather.to_csv(file, sep='\t',encoding='utf-8')