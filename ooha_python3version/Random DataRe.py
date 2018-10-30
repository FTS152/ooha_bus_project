#!/usr/bin/env python
# coding: utf-8

# In[1]:


import random
seed_NUM= 1
#生成TimeResult和站數（假想路線，路線裡面就分了三種時間段）
import math
import dill
import numpy
random.seed(seed_NUM)
numpy.random.seed(seed_NUM)
TimeSLOT = [(360,720),(720,1080),(1080,1440)]
SlotChoice = random.randint(0,2)
print("時間區段種類:")
print(chr(65+SlotChoice))
StopNum = random.randint(20,90) #discuss
N={}
TotalN = random.randint(TimeSLOT[SlotChoice][0],TimeSLOT[SlotChoice][1]) #fixed sum
N = numpy.random.multinomial(TotalN, numpy.ones(StopNum)/StopNum, size=1)[0]
remain = numpy.random.multinomial(N[StopNum-1], numpy.ones(StopNum-1)/(StopNum-1), size=1)[0]
for w in range(StopNum-1):
    N[w] = N[w]+remain[w]
N[StopNum-1] = 0
print(list(N))
print(TotalN)
file = open("StopNum", 'wb')
dill.dump(StopNum, file)
file.close()
with open("Time_N", 'wb') as file:
    dill.dump(list(N), file)
file.close()


# In[2]:


#生成假想廣告和名字（分成少中多）
import random
random.seed(seed_NUM)
Scene_AD = [10,25,50]
ADChoice = random.randint(0,50)
Time_CHOICE = [30,60]
print("廣告種類:")
print(chr(65+(ADChoice%3)))
M = Scene_AD[int(ADChoice%3)]
AdTime={}
AdName={}
print(M)
for w in range(M):
    AdTime[w] = random.choice(Time_CHOICE)
    if w < 26:
        AdName[chr(65+w)] = w
    else :
        AdName[chr(71+w)] = w
print(AdTime)
print(AdName)
file = open("Ad_NUM",'wb')
dill.dump(M,file)
file.close()
ADTimeFile = open("AdTime", 'wb')
dill.dump(AdTime, ADTimeFile)
ADTimeFile.close()
ADNameFile = open("AdName", 'wb')
dill.dump(AdName, ADNameFile)
ADNameFile.close()


# In[3]:


#生成客群
#Off：random大站數量（1-5），然後設定下車機率是小站的兩倍？
#On：random上來的總人數（1-10），隨機生成其族群（40%機率是族群X之類的），還有用下車機率骰出會在哪一站下車！
from itertools import product
K=12 #暫用新客群
AudienceNum = {}
random.seed(seed_NUM)
Scene_SexMore = 0.8
Scene_AgeMore = 0.5
temp1 = random.randint(0,150)
if temp1%2 == 0:
    Scene_SexProb = [Scene_SexMore, round(1-Scene_SexMore,1)]#男生多 discuss
else:
    Scene_SexProb = [round(1-Scene_SexMore,1), Scene_SexMore]
print("性別種類:")
print(chr((temp1%2)+65))
temp2 = random.randint(0,200)
Scene_AgeProb = [(1-Scene_AgeMore)/5]*6
for i in range(6):
    if temp2%6 is i:
        print("年齡種類:")
        Age_Num = i
        print(chr(i+65))
        Scene_AgeProb[i] = Scene_AgeMore
print(Scene_SexProb)
print(Scene_AgeProb)
AudiProb = [round(x * y,4) for x, y in product(Scene_SexProb, Scene_AgeProb)]
#0,1,2,3,4,5,6,7,8,9,10,11：這種狀況下是客群0

On = {}
AudiOn = {}
#模擬下車機率
BIG = random.randint(1,5) #discuss
Station = [random.randint(0, StopNum-1) for _ in range(BIG)] #抓出大站
def OffProb(w):
    past = sum(i <= w for i in Station)
    if (StopNum+BIG-w-past-1) <=0:
        basic = [1]*StopNum
    else:
        basic = [1/(StopNum+BIG-w-past-1)]*StopNum
    for i in range(w+1):
        basic[i] = 0
    for i in range(BIG):
        temp = Station[i]
        basic[temp] = basic[temp]*2  
    return(basic)
print(BIG)
print(Station)

#模擬上車人數，並且生成族群以及下站的位置
for w in range(StopNum-1):
    On[w] = random.randint(0,10) #discuss
    CurrOff = OffProb(w)
    for p in range(On[w]):
        group = random.choices(range(K),AudiProb)
        #offstation = random.choice(range(w+1,StopNum)) #uniform probability
        offstation = random.choices(range(StopNum),CurrOff)
        AudiOn[w,p] = (group[0],offstation[0])
print(On)
print(AudiOn)

#初始化，為了下面的累積人數
for w in range(StopNum):
    for k in range(K):
        AudienceNum[w,k] = 0

from collections import OrderedDict
#把乘客資訊開始處理到AudienceNum裡面
for k in range(K):
    for w in range(StopNum-1):
        for p in range(On[w]):
            if k == AudiOn[w,p][0]: #找到相對應客群
                temp = w
                for i in range(w, AudiOn[w,p][1]):
                    AudienceNum[i,k] = AudienceNum[i,k]+1
#result = OrderedDict(sorted(AudienceNum.items(), key = lambda x: x[0][1]))
#AudienceNum = dict(result)
print("AudienceNum:")
print(AudienceNum)
file = open("AudiNum",'wb')
dill.dump(AudienceNum,file)
file.close()


# In[4]:


#生成preference: Binary
AudiencePreference = {}
random.seed(seed_NUM)
BinaryChoice = random.randint(0,100)
Binary = bool(BinaryChoice%2)
print("Preference:")
print(Binary)
for m in range(M):
    for k in range(K):
        if(Binary):
            AudiencePreference[m,k] = random.randint(0,1)
        else:
            AudiencePreference[m,k] = random.randint(1,5)
print(AudiencePreference)
file = open("AudiPre", 'wb')
dill.dump(AudiencePreference, file)
file.close()


# In[5]:


#Conflict
Conflict = {}
random.seed(seed_NUM)
for j1 in range(M):
    for j2 in range(j1,M):
        Conflict[j1,j2] = random.choices([0,1],[0.1,0.9])[0]
        Conflict[j2,j1] = Conflict[j1,j2]
result = OrderedDict(sorted(Conflict.items(), key = lambda x: x[0][0]))
Conflict = dict(result)
print(Conflict)
file = open("conflict",'wb')
dill.dump(Conflict, file)
file.close()


# In[6]:


print(seed_NUM)
cate = (ADChoice%3,SlotChoice,temp%2,Age_Num,bool(BinaryChoice%2))
print(cate)
get_ipython().run_line_magic('store', 'cate')


# In[ ]:




