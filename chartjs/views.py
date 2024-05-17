from datetime import datetime, timedelta
from django.shortcuts import render 
from django.views.generic import View 
import requests
from rest_framework.views import APIView 
from rest_framework.response import Response 

class HomeView(View): 
	def get(self, request, *args, **kwargs): 
         return render(request, 'chartjs/index.html') 

class ChartData(APIView):    
    authentication_classes = [] 
    permission_classes = [] 
    def get(self, request, format = None):
        #obtenemos desde los JSON url la data
        mag_json_url = 'https://services.swpc.noaa.gov/products/solar-wind/mag-1-day.json'
        plasma_json_url = 'https://services.swpc.noaa.gov/products/solar-wind/plasma-1-day.json'
        mag_response = requests.get(mag_json_url)
        plasma_response = requests.get(plasma_json_url)
         # Convertimos los datos JSON en diccionarios
        mag_data = mag_response.json()
        plasma_data = plasma_response.json()
        
        # Preparamos los datos para el gráfico
        graph_data = prepare_graph_data(mag_data, plasma_data)
        return Response(graph_data)


def prepare_graph_data(mag_data, plasma_data):
    # Crea un diccionario para almacenar los datos del gráfico
    graph_data = {
        "labels": [],
        "chartspeed": [],
        "chartdensity": [],
        "chartemperature": [],
        "chartbx": [],
        "chartby": [],
        "chartbz": [],
        "chartblon": [],
        "chartlat": [],
        "chartbt": [],
    }
    # Itera sobre los datos de magnetismo
    for item in mag_data[1:]:
        if isinstance(item, list):
            timestamp_str = item[0]  
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f') 
            density = item[1] if item[1] is not None else None 
            speed = item[2] if item[2] is not None else None 
            temperature= item[3] if item[3] is not None else None 
            graph_data['chartbx'].append(item[1] if item[1] is not None else None)
            graph_data['chartby'].append(item[2] if item[2] is not None else None)
            graph_data['chartbz'].append(item[3] if item[3] is not None else None)
            graph_data['chartblon'].append(item[4] if item[4] is not None else None)
            graph_data['chartlat'].append(item[5] if item[5] is not None else None)
            graph_data['chartbt'].append(item[6] if item[6] is not None else None)

    # Iterar sobre los datos de plasma
    for item in plasma_data[1:]:
        if isinstance(item, list):
            timestamp_str = item[0]  # Assuming the timestamp is in the first position
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f') 
            density = item[1] if item[1] is not None else None 
            speed = item[2] if item[2] is not None else None 
            temperature= item[3] if item[3] is not None else None 
            graph_data['chartdensity'].append(item[1] if item[1] is not None else None)
            graph_data['chartspeed'].append(item[2] if item[2] is not None else None)
            graph_data['chartemperature'].append(item[3] if item[3] is not None else None)
            if temperature is not None and isinstance(temperature, (int, float)):
                scientific_notation = f"{float(temperature):.2e}"
                graph_data['chartemperature'].append(scientific_notation)
            else:
                graph_data['chartemperature'].append(None)
            # Añadir el tiempo al gráfico
            graph_data['labels'].append(timestamp.strftime('%H:%M'))

    return graph_data

