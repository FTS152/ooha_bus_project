import dill
import numpy as np
import time, datetime
from sklearn.tree import tree
from sklearn.cluster import KMeans
from openpyxl import load_workbook
import sys
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

def rush(day,hour):
    if day != datetime.datetime.strptime("2011-01-01",'%Y-%m-%d').weekday() and day != datetime.datetime.strptime("2011-01-02",'%Y-%m-%d').weekday():
        if (hour>=7 and hour<=9) or (hour>=17 and hour<=19): 
            return int(1) 
        else:
            return int(0)
    else:
        return int(0)

def cluster (timestamp,rain,temp):
	global clf
	global bestClus
	wd = datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S').weekday()
	hr = int(str(timestamp.split(' ')[1]).split(':')[0])
	k = clf.predict([[wd,hr,rain,temp,rush(wd,hr)]])[0]
	return bestClus.cluster_centers_[int(k)].tolist()

def mape(y_true, y_pred): 
	y_true, y_pred = np.array(y_true), np.array(y_pred)
	return np.mean(np.abs((y_true - y_pred)))

def cluster2 (timestamp):
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
	clus = cluster2(timestamp)
	select = []
	selectTime = []
	for i in range(len(stopVec)):
		if int(stopName[i,1])==int(direction) and int(stopName[i,2])==weather(timestamp) and stopName[i,4].decode('utf-8')==clus:
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
	stopName[i,4] = cluster2(stopName[i,0].decode('utf-8'))
result = []
for i in range(len(testing)):
	result.append(onforecast(training,routeName,stopName[part+i,0].decode('utf-8'),direction)[0])

clusResult = []
for i in range(1,20):
     clusResult.append(KMeans(n_clusters = i).fit(training).inertia_)

avg = clusResult[0]/len(training) #average within error
for i in range(18):
    diff = clusResult[i]-clusResult[i+1]
    if diff<avg or i==17:
        bestClusNum = i+1
        break

bestClus = KMeans(n_clusters = bestClusNum).fit(training)
print('最佳群數: ',bestClusNum)
treeX = np.zeros((len(training),5))
treeY = np.zeros((len(training)))

for i in range(len(training)):
    treeX[i][0] = datetime.datetime.strptime(stopName[i,0].decode('utf-8'),'%Y-%m-%d %H:%M:%S').weekday()
    treeX[i][1] = int(str(stopName[i,0].decode('utf-8').split(' ')[1]).split(':')[0])
    treeX[i][2] = stopName[i,2]
    treeX[i][3] = stopName[i,3]
    treeX[i][4] = rush(treeX[i][0],treeX[i][1])
    treeY[i] = bestClus.labels_[i]
    stopName[i][4] = bestClus.labels_[i]
clf = tree.DecisionTreeClassifier()
print(treeX)
clf = clf.fit(treeX, treeY)


result2 = []
for i in range(len(testing)):
	result2.append(cluster(stopName[part+i,0].decode('utf-8'),stopName[part+i,2].decode('utf-8'),stopName[part+i,3].decode('utf-8')))

error = []
for j in range(len(result[0])):
	y_true = []
	y_pred = []
	for i in range(len(result)):
		y_true.append(testing[i][j])
		y_pred.append(result[i][j])
	error.append(round(mape(y_true,y_pred),4))

error2 = []
for j in range(len(result2[0])):
	y_true = []
	y_pred = []
	for i in range(len(result2)):
		y_true.append(testing[i][j])
		y_pred.append(result2[i][j])
	error2.append(round(mape(y_true,y_pred),4))

error = np.array(error)
error2 = np.array(error2)
result = np.array(result)
result2 = np.array(result2)
a = []
b = []
for i in range(len(result[0])):
	a.append(round(np.mean(result[:,i]),4))
	b.append(round(np.mean(testing[:,i]),4))
print('測試資料平均: ',a)
print('預測資料平均: ',b)
print('平均絕對誤差(人工): ',error)
print('平均絕對誤差(分群): ',error2)
print('誤差值平均(人工): ',np.mean(error),'誤差值標準差: ',np.std(error))
print('誤差值平均(分群): ',np.mean(error2),'誤差值標準差: ',np.std(error2))