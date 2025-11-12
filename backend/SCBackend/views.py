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
    data = []
    for song in songs:
        item= {
            'id': song.id,
            'name': song.titulo,
            'image_url': song.image_url,
        }
        if song.published and song.hls_prefix:
            item['stream_url']=request.build_absolute_uri(reversed('streaming_master', args=[song.id]))
        data.append(item) 
    
    return JsonResponse(data, safe=False)



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


def sign_s3_path(path: str) -> str:
    #firnma la URL para acceso publico temporal
    return f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{path.lstrip('/')}"

@api_view(['GET'])
def stream_master(request, song_id: int):
    #preparamos la URL del master.m3u8 para el streaming HLS
    song = get_object_or_404(Song, id=song_id, published=True)
    if not song.hls_prefix:
        return Response({"detail": "Track no preparado en HLS."}, status=409)
    return redirect(sign_s3_path(song.master_key()))  # 302 al master.m3u8