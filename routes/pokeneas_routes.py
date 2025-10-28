from flask import Blueprint, jsonify, render_template
from random import choice
import socket
import os
import boto3
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from models.pokeneas_data import pokeneas

pokenea_bp = Blueprint('pokenea_bp', __name__)

# Variables de entorno esperadas
# Configuración directa del bucket público
S3_BUCKET = "bucketgabsab"
AWS_REGION = "us-east-1"


from botocore import UNSIGNED
from botocore.client import Config

def obtener_imagenes_s3():
    """
    Obtiene imágenes de un bucket S3 público usando boto3 sin requerir credenciales.
    """
    try:
        # Conexión sin firma (no necesita credenciales)
        s3 = boto3.client("s3", region_name=AWS_REGION, config=Config(signature_version=UNSIGNED))
        
        # Si tus imágenes están dentro de una carpeta (por ejemplo 'imagenes/')
        objetos = s3.list_objects_v2(Bucket=S3_BUCKET, Prefix="imagenes/")
        
        imagenes = [
            f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
            for obj in objetos.get("Contents", [])
            if obj["Key"].lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        return imagenes

    except Exception as e:
        print(f"⚠️ Error accediendo al bucket S3: {e}")
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
