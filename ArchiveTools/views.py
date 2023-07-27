from django.shortcuts import render, HttpResponse ,redirect

from django.conf import settings
import magic
import os
from datetime import datetime
import hashlib
import tempfile
import zipfile
import exiftool
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.forms import UserCreationForm
# Create your views here.
@csrf_exempt
def compareHash(request):
    if request.method == 'POST':
        archivo_original = request.FILES.get('archivo_original')
        archivo_copia = request.FILES.get('archivo_copia')

        if archivo_original and archivo_copia:
            hash_original = calcular_hash(archivo_original)
            hash_copia = calcular_hash(archivo_copia)

            hashes = {
                'original': hash_original,
                'copia': hash_copia,
                'mismos': hash_original == hash_copia,
            }

            return render(request, 'ArchiveTools/compareHash.html', {'hashes': hashes})

    return render(request, 'ArchiveTools/compareHash.html')

def calcular_hash(archivo):
    sha256_hash = hashlib.sha256()
    for chunk in archivo.chunks():
        sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

@csrf_exempt
def extractMetadata(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        archivo_path = os.path.join('temp', archivo.name)

        # Guarda el archivo temporalmente
        with open(archivo_path, 'wb') as temp_file:
            for chunk in archivo.chunks():
                temp_file.write(chunk)

        try:
            # Extrae los metadatos utilizando pyexiftool
            with exiftool.ExifTool() as et:
                metadatos = et.execute_json("-G", archivo_path)

            # Borra el archivo temporal
            os.remove(archivo_path)

            # Devuelve los metadatos como respuesta
            response = HttpResponse(str(metadatos), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=metadatos.json'
            return response

        except Exception as e:
            # Si ocurre un error, borra el archivo temporal y muestra un mensaje de error
            os.remove(archivo_path)
            return HttpResponse(f"Error al extraer metadatos: {str(e)}")

    return render(request, 'ArchiveTools/extractMetadata.html')

@csrf_exempt
def viewFormat(request):
    if request.method == 'POST':
        archivo = request.FILES['archivo']
        nombre_archivo, extension_original = os.path.splitext(archivo.name)
        tipo_archivo = magic.from_buffer(archivo.read(), mime=True)
        archivo.seek(0)  # Reiniciar el puntero de lectura al inicio del archivo
        fecha_creacion = datetime.now()
        fecha_modificacion = archivo.name
        formato_original = extension_original[1:].lower()  # Obtener la extensión original sin el punto y en minúsculas

        advertencia = ''
        if tipo_archivo.lower() != formato_original:
            advertencia = 'Formato incorrecto'

        return render(request, 'ArchiveTools/resultViewFormat.html', {'tipo_archivo': tipo_archivo, 'fecha_creacion': fecha_creacion, 'fecha_modificacion': fecha_modificacion, 'formato_original': formato_original, 'advertencia': advertencia})
    
    return render(request, 'ArchiveTools/viewFormat.html')
@csrf_exempt
def generetaHash(request):
    if request.method == 'POST' and request.FILES['archivo']:
        archivo = request.FILES['archivo']
        contenido = archivo.read()

        # Calcula el hash del contenido del archivo utilizando la función hash de Python
        hash_resultado = hashlib.sha256(contenido).hexdigest()

        try:
            # Crea un archivo temporal en el sistema de archivos para el archivo original
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(contenido)

            # Crea un archivo temporal para el archivo de texto con el hash
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as hash_file:
                hash_file.write(hash_resultado.encode())

            # Crea un archivo ZIP en memoria
            buffer = tempfile.SpooledTemporaryFile()
            with zipfile.ZipFile(buffer, 'w') as zip_file:
                # Agrega el archivo original al ZIP
                zip_file.write(temp_file.name, archivo.name)

                # Agrega el archivo de texto con el hash al ZIP
                zip_file.write(hash_file.name, f'{archivo.name}.txt')

            # Prepara el archivo ZIP para ser entregado al usuario como descarga
            buffer.seek(0)
            contenido_temporal = buffer.read()

            # Elimina los archivos temporales después de leer su contenido
            os.remove(temp_file.name)
            os.remove(hash_file.name)

            # Devuelve el archivo ZIP como descarga
            response = HttpResponse(contenido_temporal, content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename=archivo_con_hash.zip'
            return response

        except Exception as e:
            # En caso de error, asegúrate de eliminar los archivos temporales si aún existen
            if os.path.exists(temp_file.name):
                os.remove(temp_file.name)
            if os.path.exists(hash_file.name):
                os.remove(hash_file.name)
            raise e

    return render(request, 'ArchiveTools/generetaHash.html')


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            # Redireccionar al usuario a la página de inicio después del registro
            return redirect('extractMetadata')
    else:
        form = UserCreationForm()

    return render(request, 'Archivetools/register.html', {'form': form})




