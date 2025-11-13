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
from django.utils.decorators import method_decorator
from django.shortcuts import redirect

@method_decorator(require_http_methods(["GET"]), name='dispatch')
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
@require_http_methods(['GET'])
def get_songs(request):
    songs = Song.objects.all()
    data = [{
        'id': song.id,
        'name': song.titulo,
        'url': song.audio_file.url,
        'image_url': song.image_file.url if song.image_file else None
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


#*
#@api_view(['GET'])
#    def downloadRequestedSong(request, song_id):
#        song = get_object_or_404(Song, id = song_id)
#        file_path = song.audio_file.path

#        if not os.path.exists(file_path):
#            return JsonResponse({'success':False, 'message':'Error al obtener la ubicacion del archivo'},status = 404)
#        try:
#                response = FileResponse(open(file_path, 'rb'),as_attachment=True, filename=urllib.parse.quote(f'{song.titulo}.mp3'))
#                response["Access-Control-Allow-Origin"] = "*"
#                response["Access-Control-Expose-Headers"] = "Content-Disposition"
#                return response
#        except Exception:
#            return JsonResponse({'success':False, 'message': 'Error para descargar el archivo'}, status = 500)
# 
# 
# 
# #

    
@api_view(['GET'])
def health(request):
    return HttpResponse(status =200)

@require_http_methods(['GET'])
def streaming(request, song_id):
    #preparamos la URL del archivo para el streaming
    song = get_object_or_404(Song, id=song_id)
    return JsonResponse({
        'streaming_url': song.audio_file.url
    })
