# coding: utf-8

# In[148]:


#data must meet the following data rule
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
# output: return a dataframe in which unneeded data are omitted

import dill
import pandas as pd
import numpy 
from operator import itemgetter
import sys

#******important****** the 'results' in open() can be replaced by given fileName. User can change it.
file = open('results','rb')
#remember to close the file
results = dill.load(file)
inputData = pd.DataFrame(results)


ageStd = int(sys.argv[1])
timeStd = int(sys.argv[2])
testN = int(sys.argv[3])


# In[143]:


def cleanData(inputData,ageStandard,timeStandard,testNum):
    inputData=inputData.sort_values(by=[0,1,7,8]) #sort data by 0 route number 1 player info 7 date 8 time（轉置）
    inputData=inputData.reset_index()
    arrayNum = len(inputData.index)
    inputData=inputData.T
    checkIfDelete = [0]*arrayNum # array is to see if given data is to be deleted
    time = numpy.zeros((arrayNum, 4))

    
    for i in range(0,arrayNum):#deal with time
        temp = inputData[i][8].split(':')
        time[i][1] = float(temp[0])#hour
        time[i][2] = float(temp[1])#minute
        time[i][3] = float(temp[2])#second

    for i in range(0,arrayNum-1):
        if(checkIfDelete[i]==1):
            continue
        if((i+testNum)>arrayNum-1):
            loopNum = arrayNum-1-i
           
        else:
            loopNum = testNum
        
        for j in range(1,loopNum+1):
            
            if(checkIfDelete[i+j]==1):
                continue
            if(inputData[i][1]!=inputData[i+j][1]):
                continue
            if(inputData[i][0]!=inputData[i+j][0]):
                continue
            if(inputData[i][6]!=inputData[i+j][6]):
                continue
            if(inputData[i][4]!=inputData[i+j][4]):
                continue
            if(inputData[i][7]!=inputData[i+j][7]):
                continue
            if(timeDifference(time,i,j)>timeStandard):
                continue
            if(ageDifference(inputData,i,j)>ageStandard):
                continue
            
            checkIfDelete[i+j] = 1

    deleteIndex=[]
    for i in range(0,arrayNum):
        if(checkIfDelete[i]==1):
            deleteIndex.append(i)
            
    resultData = inputData.T.drop(deleteIndex)
    resultData=resultData.reset_index()
    del resultData["level_0"]
    del resultData["index"]
    
    
    arrayNum2 = len(resultData.index)
    
    resultArray=[]
    for i in range(arrayNum2):
        resultArray.append(resultData.T[i].tolist())
    
    return resultArray


def timeDifference(time, i, j):
    difference = (time[i+j,1]-time[i,1])*3600 + (time[i+j,2]-time[i,2])*60 + time[i+j,3]-time[i,3]
    if(i==0):
        print(difference)
    return difference

def ageDifference(inputData,i,j):
    difference = abs(inputData[i+j][5]-inputData[i][5])
    return difference


result=cleanData(inputData,ageStd,timeStd,testN)

file.close()
with open('results', 'wb') as file:
    dill.dump(result,file)







