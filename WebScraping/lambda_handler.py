import requests
import boto3
from bs4 import BeautifulSoup
import json
from geopy.geocoders import OpenCage
from geopy.exc import GeocoderServiceError
import re
import time

OPENCAGE_API_KEY = 'abdb3fe6abf0445499929e2f2bf4f579'

lambda_client = boto3.client('lambda', region_name='us-west-2')

def get_id_post_base():
    response = lambda_client.invoke(
        FunctionName='database_conection', 
        InvocationType='RequestResponse',
        Payload=b''
    )
    return response['Payload'].read().decode('utf-8').strip()

# Asignar el valor retornado por la Lambda a ID_POST_BASE y asegurarse de que es un string
ID_POST_BASE = str(get_id_post_base())
print(f"ID_POST_BASE: {ID_POST_BASE}")

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
        return [0,0]

def lambda_handler(event, context):
    client = boto3.client('lambda')
    url = 'https://sgonorte.bomberosperu.gob.pe/24horas'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table')
    if not table:
        print("No se encontró la tabla en la página.")
        return {
            'statusCode': 500,
            'body': json.dumps('No se encontró la tabla en la página.')
        }

    rows = table.find_all('tr')[1:]
    data = []
    n=0
    for row in rows:
        #n=n+1
        cols = row.find_all('td')
        if len(cols) >= 5:
            id_post = cols[0].text.strip()
            if id_post == ID_POST_BASE or n==5:
                print(f"Se ha alcanzado la fila con ID_POST_BASE: {ID_POST_BASE}")
                break
            fecha_y_hora = cols[1].text.strip()
            direccion = clean_address(cols[2].text.strip()) + ", Peru"
            tipo = cols[3].text.strip()
            link = cols[4].find('a')
            response_payload = {
                'id_post': id_post,
                'fecha_hora': fecha_y_hora,
                'ubicacion': direccion,
                'tipo_alerta': tipo,
                'coordenada': json.dumps(get_coordinates_opencage(direccion, OPENCAGE_API_KEY)),
                'tipo': 'emergencia',
                'link': link['href'] if link else None,
                
            }
            print(response_payload)
            
            params = {
                'FunctionName': 'LambdaBedrock',  # nombre de la función Lambda que deseas invocar
                'InvocationType': 'RequestResponse',  # 'Event' para invocación asíncrona
                'Payload': json.dumps(response_payload)
            }
            
            try:
                response = client.invoke(**params)
                response_payload = json.loads(response['Payload'].read().decode('utf-8'))
                print('Invocación exitosa:', response_payload)
            except Exception as e:
                print('Error al invocar la función Lambda:', e)
                raise e
