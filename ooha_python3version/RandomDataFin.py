
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
K=12 
AudienceNum = {}
random.seed(seed_NUM)
Scene_SexProb = [0.5,0.5]#uniform
Scene_AgeProb = [1/6]*6
print(Scene_SexProb)
print(Scene_AgeProb)
AudiProb = [round(x * y,4) for x, y in product(Scene_SexProb, Scene_AgeProb)]
#0,1,2,3,4,5,6,7,8,9,10,11：這種狀況下是客群0

On = {}
AudiOn = {}
#模擬下車機率
#BIG = random.randint(3,StopNum) #隨機設定大站池
#Station = [random.randint(0, StopNum-1) for _ in range(BIG)] #大站池
StationOfCustomer=[]#每個客群的大站
EveryCustomer = [3]*K
for k in range(K):
    random.seed(seed_NUM+k)
    StationOfCustomer.append(random.sample(list(range(0,StopNum-1)),EveryCustomer[k])) #不同下車機率，同樣大站數量
    #StationOfCustomer.append(random.sample(Station,3)) #類似下車機率
def OffProb(w,Station,k):
    past = sum(i <= w for i in Station)
    if (StopNum+EveryCustomer[k]-w-past-1) <=0:
        basic = [1]*StopNum
    else:
        basic = [1/(StopNum+EveryCustomer[k]-w-past-1)]*StopNum
    for i in range(w+1):
        basic[i] = 0
    for i in range(EveryCustomer[k]):
        temp = Station[i]
        basic[temp] = basic[temp]*2  
    return(basic)
print(StationOfCustomer)

#模擬上車人數，並且生成族群以及下站的位置
totalOnBus=[]
for w in range(StopNum-1):
    cusType=[]
    totalOn=random.randint(0,10)
    totalOnBus.append(totalOn)#紀錄各站上來的人數
    for p in range(totalOn):
        cusType.append(random.choices(range(K),AudiProb)) #紀錄cusType的客群人數
    for k in range(K): #紀錄w,k
        On[w,k]=cusType.count([k])

for k in range(K):
    for w in range(StopNum-1):
        CurrOff = OffProb(w,StationOfCustomer[k],k)
        for p in range(On[w,k]):
            #offstation = random.choice(range(w+1,StopNum)) #uniform probability
            offstation = random.choices(range(StopNum),CurrOff)
            AudiOn[w,k,p] = (offstation[0]) 
print("On:")
print(On)
print("AudiOn: ")
print(AudiOn)

#初始化，為了下面的累積人數
for w in range(StopNum):
    for k in range(K):
        AudienceNum[w,k] = 0

from collections import OrderedDict
#把乘客資訊開始處理到AudienceNum裡面
for w in range(StopNum-1):
    for k in range(K):#處理上車
        if(w==0):
            AudienceNum[w,k]=AudienceNum[w,k]+On[w,k]
        else:
            AudienceNum[w,k]=AudienceNum[w-1,k]+On[w,k]
        ##把在該站前的人都traverse一遍看誰要下車
    for g in range(w):#在站w前
        for j in range(K):#看看每個客群
            for p in range(0,On[g,j]):
                if (AudiOn[g,j,p]==w):
                    AudienceNum[w,j]=AudienceNum[w,j]-1
print("AudienceNum:")
print(AudienceNum)
file = open("AudiNum",'wb')
dill.dump(AudienceNum,file)
file.close()


# In[4]:


#生成preference: 客群間有沒有極端差異
AudiencePreference = {}
numpy.random.seed(seed_NUM)
random.seed(seed_NUM)
Binary = bool((random.randint(0,250))%2)
DifferChoice = numpy.random.randint(0,2,size=K)
K_Des = numpy.random.randint(0,2, size=K)
print(DifferChoice)
print(K_Des) #若要極端，就設DifferChoice全為0；不然就全生成1，是一般隨機
for m in range(M):
    for k in range(K):
        if Binary :
            AudiencePreference[m,k] = random.randint(0,1)
        else:
            if DifferChoice[k] == 0: #big
                if K_Des[k] == 0:
                    AudiencePreference[m,k] = random.randint(1,3)
                else:
                    AudiencePreference[m,k] = random.randint(3,5)
            else: #general
                AudiencePreference[m,k] = random.randint(1,5)
#result = OrderedDict(sorted(AudiencePreference.items(), key = lambda x: x[0][1]))
#print(dict(result))
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
        Conflict[j1,j2] = random.choices([0,1],[0.1,0.9])[0] #90%機率不會有衝突
        Conflict[j2,j1] = Conflict[j1,j2]
result = OrderedDict(sorted(Conflict.items(), key = lambda x: x[0][0]))
Conflict = dict(result)
print(Conflict)
file = open("conflict",'wb')
dill.dump(Conflict, file)
file.close()


# In[6]:


print(seed_NUM)
cate = (ADChoice%3,SlotChoice,Binary)#廣告數量，時間段數量，Preference
print(cate)

