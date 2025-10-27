from flask import Blueprint, jsonify, render_template
from random import choice
import socket
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from models.pokeneas_data import pokeneas

pokenea_bp = Blueprint('pokenea_bp', __name__)

# Variables de entorno esperadas
S3_BUCKET = os.getenv("S3_BUCKET")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")

def obtener_imagenes_s3():
    """
    Intenta obtener las imágenes desde un bucket S3 público.
    Si no hay credenciales o hay error, devuelve una lista vacía.
    """
    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        objetos = s3.list_objects_v2(Bucket=S3_BUCKET)
        imagenes = [
            f"https://{S3_BUCKET}.s3.amazonaws.com/{obj['Key']}"
            for obj in objetos.get("Contents", [])
            if obj["Key"].lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        return imagenes
    except (NoCredentialsError, PartialCredentialsError, Exception):
        return []

@pokenea_bp.route('/pokenea-json')
def pokenea_json():
    pokenea = choice(pokeneas)
    contenedor_id = socket.gethostname()
    data = {
        "id": pokenea["id"],
        "nombre": pokenea["nombre"],
        "altura": pokenea["altura"],
        "habilidad": pokenea["habilidad"],
        "contenedor_id": contenedor_id
    }
    return jsonify(data)

@pokenea_bp.route('/pokenea-imagen')
def pokenea_imagen():
    contenedor_id = socket.gethostname()
    pokenea = choice(pokeneas)

    # Si hay un bucket configurado, intenta tomar una imagen de S3
    if S3_BUCKET:
        imagenes_s3 = obtener_imagenes_s3()
        if imagenes_s3:
            pokenea["imagen"] = choice(imagenes_s3)

    return render_template('imagen.html', pokenea=pokenea, contenedor_id=contenedor_id)
