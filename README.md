# ooha_bus_project
紀錄四個大四生在專題中struggle的過程

Python Usage:
```
python dump.py [routeName] [direction] [date(YYYY-mm-dd)](dump data from Elastic search
```
```
python preprocess.py [routeName] [direction] (clustering each face to a bus
```
```
python onforecast.py [routeName] [direction] [time(YYYY-mm-dd HH:MM:SS)] (predict certain bus
```

```
python offforecast.py [routeName] [direction] (given on data and off average, generate the number of passengers between every stops
```
```
python validation.py [routeName] [direction] (validate with MAD
```
