import json
import os
import requests
from datetime import date
import boto3
from botocore.exceptions import ClientError

def download_page(page_index, curr_date):

    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }

    response = requests.get(f"https://casas.mitula.com.co/find?page={page_index}&operationType=sell&propertyType=mitula_studio_apartment&geoId=mitula-CO-poblacion-0000014156&text=Bogot%C3%A1%2C++%28Cundinamarca%29", headers=headers)

    if response.status_code == 200:
        print(f"✅ Página {page_index} descargada correctamente")

        file_name = f"/tmp/landing-casas-{curr_date}/{page_index:03}.html"

        with open(file_name, "w") as file:
            file.write(response.text)

        print(f"✅ Página {page_index} guardada correctamente")
        return file_name
    else:
        print(f"❌ Error {response.status_code} al descargar la página {page_index}")

def delete_directory(directory):
    if os.path.exists(directory):  # Verifica que el directorio existe
        for file in os.listdir(directory):  # Lista archivos y carpetas dentro
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):  # Si es un archivo, lo elimina
                os.remove(file_path)
            elif os.path.isdir(file_path):  # Si es un directorio, lo borra recursivamente
                delete_directory(file_path)
        os.rmdir(directory)  # Finalmente borra el directorio vacío
    else:
        print(f"⚠️ El directorio '{directory}' no existe.")

        import logging

def upload_file(file_name, bucket, object_name=None):

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name.replace("/tmp/", "")

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
        print(f"✅ Archivo '{file_name}' subido correctamente al bucket '{bucket}' con nombre '{object_name}'")
    except ClientError as e:
        print(f"❌ Error al subir el archivo '{file_name}' al bucket '{bucket}' con nombre '{object_name}': {e}")
        return False
    return True

def upload_pages(files):
    [upload_file(file, "guadar-html") for file in files]


def app(event, context):
    curr_date = date.today().strftime("%Y-%m-%d")
    os.makedirs(f"/tmp/landing-casas-{curr_date}", exist_ok=True)
    pages = [download_page(i, curr_date) for i in range(1, 11)]
    print(pages)
    upload_pages(pages)
    delete_directory(f"/tmp/landing-casas-{curr_date}", )
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Se descargaron las páginas",
        }),
    }