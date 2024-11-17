from datetime import datetime, timedelta
import pandas as pd
import pytz
import numpy as np
from django.shortcuts import render
from django.views.generic import View
import requests
from rest_framework.views import APIView
from rest_framework.response import Response

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'SolarWindData/index.html')

class ChartData(APIView):
    def get(self, request, format=None):
        try:
            #Obtain Chile's timezone 
            cl_timezone = pytz.timezone('America/Santiago')
            cl_tnow = datetime.now(cl_timezone)
            cl_24hr = cl_tnow - timedelta(hours=24)

            # timestamps 24 hr
            timestamps_24h = pd.date_range(cl_24hr, cl_tnow, freq='min').floor('min')

            # Fetch data from the JSON URLs
            mag_json_url = 'https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json'
            plasma_json_url = 'https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json'
            kp_index_url= 'https://services.swpc.noaa.gov/products/noaa-planetary-k-index-forecast.json'
            mag_response = requests.get(mag_json_url)
            plasma_response = requests.get(plasma_json_url)
            kp_response= requests.get(kp_index_url)
            
            if mag_response.status_code != 200 or plasma_response.status_code != 200 or kp_response.status_code !=200:
                return Response({'error': 'Failed to retrieve data from API'}, status=500)
            
            # Convert JSON data to DataFrames
            mag_data = mag_response.json()
            plasma_data = plasma_response.json()
            kp_data = kp_response.json()

            # Prepare data for the graph
            graph_data = prepare_graph_data(mag_data, plasma_data,kp_data, cl_24hr, cl_tnow, timestamps_24h)
            return Response(graph_data)
        except requests.RequestException as e:
            return Response({'error': 'Failed to connect to API'}, status=500)

def prepare_graph_data(mag_data: list, plasma_data: list,kp_data: list, start_time: datetime, end_time: datetime, timestamps_24h: pd.DatetimeIndex) -> dict:
    graph_data = {
        "labelsplasma": [],
        "labelsmag": [],
        "chartspeed": [],  
        "chartdensity": [], 
        "chartemperature": [],
        "chartbx": [],
        "chartby": [],
        "chartbz":[],
        "chartblon": [],
        "chartlat": [],
        "chartbt": [],
        "labelskp":[],
        "kp":[],
        "noaa_scale":[],
    }

    try:
        #data frames
        mag_df = pd.DataFrame(mag_data[1:], columns=mag_data[0])
        plasma_df = pd.DataFrame(plasma_data[1:], columns=plasma_data[0])
        kp_df=pd.DataFrame(kp_data[1:],columns=kp_data[0])

    except Exception as e:
        print(f"Error converting to DataFrame: {e}")
        return graph_data
    try:
         # Convert 'time_tag' to datetime and localize to UTC
        mag_df['time_tag'] = pd.to_datetime(mag_df['time_tag'], errors='coerce').dt.tz_localize('UTC')
        plasma_df['time_tag'] = pd.to_datetime(plasma_df['time_tag'], errors='coerce').dt.tz_localize('UTC')
        kp_df['time_tag'] = pd.to_datetime(kp_df['time_tag'], errors='coerce').dt.tz_localize('UTC')

        #Change UTC datetime to SCL datetime
        mag_df['time_tag'] = mag_df['time_tag'].dt.tz_convert('America/Santiago')
        plasma_df['time_tag'] = plasma_df['time_tag'].dt.tz_convert('America/Santiago')
        kp_df['time_tag'] = kp_df['time_tag'].dt.tz_convert('America/Santiago')
     

    except KeyError as e:
        print(f"KeyError: {e}")
        return graph_data
    try:
     # Add missing timestamps
       mag_df = mag_df.set_index('time_tag')
       mag_df = mag_df.reindex(timestamps_24h)
       mag_df = mag_df.fillna(0)
       mag_df = mag_df.reset_index()
       mag_df = mag_df.rename(columns={'index': 'time_tag'})

       plasma_df = plasma_df.set_index('time_tag')
       plasma_df = plasma_df.reindex(timestamps_24h)
       plasma_df = plasma_df.fillna(0)
       plasma_df = plasma_df.reset_index()
       plasma_df = plasma_df.rename(columns={'index': 'time_tag'})

       #take just last 24hrs of Kp index   
       kp_df = kp_df.set_index('time_tag')
       kp_df = kp_df.resample('min').ffill()
       kp_df = kp_df.reindex(timestamps_24h)
       kp_df = kp_df.fillna('G0')
       kp_df = kp_df.reset_index()
       kp_df = kp_df.rename(columns={'index': 'time_tag'})

      
    
    except Exception as e:
        print(f"Date parsing error: {e}")
        return graph_data
 

    try:
        graph_data['labelsplasma'] = plasma_df['time_tag'].astype(str).tolist()
        graph_data['labelsmag'] = mag_df['time_tag'].astype(str).tolist()
        graph_data['labelskp'] = kp_df['time_tag'].astype(str).tolist()
        print(graph_data['labelskp'])
        graph_data['kp'] = kp_df['kp'].tolist()
        graph_data['noaa_scale'] = kp_df['noaa_scale'].tolist()
        graph_data['chartbx'] = mag_df['bx_gsm'].tolist()
        graph_data['chartby'] = mag_df['by_gsm'].tolist()
        graph_data['chartbz'] = mag_df['bz_gsm'].tolist()
        graph_data['chartblon'] = mag_df['lon_gsm'].tolist()
        graph_data['chartlat'] = mag_df['lat_gsm'].tolist()
        graph_data['chartbt'] = mag_df['bt'].tolist()
        graph_data['chartdensity'] = plasma_df['density'].tolist()
        graph_data['chartspeed'] = plasma_df['speed'].tolist()
        graph_data['chartemperature'] = plasma_df['temperature'].tolist()
    except KeyError as e:
        print(f"KeyError while filling graph data: {e}")
    except Exception as e:
        print(f"Error preparing graph data: {e}")

    return graph_data


