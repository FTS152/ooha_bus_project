import sys, math, random
routeName = sys.argv[1]
direction = int(sys.argv[2])
timestamp = sys.argv[3]

import dill
import numpy as np
import time, datetime
from openpyxl import load_workbook
from sklearn.tree import tree
file = open('rangedData','rb')
rangedData = dill.load(file)
file = open('stopName','rb')
stopName = dill.load(file)
file = open('stopTime','rb')
stopTime = dill.load(file)
file = open(str(routeName)+'offprob','rb')
offprob = dill.load(file)
file = open('rangedDataFull','rb')
rangedDataFull = dill.load(file)
file = open('clf','rb')
clf = dill.load(file)

wb = load_workbook('weather.xlsx')
weatherTimestamp = []
temp = []
rain = []
for i in wb['0']['A'][1:]:
    a = str(i.value).split("T", 1)[0]
    b = str(i.value).split("T", 1)[1]
    c = b.split("+", 1)[0]
    weatherTimestamp.append(str(a+" "+c))
for i in wb['0']['B'][1:]:
    temp.append(i.value)
for i in wb['0']['C'][1:]:
    rain.append(i.value)


def cluster (timestamp,weath):
	global clf
	wd = datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S').weekday()
	hr = int(str(timestamp.split(' ')[1]).split(':')[0])
	return clf.predict([[wd,hr,weath[0],weath[1]]])[0]	
	
#0: sunny 1: rainy
def weather(time):
    global weatherTimestamp
    global temp
    global rain
    for i in range(len(weatherTimestamp)):
        data = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
        cur = datetime.datetime.strptime(weatherTimestamp[i],'%Y-%m-%d %H:%M:%S')
        if data < cur:
            result = []
            if int(rain[i]) == 0 or int(rain[i]) == -99:
                result.append(int(0))
            else:
                result.append(int(1))
            result.append(int(temp[i]))
            return result

def onforecast (stopVec,routeName,timestamp,direction):
	global stopName
	global stopTime
	clus = cluster(timestamp,weather(timestamp))
	select = []
	selectTime = []
	for i in range(len(stopName)):
		formateDate = datetime.datetime.strptime(stopName[i,0].decode('utf-8'),'%Y-%m-%d %H:%M:%S')
		cur = datetime.datetime.strptime(str(timestamp),'%Y-%m-%d %H:%M:%S')
		if int(stopName[i,1])==int(direction) and int(stopName[i,4].decode('utf-8'))==int(clus):
			select.append(stopVec[i])
			selectTime.append(stopTime[i])
	
	forecast =  np.zeros((2,len(stopVec[0])))
	hit =  np.zeros((len(stopVec[0])))
	for i in range(len(select)):
		for j in range(len(stopVec[0])):
			forecast[0][j] = forecast[0][j] + select[i][j]
			if not selectTime[i][j].decode('utf-8') == '':
				hit[j] = hit[j] + 1
				forecast[1][j] = forecast[1][j] + float(selectTime[i][j].decode('utf-8'))

	for j in range(len(stopVec[0])):
		if len(select) == 0:
			return "no history data!"
		else:
			actual = (forecast[0][j]/len(select))
			if math.modf(actual)[0] > random.random():
				forecast[0][j] = int(actual)+1
			else:
				forecast[0][j] = int(actual)
			if hit[j] !=0:
				forecast[1][j] = round(forecast[1][j]/hit[j])
	pre = ''
	for j in range(len(forecast[1])):
		if pre == '' and forecast[1][j] == 0:
			forecast[1][j] = j*30
		elif pre != '' and forecast[1][j] == 0:
			nex = j
			while forecast[1][nex] == 0:
				nex = nex + 1
				if(nex == len(forecast[1])):
					for k in range(j,nex):
						forecast[1][nex] = pre + (k+1)*30
					break
			if nex == len(forecast[1]):
				break

			las = round(forecast[1][nex])
			for k in range(j,nex):
				forecast[1][k] = round((k-j+1)*((las - pre)/(nex-j+1)) + pre)
			pre = las
			j = nex
		else:
			pre = round(forecast[1][j])
	for j in range(1,len(forecast[1])):
		if forecast[1][j] > forecast[1][j-1]:
			continue
		else:
			forecast[1][j] = forecast[1][j-1] +30

	return forecast

def getPass(on,prob):
	off = np.zeros((len(on)))
	tempProb = np.zeros(len(prob))
	for j in range(len(tempProb)):
		tempProb[j] = prob[j]
	for j in range(len(on)):
		tempProb[j] = 0
		if sum(tempProb) == 0:
			continue
		else:
			tempProb = tempProb/sum(tempProb)
		if (on[j]) == 0 or j == len(on)-1:
			continue
		for k in range(int(on[j])):
			x = np.random.choice(len(on), size = 1, replace = False, p = tempProb)
			off[x]=off[x]+1

	passenger = np.zeros((len(on)))
	for j in range(len(on)):
		if(j==0):
			passenger[j]=on[j]-off[j]
		else:
			passenger[j]=passenger[j-1] + on[j] - off[j]      

	return(passenger)

print(rangedData[0])
x = onforecast(rangedData,routeName,timestamp,direction)

a = []
for i in rangedDataFull:
	forecast = onforecast(i,routeName,timestamp,direction)[0]
	a.append(getPass(forecast,offprob))

for i in range(len(a)):
	print(a[i])
print(x[1])

