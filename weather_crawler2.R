rm(list=ls(all.names=TRUE))
library(XML)
library(RCurl)
library(httr)
Sys.setlocale(category = "LC_ALL", locale = "cht")
urlCode = c("TWXX0021:1:TW")
#,"TWXX0025:1:TW")
startNo = 1
endNo   = length(urlCode)
subPath <- "https://weather.com/zh-TW/weather/hourbyhour/l/"
cityCode <- c("台北")
#"桃園")


alldata <- data.frame()

for( pid in 1:length(urlCode)){
    urlPath <- paste(subPath, urlCode[pid], sep='')
    temp    <- getURL(urlPath, encoding = "big5")
    xmldoc  <- htmlParse(temp)

    hour <- xpathSApply(xmldoc,"//div[@class='hourly-time']//span",xmlValue)
    temperature <-  xpathSApply(xmldoc,"//td[@class='temp']",xmlValue)
    rain <- xpathSApply(xmldoc,"//td[@class='precip']",xmlValue)
    
    
    for(time in 1:length(hour)){

      hour2 <- hour[time]
      temperature2<- sub('.$','',temperature[time])
      rain2<-rain[time]


      Erroresult<- tryCatch({
        subdata <- data.frame(hour2,temperature2,rain2)
        alldata <- rbind(alldata, subdata)
      }, warning = function(war) {
        print(paste("MY_WARNING:  ", urlPath))
      }, error = function(err) {
        print(paste("MY_ERROR:  ", urlPath))
      }, finally = {
        print(paste("End Try&Catch", urlPath))
      })
    }
  }




print(nrow(alldata))
write.csv(alldata, file = "/Users/walter/Desktop/weather.csv")