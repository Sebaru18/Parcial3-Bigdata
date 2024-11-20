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

    # Extraer categoría, titular y enlace
    for article in soup.find_all('article'):
        try:
            category = article.find('span', class_='category').text.strip()
            headline = article.find('h2', class_='headline').text.strip()
            link = article.find('a', href=True)['href']
            headlines.append([category, headline, link])
        except AttributeError:
            continue

    # Preparar estructura para guardar en S3
    today = datetime.now()
    year, month, day = today.year, today.month, today.day
    periodico = "eltiempo" if "eltiempo" in raw_key else "elespectador"
    csv_key = f"headlines/final/periodico={periodico}/year={year}/month={month}/day={day}/headlines.csv"

    # Crear CSV en memoria
    csv_content = ""
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
