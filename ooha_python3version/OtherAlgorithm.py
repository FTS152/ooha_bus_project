#!/usr/bin/env python
# coding: utf-8

# In[3]:


import dill
TickSize=10
#StopNum：站數
file = open('StopNum','rb')
StopNum = dill.load(file)
#Nw：第w站所花時間段數量，maxN：各站時間段總數
file = open('Time_N','rb')
N = dill.load(file)
temp = 0
TotalN = 0
TotalBusTime = {}
TotalBusTime[0] = 0

for w in range(StopNum-1):
    TotalN = TotalN + N[w]
    TotalBusTime[w+1] = TotalN
N[StopNum-1] = 0
TotalN = TotalN + N[StopNum-1]
TotalBusTime[StopNum] = TotalN

print("N:")
print(N)
print("TotalN:")
print(TotalN)
print("TotalBusTime:")
print(TotalBusTime)

#AdTime j: 第j種廣告時長會佔據多少時間段
file = open('AdTime','rb')
AdTime = dill.load(file)
file = open('AdName','rb')
AdName = dill.load(file)
#M：廣告數量
file = open('Ad_NUM','rb')
M = dill.load(file)
#AdRepeatTime, AdRepeatNum: 最短P個時間段內不可播放同樣廣告超過K次
for i in range(M):
    AdTime[i] = int(AdTime[i]/TickSize)
print("AdTime:")
print(AdTime)
print("AdName:")
print(AdName)

#AudiencePreference jk: 客群k喜歡廣告j的程度 
file = open('AudiPre','rb')
AudiencePreference = dill.load(file)
print("AudiencePreference:")
print(AudiencePreference)
#K: 客群種類數
K = 12
print("K:%d"%K)
#AudienceNum w,k: w站上車上有幾位屬於客群k的人
file = open('AudiNum','rb')
AudienceNum = dill.load(file)
print("AudienceNum:")
print(AudienceNum)


# In[39]:


yTurn = {}
#計算哪個廣告開始在哪個時間段開始播
indi_AD = 0
indi_T = 0
for n in range(TotalN):
    for m in range(M):
        yTurn[n,m] = 0
    if n is indi_T:
        yTurn[n,indi_AD] = 1
        indi_T = indi_T + AdTime[indi_AD]
        indi_AD = (indi_AD+1)%M
#開始算objective

Ad_TurnPre = {}
for j in range(M):
    Ad_TurnPre[j] = sum( (sum(AudienceNum[w,k]*AudiencePreference[j,k] for k in range(K))*sum( yTurn[i,j] for i in range(TotalBusTime[w], TotalBusTime[w+1]) ))for w in range(StopNum) )
print(Ad_TurnPre)
print(Ad_TurnPre[min(Ad_TurnPre, key = Ad_TurnPre.get)])


# In[38]:


import random
random.seed(1)
yRan = {}
indi_AD = 0
indi_T = 0
for n in range(TotalN):
    for m in range(M):
        yRan[n,m] = 0
    if n is indi_T:
        yRan[n,indi_AD] = 1
        indi_T = indi_T + AdTime[indi_AD]
        indi_AD = random.randint(0,M-1)
#print(yRan)

Ad_RanPre = {}
for j in range(M):
    Ad_RanPre[j] = sum( (sum(AudienceNum[w,k]*AudiencePreference[j,k] for k in range(K))*sum( yRan[i,j] for i in range(TotalBusTime[w], TotalBusTime[w+1]) ))for w in range(StopNum) )
print(Ad_RanPre)
print(Ad_RanPre[min(Ad_RanPre, key = Ad_RanPre.get)])

