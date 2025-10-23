from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Song)
admin.site.register(CustomUser)
admin.site.register(Artista)
admin.site.register(ArtistaAlbum)
admin.site.register(AlbumCancion)
admin.site.register(Playlist)
admin.site.register(PlaylistCanciones)
admin.site.register(Reaccion)
admin.site.register(Reproduccion)
admin.site.register(HistorialReproducciones)