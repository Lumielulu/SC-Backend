import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path
from typing import Iterable

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from models import Song, AudioVariant


def run(cmd: list[str]):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        raise CommandError(f"Command failed ({p.returncode}): {' '.join(cmd)}\n{p.stdout}")
    return p.stdout


def ffmpeg_hls(src_path: Path, out_dir: Path, abrs: Iterable[int]):
    """
    Genera HLS para cada bitrate en out_dir/ABR/ con playlist hls.m3u8
    y un master.m3u8 en out_dir.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    variants = []

    for abr in abrs:
        vdir = out_dir / f"{abr}k"
        vdir.mkdir(parents=True, exist_ok=True)
        # Audio AAC CBR aproximado, segmentación 6s
        # Nota: -b:a {abr}k y lista de segmentos .ts
        cmd = [
            "ffmpeg", "-y",
            "-i", str(src_path),
            "-vn", "-acodec", "aac", "-b:a", f"{abr}k",
            "-hls_time", "6", "-hls_playlist_type", "vod",
            "-hls_segment_filename", str(vdir / "seg_%05d.ts"),
            str(vdir / "hls.m3u8"),
        ]
        run(cmd)
        variants.append((abr, f"{abr}k/hls.m3u8"))

    # master.m3u8
    master = ["#EXTM3U"]
    for abr, rel in variants:
        # BANDWIDTH aproximado (abr*1000), CODECS AAC-LC
        master.append(f'#EXT-X-STREAM-INF:BANDWIDTH={abr*1000},CODECS="mp4a.40.2"')
        master.append(rel)
    (out_dir / "master.m3u8").write_text("\n".join(master) + "\n", encoding="utf-8")


def guess_content_type(p: Path) -> str:
    ext = p.suffix.lower()
    if ext == ".m3u8":
        return "application/vnd.apple.mpegurl"
    if ext == ".ts":
        return "video/mp2t"
    return "application/octet-stream"


def upload_dir_to_s3(local_dir: Path, bucket: str, prefix: str, region: str | None = None):
    """Sube recursivamente directorio a S3 en s3://bucket/prefix/"""
    session = boto3.session.Session(region_name=region)
    s3 = session.client("s3")

    for p in local_dir.rglob("*"):
        if p.is_dir():
            continue
        key = f"{prefix.rstrip('/')}/{p.relative_to(local_dir).as_posix()}"
        extra = {
            "ContentType": guess_content_type(p),
            "CacheControl": "public, max-age=31536000" if p.suffix != ".m3u8" else "public, max-age=60",
        }
        s3.upload_file(str(p), bucket, key, ExtraArgs=extra)


class Command(BaseCommand):
    help = "Ingesta una canción: genera HLS (64/96/128 kbps), sube a S3 y actualiza la DB."

    def add_arguments(self, parser):
        parser.add_argument("--song-id", type=int, required=True, help="ID de Song")
        parser.add_argument("--src", type=str, required=True, help="Ruta al audio fuente (mp3/wav)")
        parser.add_argument("--prefix", type=str, required=True, help="prefijo HLS, ej: tracks/mi_cancion")
        parser.add_argument("--abrs", type=str, default="64,96,128", help="Lista de bitrates, ej: 64,96,128")
        parser.add_argument("--bucket", type=str, default=getattr(settings, "AWS_STORAGE_BUCKET_NAME", None),
                            help="Bucket S3 (por defecto toma settings.AWS_STORAGE_BUCKET_NAME)")
        parser.add_argument("--region", type=str, default=getattr(settings, "AWS_S3_REGION_NAME", None),
                            help="Región S3 (por defecto settings.AWS_S3_REGION_NAME)")
        parser.add_argument("--dry-run", action="store_true", help="No sube a S3 ni toca DB (solo genera HLS local)")

    def handle(self, *args, **opts):
        song_id = opts["song_id"]
        src = Path(opts["src"]).expanduser().resolve()
        prefix = opts["prefix"].strip("/")
        abrs = tuple(int(x) for x in opts["abrs"].split(",") if x.strip())
        bucket = opts["bucket"]
        region = opts["region"]
        dry = opts["dry_run"]

        if not src.exists():
            raise CommandError(f"Fuente no encontrada: {src}")
        if not abrs:
            raise CommandError("ABRs vacíos")
        if not dry and not bucket:
            raise CommandError("Bucket S3 no especificado (use --bucket o configure AWS_STORAGE_BUCKET_NAME)")

        # 1) Generar HLS en tmp
        tmp = Path(tempfile.mkdtemp(prefix="ingest_"))
        try:
            self.stdout.write(self.style.NOTICE(f"Generando HLS en {tmp}..."))
            ffmpeg_hls(src, tmp, abrs)

            # 2) Subir a S3 (si no dry-run)
            if not dry:
                self.stdout.write(self.style.NOTICE(f"Subiendo a s3://{bucket}/{prefix}/ ..."))
                upload_dir_to_s3(tmp, bucket, prefix, region)

            # 3) Actualizar DB (si no dry-run)
            if not dry:
                with transaction.atomic():
                    song = Song.objects.select_for_update().get(id=song_id)
                    song.hls_prefix = f"{prefix.rstrip('/')}/"
                    song.published = True
                    song.save()
                    for a in abrs:
                        AudioVariant.objects.update_or_create(
                            song=song, abr_kbps=a, defaults={"is_published": True}
                        )

            self.stdout.write(self.style.SUCCESS("✅ Ingesta completada."))
            if dry:
                self.stdout.write(self.style.WARNING("DRY-RUN: no se subió a S3 ni se tocó la DB."))

        finally:
            shutil.rmtree(tmp, ignore_errors=True)
