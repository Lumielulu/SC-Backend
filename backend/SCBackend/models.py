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
