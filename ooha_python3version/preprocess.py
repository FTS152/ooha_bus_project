import dill
file = open('results','rb')
number = dill.load(file)

#need edit when direction or route is different
import json
with open('./MOTC/920.json', 'r', encoding="utf-8") as f:
    data = json.load(f)
stopLat = []
stopLon = []
for i in data[1]['Stops']:
    stopLat.append(i['StopPosition']['PositionLat'])
    stopLon.append(i['StopPosition']['PositionLon'])
    
data = []
for i in range(len(number[0])):
    if(number[0][i]=='920'):
        data.append([number[0][i],number[1][i],number[2][i],number[3][i],number[4][i],number[5][i],number[6][i],number[7][i],number[8][i]])

#index of data: 6=direction,7=date,8=time
data = sorted(data,key = lambda x: (x[1], x[7], x[8]))

import numpy as np
import time

def pos(lat,lon,stopLat,stopLon):
    M = 1
    for i,j,k in zip(stopLat,stopLon,range(1,len(stopLat)+1)):
        distance = pow((lat - i),2) + pow((lon - j),2)
        if(distance < M):
            stop = k
            M = distance
    return int(stop)


def schedule(data):
    stopInfo = np.zeros((len(data),len(data)))
    global stopName
    stopName = []
    counter = 0
    stopName.append(str(data[0][7])+" "+str(data[0][8])+" "+str(data[0][6]))
    stopInfo[0,0] = pos(data[0][2],data[0][3],stopLat,stopLon)
    for i in range(1,len(data)):
        if data[i][7]!=data[i-1][7] or data[i][6]!=data[i-1][6] or int(data[i][8].split(':')[0])-int(data[i-1][8].split(':')[0])>2:
            counter = counter + 1
        for j in range(len(stopInfo)):
            if not stopInfo[counter,j]:
                if j == 0:
                    stopName.append(str(data[i][7])+" "+str(data[i][8])+" "+str(data[i][6]))
                stopInfo[counter,j] = pos(data[i][2],data[i][3],stopLat,stopLon)
                break
    for i in range(len(stopInfo)):
        if sum(stopInfo[i,:]) == 0:
            bottom = i
            break
    for i in range(len(stopInfo)):
        if sum(stopInfo[:,i]) == 0:
            right = i
            break
    stopInfoZero = np.zeros((bottom,right))
    for i in range(bottom):
        for j in range(right):
            stopInfoZero[i,j]=stopInfo[i,j]
            
            
    return stopInfoZero

def passVector(stopInfo):
    global stopName
    stopVec = np.zeros((len(stopInfo),len(stopLat)))
    delete = []
    for i in range(len(stopInfo)):
        for j in range(len(stopInfo[0])):
            if (stopInfo[i,j]==0):
                break
            else:
                stopVec[i,int(stopInfo[i,j])-1]=int(stopVec[i,int(stopInfo[i,j])-1])+1
        #print(sum(stopVec[i,:]))
        if (sum(stopVec[i,:])<=2):
            delete.append(i)

    stopVec = np.delete(stopVec,delete,0)
    for i in sorted(delete, reverse=True): 
        del stopName[i]

    return(stopVec)
            
            
cleanData = passVector(schedule(data))

import dill
file = open('cleanData', 'wb')
dill.dump(cleanData,file)
file = open('stopName', 'wb')
dill.dump(stopName,file)