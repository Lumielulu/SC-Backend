from django.db import models

# Create your models here.


class Song(models.Model):
    audio_file = models.FileField(upload_to='songs/', default='')
    image_file = models.FileField(upload_to='image/',default='')
    titulo = models.CharField(max_length=255)

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


class User(models.Model):
    image_file = models.FileField(upload_to='profile_picture/',default='')
    username = models.CharField(max_length=20, default='', primary_key=True)
    password = models.CharField(max_length=12, default='', null=False)
    email = models.EmailField(max_length=254)
    @property
    def profile_image_url(self):
        if self.image_file:
            return self.image_file.url
        
    def __str__(self):
        return self.image_file or self.username or self.email