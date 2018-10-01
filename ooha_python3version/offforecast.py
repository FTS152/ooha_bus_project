

import sys
routeName = sys.argv[1]
direction = int(sys.argv[2])

x=[]
x.append(input('第一大站: '))
x.append(input('第二大站: '))
x.append(input('第三大站: '))

import dill
file = open('rangedData','rb')
rangedData = dill.load(file)
file = open('stopName','rb')
stopName = dill.load(file)

from openpyxl import load_workbook
import numpy as np
wb = load_workbook(str(routeName)+'off.xlsx')
offTrue0 = []
offTrue1 = []

#need edit when route is different
for i in wb['0']['B'][1:]:
	offTrue0.append(i.value)
for i in wb['1']['B'][1:]:
	offTrue1.append(i.value)

def predict (stopVec,offTrue,direction,big):
	tempOff = np.zeros(len(stopVec[0,:]))
	x[0] = int(big[0]) -1
	x[1] = int(big[1]) -1
	x[2] = int(big[2]) -1

	tempOff[x[0]]=0.001
	tempOff[x[1]]=0.001
	tempOff[x[2]]=0.701
	a = (1-sum(tempOff))
	b = len(tempOff)-len(x)
	counter = 0

	for i in range(len(tempOff)):
		for j in range(len(x)):
			if i == x[j]: 
				break
			if j == len(x)-1:
				tempOff[i]=a/b
				counter=counter+1
	leastError = errorCal(stopVec,tempOff,offTrue,direction)
	bestTemp = tempOff.copy()
	for m in range(7):
		for n in range(m,7):
			tempOff[x[2]] = tempOff[x[2]] - 0.1
			tempOff[x[1]] = tempOff[x[1]] + 0.1
			newError = errorCal(stopVec,tempOff,offTrue,direction)
			if newError < leastError:
				bestTemp = tempOff.copy()
				leastError = newError
				print(newError)

		tempOff[x[0]] = tempOff[x[0]]+0.1
		tempOff[x[1]] = tempOff[x[1]]-0.1
		temp = tempOff[x[1]]
		tempOff[x[1]] = tempOff[x[2]]
		tempOff[x[2]] = temp
	return bestTemp


def errorCal(stopVec,tempOff,offTrue,direction):
	global stopName
	Error=0
	for i in range(len(stopVec)):
		current = np.zeros(len(stopVec[0]))
		tempTempOff = tempOff.copy()
		if int(stopName[i,1]) != direction:
			continue
		for j in range(len(stopVec[0])):
			tempTempOff[j] = 0
			if sum(tempTempOff) == 0:
				continue
			else:
				tempTempOff = tempTempOff/sum(tempTempOff)
			if (stopVec[i,j]) == 0 or j == len(stopVec[0])-1:
				continue
			for k in range(int(stopVec[i,j])):
				x = np.random.choice(len(stopVec[0]), size = 1, replace = False, p = tempTempOff)
				current[x]=current[x]+1

		if(sum(current)!=0):
			current = current/sum(current)
		for i in range(len(current)):

			Error = Error + pow((current[i] - offTrue[i]),2)

	return Error


def getPass(on,prob,direction):
	global stopName 
	off = np.zeros((len(on[:,0]),len(on[0,:])))
	for i in range(len(on[:,0])):
		tempProb = np.zeros(len(prob))
		for j in range(len(tempProb)):
			tempProb[j] = prob[j]
		if int(stopName[i,1]) != direction:
			continue
		for j in range(len(on[0,:])):
			tempProb[j] = 0
			if sum(tempProb) == 0:
				continue
			else:
				tempProb = tempProb/sum(tempProb)
			if (on[i,j]) == 0 or j == len(on[0,:])-1:
				continue
			for k in range(int(on[i,j])):
				x = np.random.choice(len(on[0,:]), size = 1, replace = False, p = tempProb)
				off[i,x]=off[i,x]+1

	passenger = np.zeros((len(on[:,0]),len(on[0,:])))
	for i in range(len(on[:,0])):
		if int(stopName[i,1]) != direction:
			continue
		for j in range(len(on[0,:])):
			if(j==0):
				passenger[i,j]=on[i,j]-off[i,j]
			else:
				passenger[i,j]=passenger[i,j-1] + on[i,j] - off[i,j]      

	return(passenger)


if(direction == 0):
	prob = predict(rangedData,offTrue0,direction,x)
else:
	prob = predict(rangedData,offTrue1,direction,x)

print(prob)

file = open(str(routeName)+'offprob', 'wb')
dill.dump(prob,file)
