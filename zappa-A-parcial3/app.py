import requests
import boto3
from datetime import datetime

def handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = "bucketparcial3corte"  

    
    urls = {
        "eltiempo": "https://www.eltiempo.com/",
        "publimetro": "https://www.publimetro.co/"
    }

    # Iterar sobre las URLs
    for name, url in urls.items():
        try:
            # Descargar el contenido
            response = requests.get(url)
            response.raise_for_status()  # Verifica errores HTTP
            

            fecha = datetime.now().strftime("%Y-%m-%d")
            s3_key = f"headlines/raw/contenido-{name}-{fecha}.html"

            # Subir el contenido a S3
            s3.put_object(
                Bucket=bucket_name,
                Key=s3_key,
                Body=response.content,
                ContentType="text/html"
            )
            print(f"Archivo guardado en S3: {s3_key}")
        except Exception as e:
            print(f"Error descargando {name}: {e}")
