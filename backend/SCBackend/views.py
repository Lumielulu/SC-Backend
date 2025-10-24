#api 
from rest_framework.decorators import api_view
from rest_framework import generics
import json
import os
import urllib.parse
from .serializers import UserSerializer
from .models import *
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.http import JsonResponse,FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response


@require_http_methods(['GET'])
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "username": user.username,
            "email": user.email,
            "profile_image": user.image_file.url if user.image_file else None,
        })


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



@require_http_methods(['POST'])
class RegisterView(generics.CreateAPIView):
    serializer_class = UserSerializer


@csrf_exempt
@require_http_methods(['POST'])
def regUser(request):
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        #image_file = data.get('profile_picture') #opcional
        if not username or not password:
            return JsonResponse({'success': False})
        
        user = CustomUser.objects.create_user(username = username , password=password)

        return JsonResponse({'success': True})
    except Exception as e:
        return  JsonResponse({'success':False})



@api_view(['GET'])
def getUsers(request):
    data = json.loads(request.body)
    users = CustomUser.objects.get(id = data.id) 
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)



@api_view(['GET'])
def downloadRequestedSong(request, song_id):
    song = get_object_or_404(Song, id = song_id)
    file_path = song.audio_file.path

    if not os.path.exists(file_path):
        return JsonResponse({'success':False, 'message':'Error al obtener la ubicacion del archivo'},status = 404)
    try:
            response = FileResponse(open(file_path, 'rb'),as_attachment=True, filename=urllib.parse.quote(f'{song.titulo}.mp3'))
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Expose-Headers"] = "Content-Disposition"
            return response
    except Exception:
        return JsonResponse({'success':False, 'message': 'Error para descargar el archivo'}, status = 500)
    
@api_view(['GET'])
def health(request):
    return HttpResponse(status =200)