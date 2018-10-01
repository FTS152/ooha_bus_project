import dill
import numpy as np
import time, datetime
file = open('rangedData','rb')
rangedData = dill.load(file)
file = open('stopName','rb')
stopName = dill.load(file)
file = open('stopTime','rb')
stopTime = dill.load(file)

import sys
routeName = sys.argv[1]
direction = int(sys.argv[2])

part = round(len(rangedData)*0.75)
training = rangedData[0:part,:]
testing = rangedData[part:len(rangedData),:]

def mape(y_true, y_pred): 
	y_true, y_pred = np.array(y_true), np.array(y_pred)
	return np.mean(np.abs((y_true - y_pred)))

def cluster (timestamp):
	wd = datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S').weekday()
	hr = int(str(timestamp.split(' ')[1]).split(':')[0])
	if wd == datetime.datetime.strptime("2011-01-01",'%Y-%m-%d').weekday() or wd == datetime.datetime.strptime("2011-01-02",'%Y-%m-%d').weekday():
		if hr<=12 : 
			return "weekend morning"
		else:
			return "weekend afternoon"
	else:
		if hr>=7 and hr<=9: 
			return "weekday rush1" 
		if hr>=17 and hr<=19:
			return "weekday rush2"
		else:
			return "weekday off-peak"		
	
#0: sunny 1: rainy
def weather(time):
	return int(0)

def onforecast (stopVec,routeName,timestamp,direction):
	global stopName
	global stopTime
	clus = cluster(timestamp)
	select = []
	selectTime = []
	for i in range(len(stopVec)):
		if int(stopName[i,1])==int(direction) and int(stopName[i,2])==weather(timestamp) and stopName[i,3].decode('utf-8')==clus:
			select.append(stopVec[i])
	
	forecast =  np.zeros((2,len(stopVec[0])))
	for i in range(len(select)):
		for j in range(len(stopVec[0])):
			forecast[0][j] = forecast[0][j] + select[i][j]
	for j in range(len(stopVec[0])):
		if len(select) == 0:
			return "no history data!"
		else:
			forecast[0][j] = round(forecast[0][j]/len(select))

	return forecast

for i in range(len(stopName)):
	stopName[i,3] = cluster(stopName[i,0].decode('utf-8'))
result = []
for i in range(len(testing)):
	result.append(onforecast(training,routeName,stopName[part+i,0].decode('utf-8'),direction)[0])

error = []
for j in range(len(result[0])):
	y_true = []
	y_pred = []
	for i in range(len(result)):
		y_true.append(testing[i][j])
		y_pred.append(result[i][j])
	error.append(round(mape(y_true,y_pred),4))

error = np.array(error)
result = np.array(result)
a = []
b = []
for i in range(len(result[0])):
	a.append(round(np.mean(result[:,i]),4))
	b.append(round(np.mean(testing[:,i]),4))
print('測試資料平均: ',a)
print('預測資料平均: ',b)
print('平均絕對誤差: ',error)
print('誤差值平均: ',np.mean(error),'誤差值標準差: ',np.std(error))


