import boto3
import requests
from datetime import datetime

# Configuración
BUCKET_NAME = "landing-casas-xxx"
BASE_URL = "https://casas.mitula.com.co/apartaestudio/bogota?page={}"
HEADERS = {"User-Agent": "Mozilla/5.0"}

s3 = boto3.client("s3")

def download_pages():
    today = datetime.today().strftime('%Y-%m-%d')
    
    for page in range(1, 11):  # Descargar las primeras 10 páginas
        url = BASE_URL.format(page)
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            filename = f"{today}/page_{page}.html"
            s3.put_object(Bucket=BUCKET_NAME, Key=filename, Body=response.text)
            print(f"✅ Página {page} guardada en S3: {filename}")
        else:
            print(f"❌ Error al descargar la página {page}")

def lambda_handler(event, context):
    download_pages()
    return {"status": "ok"}
