##calcuate the average onboard , average offboard and total number of people
##input : workbooks of plenty worksheet
##out
library(XLConnect)
ptt1 <- loadWorkbook("/Users/user/Documents/Junior/project/920ptt1.xlsx")
ptt2 <- loadWorkbook("/Users/user/Documents/Junior/project/920ptt2.xlsx")
ptt3 <- loadWorkbook("/Users/user/Documents/Junior/project/920ptt3.xlsx")
ptt4 <- loadWorkbook("/Users/user/Documents/Junior/project/920ptt4.xlsx")
stop <- loadWorkbook("/Users/user/Documents/Junior/project/stops.xlsx")
stops <- readWorksheet(stop,1)


avgBus <- function (workbookA,workbookB,workbookC,workbookD,stop){
	workBookList <- list(workbookA,workbookB,workbookC,workbookD)
	sheetNum <- array(0,dim=4)
	sheetNum[1] <- length(getSheets(workbookA))
	sheetNum[2] <- length(getSheets(workbookB))
	sheetNum[3] <- length(getSheets(workbookC))
	sheetNum[4] <- length(getSheets(workbookD))

	name0 <- data.frame(stops=stop[1:52,14])
	name1 <- data.frame(stops=stop[53:101,14])
	count0 <- rep(0,nrow(name0))
	count1 <- rep(0,nrow(name1))
	on<-count0
	off<-count0
	Count0<-cbind(name0,on,off,count0)
	on<-count1
	off<-count1
	Count1<-cbind(name1,on,off,count1)

	##workbookA
	for(k in 1:4){
		for(i in 1:sheetNum[k]){
			worksheet<-readWorksheet(workBookList[[k]],i)
			start<-firstData(worksheet)
			end<-lastData(worksheet)
 		  sample<-data.frame(worksheet[start:end,1:3])
 		  if(colnames(worksheet)[12] == "X1"){
 		    check<-FALSE
 		    p<-2
 		    for(j in 1:nrow(Count1)){
 		      if(p > nrow(sample)) break
 		      if(check){
 		        if(is.na(sample[p,2]) && is.na(sample[p,3])){
 		          if(sample[p,1] == Count1[4,1] || sample[p,1] == Count1[12,1]){ #高速公路、中山國中跳過
 		            p<-p+1
 		          }
 		          else check<-FALSE #確定沒東西了
 		        }
 		        else{ #確定非na
 		          Count1[j,2]<-Count1[j,2]+sample[p,2]
 		          Count1[j,3]<-Count1[j,3]+sample[p,3]
 		          if(is.na(Count1[j,2])||is.na(Count1[j,3])){
 		            print(c(k,i))
 		          }
 		          Count1[j,4]<-Count1[j,4]+1
 		          p<-p+1
 		        }
 		      }
 		      if(sample[1,1] == Count1[j,1]){
 		        check<-TRUE
 		        Count1[j,2]<-Count1[j,2]+sample[1,2]
 		        Count1[j,3]<-Count1[j,3]+sample[1,3]
 		        Count1[j,4]<-Count1[j,4]+1
 		      }
 		    }
			}
			else if(colnames(worksheet)[12] == "X0"){
			  check<-FALSE
			  p<-2
			  for(j in 1:nrow(Count0)){
			    if(p > nrow(sample)) break
			    if(check){
			      if(is.na(sample[p,2]) && is.na(sample[p,3])){
			        if(sample[p,1] == Count0[34,1] || sample[p,1] == Count0[49,1]){ #高速公路、中山國中跳過
			          p<-p+1
			        }
			        else check<-FALSE #確定沒東西了
			      }
			      else{ #確定非na
			        Count0[j,2]<-Count0[j,2]+sample[p,2]
			        Count0[j,3]<-Count0[j,3]+sample[p,3]
			        if(is.na(Count0[j,2])||is.na(Count0[j,3])){
			          print(c(k,i))
			        }
			        Count0[j,4]<-Count0[j,4]+1
			        p<-p+1
			      }
			    }
			    if(sample[1,1] == Count0[j,1]){
			      check<-TRUE
			      Count0[j,2]<-Count0[j,2]+sample[1,2]
			      Count0[j,3]<-Count0[j,3]+sample[1,3]
			      Count0[j,4]<-Count0[j,4]+1
			    }
			  }
			}
		}
	}
	library(rJava)
	library(xlsxjars)
	library(xlsx)
	write.xlsx(x=data.frame(Count0),file="avgBusResult.xlsx",sheetName="林口板橋", row.names = FALSE)
	write.xlsx(x=data.frame(Count1),file="avgBusResult.xlsx",sheetName="板橋林口",append=TRUE, row.names=FALSE)
}

firstData <- function(worksheet){
	for(i in 1:length(worksheet[,1])){
		if(!is.na(worksheet[i,2])){
			return(i)
		}
	}

	return(length(worksheet[,1]))
}

lastData <- function(worksheet){
	for(i in length(worksheet[,1]):1){
		if(!is.na(worksheet[i,2])){
			return(i)
		}
	}
}

calculate0 <- function(data, output){
	check<-FALSE
	p<-2
	for(i in c(1:nrow(output))){
		if(p > nrow(data)) break
		if(check){
			if(is.null(data[p,2]) && is.null(data[p,3])){
				if(data[p,1] == output[34,1] || data[p,1] == output[49,1]){ #高速公路、中山國中跳過
					p<-p+1
				}
				else check<-FALSE #確定沒東西了
			}
			else{ #確定有東西
				output[i,2]<-output[i,2]+data[p,2]
				output[i,3]<-output[i,3]+data[p,3]
				output[i,4]<-output[i,4]+1
				p<-p+1
			}
		}
		if(data[1,1] == output[i,1]){
			b<-TRUE
			output[i,2]<-output[i,2]+data[1,2]
			output[i,3]<-output[i,3]+data[1,3]
			output[i,4]<-output[i,4]+1
		}
	}
}

calculate1 <- function(data, output){
	check<-FALSE
	p<-2
	for(i in c(1:nrow(output))){
		if(p > nrow(data)) break
		if(check){
			if(is.null(data[p,2]) && is.null(data[p,3])){
				if(data[p,1] == output[4,1] || data[p,1] == output[12,1]){ #高速公路、中山國中跳過
					p<-p+1
				}
				else check<-FALSE #確定沒東西了
			}
			else{ #確定有東西
				output[i,2]<-output[i,2]+data[p,2]
				output[i,3]<-output[i,3]+data[p,3]
				output[i,4]<-output[i,4]+1
				p<-p+1
			}
		}
		if(data[1,1] == output[i,1]){
			b<-TRUE
			output[i,2]<-output[i,2]+data[1,2]
			output[i,3]<-output[i,3]+data[1,3]
			output[i,4]<-output[i,4]+1
		}
	}
}
