from SCBackend.models import Song, AudioVariant

def ingest_song(song_id: int, src_path: str, prefix: str, abrs=(64,96,128)):
    # 1) Normaliza/codifica y segmenta por bitrate (FFmpeg)
    # 2) Sube a S3 con content-type y cache correctos
    # 3) Construye master.m3u8 y súbelo
    # 4) Actualiza DB:
    song = Song.objects.get(id=song_id)
    song.hls_prefix = f"tracks/{prefix}/"
    song.published = True
    song.save()
    for a in abrs:
        AudioVariant.objects.update_or_create(song=song, abr_kbps=a, defaults={"is_published": True})
