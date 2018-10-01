library('jsonlite')
library('rjson')
result <- fromJSON(file = "920.json")
busInfo <<- c()
Rawdata <- read.table("data.csv",header = TRUE, sep=",")
data <- c()
for(i in 1:nrow(Rawdata)){
	if(Rawdata$routeName[i]==920)
		data<-rbind(data,Rawdata[i,])
}
data <- data[order(data$plateNum,data$date,data$time),]

lat<-c()
long<-c()
for(i in  1:length(result[[1]]$Stops)){
	lat<-append(lat,result[[1]]$Stops[[i]]$StopPosition$PositionLat)
	long<-append(long,result[[1]]$Stops[[i]]$StopPosition$PositionLon)
}
position<<-cbind(lat,long)


pos<-function(lat,long,position){
	M=1
	for(i in 1:nrow(position)){
		distance=(lat-position[i,1])^2+(long-position[i,2])^2
		if(distance<M){
			stop=i
			M=distance
		}
	}
	return(stop)
}
schedule<-function(data){
	stopInfo<-matrix(nrow=nrow(data),ncol=nrow(data))
	stopName <- c()
	counter=1
	stopName<-append(stopName,paste(paste(data$date[1],data$time[1]),data$direction[1]))
	busInfo <<- rbind(busInfo,c(paste(data$date[1],data$time[1]),data$direction[1],weekdays(as.Date(data$date[1])),strsplit(as.character(data$time[1]),split=":")[[1]][1]))
	stopInfo[1,1]=pos(data$latitude[1],data$longitude[1],position)
	for(i in 2:nrow(data)){
		if(data$date[i]!=data$date[i-1]||
			difftime(paste(Sys.Date(),data$time[i]),paste(Sys.Date(),strsplit(stopName[counter],split=" ")[[1]][2]),units="hours")>2||data$direction[i]!=data$direction[i-1]
			)
			counter=counter+1
		for(j in 1:nrow(stopInfo))
			if(is.na(stopInfo[j,counter])){
				if(j==1){
					stopName<-append(stopName,paste(paste(data$date[i],data$time[i]),data$direction[i]))
					busInfo <<- rbind(busInfo,c(paste(data$date[i],data$time[i]),data$direction[i],weekdays(as.Date(data$date[i])),strsplit(as.character(data$time[i]),split=":")[[1]][1]))
				}
				stopInfo[j,counter]=pos(data$latitude[i],data$longitude[i],position)
				break
			}

	}
	stopInfo<-stopInfo[-which(apply(stopInfo,1,function(x)all(is.na(x)))), -which(apply(stopInfo,2,function(x)all(is.na(x))))]
	colnames(stopInfo)<-stopName

	clus <- c()
	for(i in 1:nrow(busInfo)){
		d = strsplit(busInfo[i,1],split=" ")[[1]][1]
		t = strsplit(busInfo[i,1],split=" ")[[1]][2]
		clus <- append(clus,cluster(d,t))
	}
	busInfo<<-cbind(busInfo,clus)

	return(stopInfo)
}

passVector<-function(stopInfo){
	stopVec<-matrix(0,nrow=nrow(position),ncol=ncol(stopInfo))
	colnames(stopVec) <- colnames(stopInfo)
	del <- c()
	for(i in 1:ncol(stopInfo)){
		for(j in 1:nrow(stopInfo)){
			if(is.na(stopInfo[j,i]))
				break
			else
				stopVec[as.numeric(stopInfo[j,i]),i]=as.numeric(stopVec[as.numeric(stopInfo[j,i]),i])+1
		}
		if(sum(as.numeric(stopVec[,i]))<=15)
		 	del=append(del,-i)
	}
	stopVec <- stopVec[,del]
	busInfo <<- busInfo[del,]
	return(stopVec)
}

cluster<-function(date,time){
	wd = weekdays(as.Date(date))
	hr = strsplit(as.character(time),split=":")[[1]][1]
	if( wd == weekdays(as.Date("2011-01-01"))||
		wd == weekdays(as.Date("2011-01-02"))){
		if(as.numeric(hr)<=12) 
			return("weekend morning")
		else
			return("weekend afternoon")
	}
	else{
		if(as.numeric(hr)>=7 && as.numeric(hr)<=9) 
			return("weekday rush1")
		if(as.numeric(hr)>=17 && as.numeric(hr)<=19)
			return("weekday rush2")
		else
			return("weekday off-peak")		
	}
}

onforecast<-function(stopVec,routeName,date,startTime,direction){

	clus <- cluster(date,startTime)
	select <- c()
	for(i in 1:nrow(busInfo)){
		if(busInfo[i,2]==direction && busInfo[i,5]==clus && busInfo[i,1]>paste(date,startTime))
			select <- cbind(select,stopVec[,i])
	}
	forecast <- vector("numeric",nrow(select))
	for(i in ncol(select):(ncol(select)-2)){
		if(i<0) return("no history data!")
		for(j in 1:nrow(select))
			forecast[j] = forecast[j] + (1/3)*select[j,i]
	}
	return(round(forecast))

}

regforecast<-function(stopVec,routeName,date,startTime,direction){

	x <- c()
	for(i in 1:nrow(busInfo)){
		t = as.numeric(busInfo[i,4])
		wd = busInfo[i,3]
		if( wd == weekdays(as.Date("2011-01-01"))||
			wd == weekdays(as.Date("2011-01-02")))
			isWeekend = 1
		else
			isWeekend = 0
	}
}

predict<-function(stopVec,offTrue,direction){
	tempOff=vector("numeric",nrow(stopVec))
	x=c(47,50,52)
	tempOff[x[1]]=0.001
	tempOff[x[2]]=0.001
	tempOff[x[3]]=0.701
	a=(1-sum(tempOff))
	b=length(tempOff)-length(x)
	counter=0
	for(i in 1:length(tempOff)){
		for(j in 1:length(x)){
			if(i==x[j]) break
			if(j==length(x)){
				tempOff[i]=a/b
				counter=counter+1
			}
		}
	}
	leastError=errorCal(stopVec,tempOff,offTrue,direction)
	bestTemp=tempOff
	for(m in 1:70){
		for(n in m:70){
			tempOff[x[3]]=as.numeric(tempOff[x[3]])-0.01
			tempOff[x[2]]=as.numeric(tempOff[x[2]])+0.01
			newError=errorCal(stopVec,tempOff,offTrue,direction)
			if(newError<leastError){
				bestTemp=tempOff
				leastError=newError
			}
		}
		tempOff[x[1]]=as.numeric(tempOff[x[1]])+0.01
		tempOff[x[2]]=as.numeric(tempOff[x[2]])-0.01
		temp=tempOff[x[2]]
		tempOff[x[2]]=tempOff[x[3]]
		tempOff[x[3]]=temp
	}
	print(leastError)
	return(bestTemp)
}

errorCal<-function(stopVec,tempOff,offTrue,direction){
	Error=0
	for(i in 1:ncol(stopVec)){
		current=vector("numeric",nrow(stopVec))
		tempTempOff=tempOff
		if(strsplit(colnames(stopVec)[i],split=' ')[[1]][3]!=direction)
			next
		for(j in 1:nrow(stopVec)){
			tempTempOff[j]=0
			tempTempOff=tempTempOff/sum(tempTempOff)
			if(as.numeric(stopVec[j,i])==0||j==nrow(stopVec)){
				next
			}
			for(k in 1:as.numeric(stopVec[j,i])){
				x=sample(nrow(stopVec),1,prob=tempTempOff)
				current[x]=current[x]+1
			}
		}
		if(sum(current)!=0)
			current=current/sum(current)
		for(i in 1:length(current)){
			Error=Error+(current[i]-offTrue[i])^2
		}
	}
	return(Error)
}

getOff<-function(on,prob,direction){
	off=matrix(0,nrow=nrow(on),ncol=ncol(on))
	colnames(off)<-colnames(on)
	for(i in 1:ncol(on)){
		tempProb=prob
		if(strsplit(colnames(on)[i],split=' ')[[1]][3]!=direction)
			next
		for(j in 1:nrow(on)){
			tempProb[j]=0
			tempProb=tempProb/sum(tempProb)
			if(as.numeric(on[j,i])==0||j==nrow(on))
				next
			for(k in 1:as.numeric(on[j,i])){
				x=sample(nrow(on),1,prob=tempProb)
				off[x,i]=off[x,i]+1
			}
		}
	}
	return(off)	
}

passNum<-function(on,off,direction){
	pass=matrix(0,nrow=nrow(on),ncol=ncol(on))
	colnames(pass)<-colnames(on)
	for(i in 1:ncol(on)){
		if(strsplit(colnames(on)[i],split=' ')[[1]][3]!=direction)
			next
		for(j in 1:nrow(on)){
			if(j==1)
				pass[j,i]=on[j,i]-off[j,i]
			else{
				pass[j,i]=pass[j-1,i]+on[j,i]-off[j,i]		
			}
		}		
	}
	del <- c()
	for(i in 1:ncol(pass)){
		if(sum(pass[,i])==0)
		 	del=append(del,-i)
	}
	pass <- pass[,del]
	return(pass)
}