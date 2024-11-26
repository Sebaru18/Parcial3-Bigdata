import boto3
import csv
from bs4 import BeautifulSoup
from datetime import datetime
import os

s3 = boto3.client('s3')

def handler(event, context):
    # Obtener detalles del evento S3
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    raw_key = event['Records'][0]['s3']['object']['key']
    
    # Descargar el archivo HTML
    response = s3.get_object(Bucket=bucket_name, Key=raw_key)
    html_content = response['Body'].read().decode('utf-8')
    
    # Procesar el HTML con BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    headlines = []

    # Verificar qué periódico es
    if "eltiempo" in raw_key:
        periodico = "eltiempo"
        base_url = "https://www.eltiempo.com"
    elif "publimetro" in raw_key:
        periodico = "publimetro"
        base_url = "https://www.publimetro.co"
    else:
        print("Periódico desconocido en la ruta del archivo.")
        return

    # Extraer titulares y enlaces
    for article in soup.find_all('a', href=True):  # Cambia el selector según la estructura del HTML
        try:
            # Obtener el enlace completo
            link = article['href']
            if not link.startswith("http"):
                link = base_url + link
            
            # Procesar la categoría y el titular
            if periodico == "eltiempo":
                # Estructura: https://www.eltiempo.com/categoria/titular
                path_parts = link.replace(base_url, "").split("/")
                if len(path_parts) >= 3:
                    category = path_parts[1].replace("-", " ").capitalize()
                    headline = path_parts[2].replace("-", " ").capitalize()
                else:
                    category = path_parts[1].replace("-", " ").capitalize()
                    headline = "Sin titular"
            elif periodico == "publimetro":
                # Estructura: /categoria/yyyy/mm/dd/titular
                path_parts = link.replace(base_url, "").split("/")
                if len(path_parts) >= 5:
                    category = path_parts[1].replace("-", " ").capitalize()
                    headline = " ".join(path_parts[5:]).replace("-", " ").capitalize()
                else:
                    category = path_parts[1].replace("-", " ").capitalize()
                    headline = "Sin titular"
            
            # Añadir la información procesada a la lista
            headlines.append([category, headline, link])
        except Exception as e:
            print(f"Error procesando un artículo: {e}")
            continue
    
    if not headlines:
        print("No se encontraron titulares. Revisa la estructura del HTML.")
        return

    # Preparar estructura para guardar en S3
    today = datetime.now()
    year, month, day = today.year, today.month, today.day
    csv_key = f"headlines/final/periodico={periodico}/year={year}/month={month}/day={day}/headlines.csv"

    # Crear y escribir el CSV en memoria
    csv_content = "Categoría,Titular,Enlace\n"
    for headline in headlines:
        csv_content += ",".join(headline) + "\n"
    
    # Subir el CSV a S3
    s3.put_object(
        Bucket=bucket_name,
        Key=csv_key,
        Body=csv_content.encode('utf-8'),
        ContentType='text/csv'
    )
    print(f"Archivo procesado y guardado en: {csv_key}")
