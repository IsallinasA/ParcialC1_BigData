from datetime import date
import json
import re
import os
import boto3
import csv
from botocore.exceptions import ClientError
from bs4 import BeautifulSoup


def extract_info(html_content, curr_date):
    soup = BeautifulSoup(html_content, 'html.parser')
    data = []

    for house in soup.find_all("a", class_="listing listing-card"):
        valor = house.get("data-price")
        barrio = house.get("data-location")
        num_habitaciones = house.get("data-rooms")
        mts2 = house.get("data-floorarea")
        
        num_banos = 0
        banos_tag = house.find("p", {"data-test": "bathrooms"})
        if banos_tag:
            num_banos = banos_tag.text.strip().split()[0]
        
        data.append([
            curr_date, barrio, valor, num_habitaciones, num_banos, mts2
        ])
    
    return data


def save_to_csv(data, filename):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            'FechaDescarga', 'Barrio', 'Valor', 'NumHabitaciones', 'NumBanos', 'mts2'
        ])
        writer.writerows(data)


def upload_file(file_name, bucket, object_name=None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name.replace("/tmp/", "")

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_name, bucket, object_name)
        print(
            f"✅ Archivo '{file_name}' subido correctamente "
            f"al bucket '{bucket}' con nombre '{object_name}'"
        )
    except ClientError as e:
        print(
            f"❌ Error al subir el archivo '{file_name}' "
            f"al bucket '{bucket}' con nombre '{object_name}': {e}"
        )
        return False
    return True


HTML_EXTENSION = re.compile(r".*\.html$", re.IGNORECASE)


def app(event, context):
    record = event["Records"][0]

    if not HTML_EXTENSION.match(record["s3"]["object"]["key"]):
        print("❌ El archivo no es un HTML")
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "El archivo no es un HTML"}),
        }

    file = record["s3"]["object"]["key"]

    s3_client = boto3.client('s3')
    try:
        response = s3_client.get_object(
            Bucket=record["s3"]["bucket"]["name"], Key=file
        )
        html_content = response['Body'].read().decode('utf-8')
    except ClientError as e:
        print(
            f"❌ Error al descargar el archivo '{file}' "
            f"del bucket '{record['s3']['bucket']['name']}': {e}"
        )
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Error al descargar el archivo"}),
        }

    curr_date = date.today().strftime("%Y-%m-%d")
    os.makedirs(f"/tmp/casas-final-{curr_date}", exist_ok=True)
    data = extract_info(html_content, curr_date)
    csv_file_name = (
        f"/tmp/casas-final-{curr_date}/"
        f"{str(file.split('/')[1]).replace('.html', '')}.csv"
    )
    print(f"Guardando archivo {csv_file_name}")
    save_to_csv(data, csv_file_name)
    upload_file(csv_file_name, 'guardar-csv')

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Apartaestudios guardados"}),
    }
