import dill
import numpy as np
import time, datetime
from sklearn.tree import tree
from sklearn.cluster import KMeans
from openpyxl import load_workbook
import sys
routeName = sys.argv[1]
direction = int(sys.argv[2])

file = open('rangedData','rb')
rangedData = dill.load(file)
file.close()
file = open('stopName','rb')
stopName = dill.load(file)
file.close()

wb = load_workbook('weather.xlsx')
timestamp = []
temp = []
rain = []
for i in wb['0']['A'][1:]:
    a = str(i.value).split("T", 1)[0]
    b = str(i.value).split("T", 1)[1]
    c = b.split("+", 1)[0]
    timestamp.append(str(a+" "+c))
for i in wb['0']['B'][1:]:
    temp.append(i.value)
for i in wb['0']['C'][1:]:
    rain.append(i.value)

def rush(day,hour):
    if day != datetime.datetime.strptime("2011-01-01",'%Y-%m-%d').weekday() and day != datetime.datetime.strptime("2011-01-02",'%Y-%m-%d').weekday():
        if (hour>=7 and hour<=9) or (hour>=17 and hour<=19): 
            return int(1) 
        else:
            return int(0)
    else:
        return int(0)

#normalize
for i in range(len(rangedData)):
    a = []
    for j in range(len(rangedData[0])):
        a.append(rangedData[i][j]/sum(rangedData[i]))
    rangedData[i] = a

part = round(len(rangedData)*0.8)
training = rangedData[0:part,:]
testing = rangedData[part:len(rangedData),:]

result = []
for i in range(1,20):
     result.append(KMeans(n_clusters = i).fit(training).inertia_)

avg = result[0]/len(training) #average within error
for i in range(18):
    diff = result[i]-result[i+1]
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
clf = clf.fit(treeX, treeY)


def cluster (timestamp,rain,temp):
	global clf
	wd = datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S').weekday()
	hr = int(str(timestamp.split(' ')[1]).split(':')[0])
	return clf.predict([[wd,hr,rain,temp,rush(wd,hr)]])[0]			

ans = []
for i in range(len(testing)):
	M = 1000000
	for j in range(len(bestClus.cluster_centers_)):
		ss = 0
		for k in range(len(testing[0])):
			ss = ss + pow(testing[i][k] - bestClus.cluster_centers_[j][k],2)
		if ss < M:
			M = ss
			center = j
	ans.append(center)


forecast = []
for i in range(len(testing)):
	forecast.append(int(cluster(stopName[part+i,0].decode('utf-8'),stopName[part+i,2].decode('utf-8'),stopName[part+i,3].decode('utf-8'))))

res = 0
for i in range(len(testing)):
	if ans[i]==forecast[i]:
		res = res + 1 


print('答案:  ',ans)
print('預測:  ',forecast)
print('預測正確/全部: ',res,"/",len(testing))

