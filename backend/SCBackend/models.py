from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
# Create your models here.



class Artista(models.Model):
    nombre_artista = models.CharField(max_length=100)
    def __str__(self):
        return self.nombre_artista

class Song(models.Model):
    audio_file = models.FileField(upload_to='songs/', default='')
    image_file = models.FileField(upload_to='image/',default='')
    titulo = models.CharField(max_length=100)
    duracion = models.PositiveIntegerField()


    def __str__(self):
        return self.titulo or self.song_url or self.image_url
    
    #guarda la ruta fisica!
    @property
    def image_url(self):
        if self.image_file:
            return self.image_file.url
        return ''
    
    #guarda la ruta fisica!
    @property
    def song_url(self):
        if self.audio_file:
            return self.audio_file.url
        return ''


class ArtistaAlbum (models.Model):
    url_album = models.URLField(max_length=2000)
    fecha_lanzamiento = models.DateField(auto_now_add=True)
    artista = models.ForeignKey(Artista, on_delete=models.CASCADE)

class AlbumCancion(models.Model):
    id_cancion = models.ForeignKey(Song, on_delete=models.CASCADE)
    id_album   = models.ForeignKey(ArtistaAlbum, on_delete=models.CASCADE)

#inicio de relaciones playlist-usuario
class CustomUser(AbstractUser):
    image_file = models.FileField(upload_to='profile_pictures/', blank=True, null=True)

    #ruta fisica de la imagen, esta es la que se usa para obtenerlas desde la S3
    @property
    def profile_image_url(self):
        if self.image_file:
            return self.image_file.url
        return ''

    def __str__(self):
        return self.profile_image_url

class Playlist(models.Model):
    nombre_playlist = models.CharField(max_length=100, null=True, blank=True)


class PlaylistCanciones(models.Model):
    id_cancion = models.ForeignKey(Song, on_delete=models.CASCADE)
    id_playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)


class Reaccion(models.Model):
    LIKE_CHOICES = [
        ("like","Like"),
        ("dislike", "Dislike")
    ]
    like = models.CharField(max_length=10, choices=LIKE_CHOICES)
    timestamp = models.DateField(auto_now_add=True)
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cancion_id = models.ForeignKey(Song, on_delete=models.CASCADE)


class Reproduccion(models.Model):
    fecha_reproduccion = models.DateField(auto_now_add=True)
    cancion_id = models.ForeignKey(Song, on_delete=models.CASCADE)
    artista_id = models.ForeignKey(Artista, on_delete=models.CASCADE)


class HistorialReproducciones(models.Model):
    id_reproduccion = models.ForeignKey(Reproduccion, on_delete=models.CASCADE)