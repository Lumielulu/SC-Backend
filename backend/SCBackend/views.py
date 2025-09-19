#api 
import json
import os
from .models import *
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse,FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt


#este es mi backen



@csrf_exempt
@require_http_methods(['POST'])
def test_angular(request):
    data = json.loads(request.body)
    user = data.get('username')
    password = data.get('password')
    
    if user =='HOLAMUNDO' and password == '123':
        return JsonResponse({'success': True, 'username':'HOLAMUNDO', 'password': '123'})
    else:
        return JsonResponse({'success': False, 'error_messages' : 'CODE_L1'})    
    


@csrf_exempt
@require_http_methods(['GET'])
def streaming_test(request, song_id):
    #preparamos la URL del archivo para el streaming
    song = get_object_or_404(Song, id=song_id)

    
    #obtenemos la ruta FISICA de la cancion guardada, no la relativa!!!
    file_path =song.audio_file.path

    #validamos su existencia
    if not os.path.exists(file_path):
        return HttpResponse(status = 404)
    
    #preparamos el archivo mediante la funcion de fileresponse, primero abrimos el archivo, luego lo leemos y asignamos su tipo de contenido
    response = FileResponse(open(file_path,'rb'), content_type = 'audio/mpeg')
    
    #le asignamos el tipo de rango aceptado por el navegador
    response['Accept-Ranges'] = 'bytes'

    #devolvemos el audio con los bytes solicitados
    return response


@csrf_exempt
@require_http_methods(['GET'])
def get_songs(request):
    songs = Song.objects.all()
    data = [{
        'id': song.id,
        'name': song.titulo,
        'url': request.build_absolute_uri(song.audio_file.url),
        'image_url': request.build_absolute_uri(song.image_file.url), 
    } for song in songs]
    return JsonResponse(data, safe= False)

