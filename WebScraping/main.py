import requests
from bs4 import BeautifulSoup
import json
from geopy.geocoders import OpenCage
from geopy.exc import GeocoderServiceError
import time
import re
from flask import Flask, jsonify
import threading

OPENCAGE_API_KEY = 'abdb3fe6abf0445499929e2f2bf4f579'
ID_POST_BASE = '2024022317'

app = Flask(_name_)

data_cache = []

@app.route('/recepciondedatos', methods=['GET'])
def mostrar_datos():
    global data_cache
    return jsonify(data_cache), 200

def run_flask():
    app.run(port=5000)

threading.Thread(target=run_flask, daemon=True).start()

def clean_address(address):
    replacements = {
        r'\bAV\b': 'Avenida',
        r'\bJR\b': 'Jiron',
        r'\bCL\b': 'Calle',
        r'\bCRUCE\b': 'con',
        r'\bDE\b': ''
    }
    for abbr, full in replacements.items():
        address = re.sub(abbr, full, address, flags=re.IGNORECASE)
    return re.sub(r'[^a-zA-Z0-9\s]', '', address).strip()

def get_coordinates_opencage(address, api_key):
    try:
        location = OpenCage(api_key).geocode(address, timeout=10)
        return (location.latitude, location.longitude) if location else None
    except GeocoderServiceError as e:
        print(f"Error geocoding {address}: {e}")
        return None

def fetch_and_update_data():
    global data_cache
    url = 'https://sgonorte.bomberosperu.gob.pe/24horas'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    rows = table.find_all('tr')[1:] if table else []

    data = []
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 5:
            id_post = cols[0].text.strip()
            fecha_y_hora = cols[1].text.strip()
            direccion = clean_address(cols[2].text.strip()) + ", Peru"
            tipo = cols[3].text.strip()
            link = cols[4].find('a')
            entry = {
                'id_post': id_post,
                'fecha_hora': fecha_y_hora,
                'ubicacion': direccion,
                'tipo': tipo,
                'coordenada': get_coordinates_opencage(direccion, OPENCAGE_API_KEY),
                'tipo_alerta': 'emergencia',
                'link': link['href'] if link else None,
            }
            data.append(entry)
            if id_post == ID_POST_BASE:
                break  # Stop processing further rows once we reach the ID_POST_BASE
            time.sleep(1)

    new_data = [item for item in data if item not in data_cache]
    data_cache.extend(new_data)
    print(json.dumps(new_data, indent=4, ensure_ascii=False))

if _name_ == '_main_':
    while True:
        fetch_and_update_data()
        print("Esperando 2 minutos para la próxima actualización...")
        time.sleep(120)