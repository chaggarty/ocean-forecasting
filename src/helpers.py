import os
from tempfile import mkdtemp
import netCDF4
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as dlt
import datetime
import time
import calendar
import requests
from bs4 import BeautifulSoup
import json
import logging

def prediction(windSpeed, waveHt, waveDir, tide):
    if windSpeed < 3 and waveHt > 4 and waveDir < 285 and waveDir > 195 and float(tide) < 3.5:
        return 'Great!'
    elif windSpeed < 6 and waveHt > 2 and waveDir < 300 and waveDir > 180 and float(tide) < 5:
        return 'Good'
    elif windSpeed < 8 and waveHt > 1.5 and waveDir < 300 and waveDir > 180 and float(tide) < 5:
        return 'Fair'
    else:
        return 'Poor'

def surfline_data():
    url = 'https://www.surfline.com/surf-report/ponto-north/584204214e65fad6a7709c79'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tide = soup.find("span", {"class": "quiver-reading"})
    conditions = soup.find("div", {"class": "quiver-spot-report"})
    return tide.contents[0], conditions.div.text

def air_data():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    latitude = '33.112026'
    longitude = '-117.324464'
    DARKSKY_URL = os.getenv('DARKSKY_URL')
    url = DARKSKY_URL + latitude + ',' + longitude
    page = requests.get(url)
    json_data = json.loads(page.text)
    json_small = json_data["currently"]
    json_temp = json_small["temperature"]
    json_wind = json_small["windSpeed"]
    json_windDir = json_small["windBearing"]
    return json_temp, json_wind, json_windDir

def ocean_data(stn, startdate, enddate):
    # CDIP Archived Dataset URL
    # data_url = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/archive/' + stn + 'p1/' + stn + 'p1_historic.nc'

    # CDIP Realtime Dataset URL
    data_url = 'http://thredds.cdip.ucsd.edu/thredds/dodsC/cdip/realtime/' + stn + 'p1_rt.nc'

    nc = netCDF4.Dataset(data_url)
    ncTime = nc.variables['sstTime'][:]
    timeall = [datetime.datetime.fromtimestamp(t) for t in ncTime] # Convert ncTime variable to datetime stamps
    Hs = nc.variables['waveHs']
    Tp = nc.variables['waveTp']
    Dp = nc.variables['waveDp'] 

    # print(nc.variables['sstSeaSurfaceTemperature'][:])
    # print(nc.variables['sstTime'][:])

    # for d in nc.dimensions.items():
    #     print(d)


    # Create a variable of the Buoy Name and Month Name, to use in plot title
    buoyname = nc.variables['metaStationName'][:].astype('U13')
    buoytitle = " ".join(str(buoyname)[:-40])
    month_name = calendar.month_name[int(startdate[0:2])]
    year_num = (startdate[6:10])

    # Find nearest value in numpy array
    def find_nearest(array,value):
        idx = (numpy.abs(array-value)).argmin()
        return array[idx]

    # Convert from human-format to UNIX timestamp
    def getUnixTimestamp(humanTime,dateFormat):
        unixTimestamp = int(time.mktime(datetime.datetime.strptime(humanTime, dateFormat).timetuple()))
        return unixTimestamp

    unixstart = getUnixTimestamp(startdate,"%m/%d/%Y") 
    neareststart = find_nearest(ncTime, unixstart)  # Find the closest unix timestamp
    nearIndex = numpy.where(ncTime==neareststart)[0][0]  # Grab the index number of found date

    unixend = getUnixTimestamp(enddate,"%m/%d/%Y")
    future = find_nearest(ncTime, unixend)  # Find the closest unix timestamp
    futureIndex = numpy.where(ncTime==future)[0][0]  # Grab the index number of found date

    # Crete figure and specify subplot orientation (3 rows, 1 column), shared x-axis, and figure size
    # f, (pHs, pTp, pDp) = plt.subplots(3, 1, sharex=True, figsize=(15,10)) 

    # Manually accessing numpy array
    # print(len(nc.variables['sstSeaSurfaceTemperature'][nearIndex:futureIndex]))
    temp1c = nc.variables['sstSeaSurfaceTemperature'][-1]
    temp2c = nc.variables['sstSeaSurfaceTemperature'][nearIndex]

    temp1 = round((temp1c * 1.8) + 32, 2)
    temp2 = round((temp2c * 1.8) + 32, 2)
    
    return temp1, temp2, round(Hs[-1] * 3.281, 2), round(Tp[-1] * 1, 2), round(Dp[-1] * 1, 2)