#csv file column
#1 : data id
#2 : route number
#3 : direction
#4 : latitude
#5 : longtitude
#6 : gender
#7 : ageLow
#8 : ageHigh
#9 : date
#10: time

# argument: data as a matrix or dataframe , given time standard(in seconds), testNum(number)
# process: check if a particular row of data should be deleted
# output: return an array in which there are 0 and 1. 1 means it should be deleted,else 0.
cleanData<-function(inputData,ageStandard,timeStandard,testNum){
	obsNum <- length(inputData[,1])
	time <-  array(dim=c(obsNum,3))
	for(i in 1: obsNum){
		temp <- inputData[i,10]
		temp2 <- toString(temp)
		temp3 <- strsplit(temp2,":")
		time[i,1] <- as.integer(temp3[[1]][1])
		time[i,2] <- as.integer(temp3[[1]][2])
		time[i,3] <- as.integer(temp3[[1]][3])
	}

	checkIfDelete <- array(0,dim=obsNum)

	for(i in 2:obsNum-1){
		if(checkIfDelete[i]==1) next #already deleted
		if((i+testNum)>obsNum)
			loopNum <- obsNum-i
		else
			loopNum <- testNum
		
		for(j in 1:loopNum){

			if(checkIfDelete[i+j]==1) next #already deleted
			if(inputData[i,2]!=inputData[i+j,2]) next #different route
            if(inputData[i,3]!=inputData[i+j,3]) next #different direction
			if(inputData[i,6]!=inputData[i+j,6]) next #different gender
			if(inputData[i,9]!=inputData[i+j,9]) next #different date
			if(timeDifference(time,i,j)>timeStandard) next #pass time standard
			if(ageDifference(inputData,i,j)>ageStandard) next#pass age standard

			checkIfDelete[i+j] <- 1
			
		}
	}

	return(checkIfDelete)

}


timeDifference <- function(time,i,j){
	difference <- (time[i+j,1]-time[i,1])*3600 + (time[i+j,2]-time[i,2])*60 + time[i+j,3]-time[i,3]
	return(difference)
}

ageDifference <- function(inputData,i,j){
	difference<-abs((inputData[i,7]+inputData[i,8])/2 - (inputData[i+j,7]+inputData[i+j,8])/2)
	return(difference)
}

