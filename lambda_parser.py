import boto3
import csv
import os
from bs4 import BeautifulSoup
from datetime import datetime

# Configuración
SOURCE_BUCKET = "landing-casas-xxx"
DEST_BUCKET = "casas-final-xxx"

s3 = boto3.client("s3")

def parse_html(html):
    """ Extrae la información de cada apartaestudio """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for listing in soup.find_all("div", class_="listing"):  # Ajustar clase según HTML real
        try:
            barrio = listing.find("span", class_="location").text.strip()
            valor = listing.find("span", class_="price").text.strip()
            num_habitaciones = listing.find("span", class_="rooms").text.strip()
            num_banos = listing.find("span", class_="baths").text.strip()
            mts2 = listing.find("span", class_="size").text.strip()
            
            results.append([datetime.today().strftime('%Y-%m-%d'), barrio, valor, num_habitaciones, num_banos, mts2])
        except AttributeError:
            continue

    return results

def process_html_file(bucket, key):
    """ Descarga el HTML desde S3, extrae la información y la guarda en CSV """
    response = s3.get_object(Bucket=bucket, Key=key)
    html = response["Body"].read().decode("utf-8")
    
    parsed_data = parse_html(html)
    
    if parsed_data:
        csv_filename = key.replace("html", "csv")
        csv_path = f"/tmp/{os.path.basename(csv_filename)}"
        
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["FechaDescarga", "Barrio", "Valor", "NumHabitaciones", "NumBanos", "mts2"])
            writer.writerows(parsed_data)

        s3.upload_file(csv_path, DEST_BUCKET, csv_filename)
        print(f"✅ CSV guardado en S3: {csv_filename}")

def lambda_handler(event, context):
    """ Función principal que se ejecuta al recibir un archivo en S3 """
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]
        print(f"📥 Procesando archivo: {key}")
        process_html_file(bucket, key)

    return {"status": "ok"}
