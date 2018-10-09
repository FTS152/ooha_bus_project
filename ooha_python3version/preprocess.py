import dill
import numpy as np
import time, datetime
file = open('results','rb')
number = dill.load(file)

import sys
routeName = sys.argv[1]
direction = int(sys.argv[2])

import json
with open('./MOTC/'+routeName+'.json', 'r', encoding="utf-8") as f:
    data = json.load(f)
stopLat = []
stopLon = []
if direction == int(0):
    for i in data[0]['Stops']:
        stopLat.append(i['StopPosition']['PositionLat'])
        stopLon.append(i['StopPosition']['PositionLon'])
else:
    for i in data[1]['Stops']:
        stopLat.append(i['StopPosition']['PositionLat'])
        stopLon.append(i['StopPosition']['PositionLon'])
#index of data: 6=direction,7=date,8=time
number = sorted(number,key = lambda x: (str(x[1]), str(x[7]),str(x[8])))

stopName = np.empty((len(number),4),dtype='a32')
stopTime = np.empty((len(number),len(stopLat)),dtype='a32')
rangedDataFull = np.zeros((6,len(number),len(stopLat))) #0: little m 1: young m 2: old m 3: little f 4: young f 5: old f

def pos(lat,lon,stopLat,stopLon):
    M = 1
    for i,j,k in zip(stopLat,stopLon,range(len(stopLat))):
        distance = pow((lat - i),2) + pow((lon - j),2)
        if(distance < M):
            stop = k
            M = distance
    return int(stop)

#0: sunny 1: rainy
def weather(time):
    return int(0)

def passenger(sex,age):
    if int(age)<25:
        if sex == 'male':
            return int(0)
        else:
            return int(3)
    elif int(age)<45 and int(age)>=25:
        if sex == 'male':
            return int(1)
        else:
            return int(4)
    else:
        if sex == 'male':
            return int(2)
        else:
            return int(5)


def schedule(data):
    global stopTime
    global stopName
    global rangedDataFull
    stopInfo = np.zeros((len(data),len(stopLat)))
    counter = -1

    for i in range(0,len(data)):
        if i!=0:
            cur = datetime.datetime.strptime(data[i][8],'%H:%M:%S')
            pre = datetime.datetime.strptime(data[i-1][8],'%H:%M:%S')
        else:
            cur = datetime.datetime.strptime(data[i][8],'%H:%M:%S')
            pre = datetime.datetime.strptime(data[i][8],'%H:%M:%S')            
        if data[i][7]!=data[i-1][7] or data[i][6]!=data[i-1][6] or data[i][1]!=data[i-1][1] or (cur-pre).seconds>3600 or i == 0:
            counter = counter + 1
            now = 0
            stopName[counter][0] = str(data[i][7])+" "+str(data[i][8])
            stopName[counter][1] = str(data[i][6])
            stopName[counter][2] = weather(stopName[counter][0])       
        a = pos(data[i][2],data[i][3],stopLat,stopLon)
        stopInfo[counter][a] = stopInfo[counter][a]+1
        rangedDataFull[passenger(data[i][4],data[i][5])][counter][a] = rangedDataFull[passenger(data[i][4],data[i][5])][counter][a] + 1
        if(stopTime[counter][a].decode("utf-8") == '' and a >= now):
            stopTime[counter][a] = str(data[i][8])
            now = a

    less = []
    for i in range(len(stopInfo)):
        if sum(stopInfo[i,:]) <= 15:
            less.append(i) 
    stopInfo = np.delete(stopInfo, less, 0)
    stopTime = np.delete(stopTime, less, 0)
    stopName = np.delete(stopName, less, 0)
    r = np.zeros((6,len(data)-len(less),len(stopLat)))
    for i in range(len(rangedDataFull)):
        r[i] = np.delete(rangedDataFull[i], less, 0)
    rangedDataFull = r

    for i in range(len(stopTime)):
        for j in range(len(stopTime[0])):
            if not stopTime[i,j].decode("utf-8") == '':
                start = datetime.datetime.strptime(stopTime[i,j].decode("utf-8"),'%H:%M:%S')
                startStop = j
                break
        for j in range(startStop,len(stopTime[0])):
            if stopTime[i,j].decode("utf-8") == '':
                continue
            cur = datetime.datetime.strptime(stopTime[i,j].decode("utf-8"),'%H:%M:%S')
            stopTime[i,j] = (cur - start).seconds + 30*startStop

        pre = ''
        for j in range(len(stopTime[0])):
            if pre == '' and stopTime[i,j].decode("utf-8") == '':
                continue
            elif pre != '' and stopTime[i,j].decode("utf-8") == '':
                nex = j
                while stopTime[i,nex].decode("utf-8") == '':
                    nex = nex + 1
                    if(nex == len(stopTime[0])):
                        break
                if nex == len(stopTime[0]):
                    break

                las = float(stopTime[i,nex])
                for k in range(j,nex):
                    stopTime[i,k] = float((k-j+1)*((las - pre)/(nex-j+1)) + pre)
                pre = las
                j = nex
            else:
                pre =float(stopTime[i,j])

    return stopInfo

rangedData = schedule(number)

import dill
file = open('rangedData', 'wb')
dill.dump(rangedData,file)
file = open('stopName', 'wb')
dill.dump(stopName,file)
file = open('rangedDataFull', 'wb')
dill.dump(rangedDataFull,file)
file = open('stopTime', 'wb')
dill.dump(stopTime,file)
file.close()