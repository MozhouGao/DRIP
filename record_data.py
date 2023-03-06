import csv 
import time 
import numpy as np
import pandas as pd 
import geopandas as gpd

gps = pd.read_csv('Measured_GPS.csv',sep=',')

times = gps.time
lats = np.array(gps.latitude)
lons = np.array(gps.longitude)

fieldnames = ['lons','lats','time']


with open ('GPS_receiver.csv','w') as csv_file: 
    csv_writer = csv.DictWriter(csv_file, fieldnames = fieldnames)
    csv_writer.writeheader()

Day = True
i = 1  
while Day:
        
    with open('GPS_receiver.csv', 'a') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        lat = lats[i]
        lon = lons[i]
        hour_a_day = times[i]
        
        
        tdf = pd.DataFrame(data={'lat':[lat],'lon':[lon]})
        tgdf = gpd.GeoDataFrame(tdf, geometry=gpd.points_from_xy(tdf.lon, tdf.lat))
        tgdf = tgdf.set_crs("EPSG:4326")
        tgdf.geometry = tgdf.geometry.to_crs(epsg=26910)

        
        lat_value = tgdf.geometry.y.iloc[0]
        lon_value = tgdf.geometry.x.iloc[0]
        hour = hour_a_day
        
        
        info = {
            "lons": lon_value,
            "lats": lat_value,
            "time": hour
        }

        csv_writer.writerow(info)
        
        
        print(lat_value, lon_value, hour)
    i += 1        
    time.sleep(1)
    
    
    
