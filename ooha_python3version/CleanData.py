
# coding: utf-8

#csv file column
#0 : route number
#1 : player info(car number)
#2 : latitude
#3 : longtitude
#4 : gender
#5 : avgAge
#6 : direction
#7 : date
#8 : time

# argument: data as a matrix or dataframe , given time standard(in seconds), testNum(number)
# process: check if a particular row of data should be deleted
# output: return a dataframe in which unneeded data are omitted.


import dill
import pandas as pd
import numpy
def cleanData(inputData,ageStandard,timeStandard,testNum):
    inputData=inputData.T.sort_values(by=[0,1,7,8]) #sort data by 0 route number 1 player info 7 date 8 time
    inputData=inputData.reset_index()  
    inputData=inputData.T
    arrayNum = len(inputData.T.index)
    checkIfDelete = [0]*arrayNum # array is to see if given data is to be deleted
    time = numpy.zeros((arrayNum, 4))
    
    
    for i in range(0,arrayNum):#deal with time
        temp = inputData[i][8].split(':')
        time[i][1] = float(temp[0])#hour
        time[i][2] = float(temp[1])#minute
        time[i][3] = float(temp[2])#second

    for i in range(0,arrayNum-1):
        if(checkIfDelete[i]==1): #if the data is already deleted ,skip
            continue
        if((i+testNum)>arrayNum-1): #if test number is over the data num,skip
            loopNum = arrayNum-1-i
           
        else:
            loopNum = testNum
        
        for j in range(1,loopNum+1):
            
            if(checkIfDelete[i+j]==1): #if the data is already deleted ,skip
                continue
            if(inputData[i][1]!=inputData[i+j][1]): # car number different
                continue
            if(inputData[i][0]!=inputData[i+j][0]): # route number different
                continue
            if(inputData[i][6]!=inputData[i+j][6]): # direction different
                continue
            if(inputData[i][4]!=inputData[i+j][4]): # gender different
                continue
            if(inputData[i][7]!=inputData[i+j][7]): # date different
                continue
            if(timeDifference(time,i,j)>timeStandard): # time difference larger than given range
                continue
            if(ageDifference(inputData,i,j)>ageStandard): # age difference larger than given range
                continue
            
            checkIfDelete[i+j] = 1 #if all conditions are passed ,label the data as to be deleted

    deleteIndex=[]
    for i in range(0,arrayNum):
        if(checkIfDelete[i]==1):
            deleteIndex.append(i)
            
    resultData = inputData.T.drop(deleteIndex)
    resultData=resultData.reset_index()
    del resultData["level_0"]
    del resultData["index"]
            
    return resultData



def timeDifference(time, i, j):
    difference = (time[i+j,1]-time[i,1])*3600 + (time[i+j,2]-time[i,2])*60 + time[i+j,3]-time[i,3]
    return difference
    


def ageDifference(inputData,i,j):
    difference = abs(inputData[i+j][5]-inputData[i][5])
    return difference




