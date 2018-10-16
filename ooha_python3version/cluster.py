import dill
import numpy as np
import time, datetime
from sklearn.cluster import KMeans
from sklearn.tree import tree
file = open('rangedData','rb')
rangedData = dill.load(file)
file.close()
file = open('stopName','rb')
stopName = dill.load(file)
file.close()

#normalize
for i in range(len(rangedData)):
    a = []
    for j in range(len(rangedData[0])):
        a.append(rangedData[i][j]/sum(rangedData[i]))
    rangedData[i] = a

result = []
for i in range(1,20):
     result.append(KMeans(n_clusters = i).fit(rangedData).inertia_)

avg = result[0]/len(rangedData) #average within error
for i in range(19):
    diff = result[i]-result[i+1]
    if diff<avg or i==18:
        bestClusNum = i+1
        break

bestClus = KMeans(n_clusters = bestClusNum).fit(rangedData)
print('best k: ',bestClusNum)
treeX = np.zeros((len(stopName),4))
treeY = np.zeros((len(stopName)))

for i in range(len(stopName)):
    treeX[i][0] = datetime.datetime.strptime(stopName[i,0].decode('utf-8'),'%Y-%m-%d %H:%M:%S').weekday()
    treeX[i][1] = int(str(stopName[i,0].decode('utf-8').split(' ')[1]).split(':')[0])
    treeX[i][2] = stopName[i,2]
    treeX[i][3] = stopName[i,3]
    treeY[i] = bestClus.labels_[i]
    stopName[i][4] = bestClus.labels_[i]

clf = tree.DecisionTreeClassifier()
clf = clf.fit(treeX, treeY)

file = open('clf', 'wb')
dill.dump(clf,file)
file = open('stopName', 'wb')
dill.dump(stopName,file)
file.close()