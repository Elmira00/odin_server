import os
import uuid
from django.db import models
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import unquote

from django.utils import timezone

def logo_dir_wrapper(instance, filename):
    if not instance.created_at:
        raise ValueError("❌ created_at is None.")
    year = instance.created_at.strftime("%Y")
    month = instance.created_at.strftime("%m")
    day = instance.created_at.strftime("%d")
    source_id = instance.source.id if instance.source else "unknown"
    return os.path.join("main", str(source_id), year, month, day, filename)


import os
import requests
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

def download_and_resize_image(url, instance, max_long_edge=720):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"
        }
        response = requests.get(url, timeout=10, headers=headers)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))

        if image.mode in ("RGBA", "LA"):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        else:
            image = image.convert("RGB")

        width, height = image.size
        long_edge = max(width, height)
        if long_edge > max_long_edge:
            scale = max_long_edge / long_edge
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        buffer = BytesIO()
        image.save(buffer, format="JPEG", quality=70, optimize=True)
        buffer.seek(0)

        filename = os.path.basename(url).split("?")[0] or "image.jpg"
        if not filename.lower().endswith(('.jpg', '.jpeg')):
            filename = f"{os.path.splitext(filename)[0]}.jpg"

        return ContentFile(buffer.read(), name=filename)

    except Exception as e:
        print(f"[⚠️ IMAGE DOWNLOAD ERROR] {url} - {e}")
        return None



from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid

def telegram_buffer_to_django_file(buffer, photo_id):
    buffer.seek(0)
    file_name = f"{photo_id}.jpg"
    django_file = InMemoryUploadedFile(
        file=buffer,
        field_name="image",
        name=file_name,
        content_type="image/jpeg",
        size=len(buffer.getvalue()),
        charset=None
    )
    return django_file


def build_telegram_image_url(channel_url, message_id, photo_obj):
    try:
        photo_id = photo_obj.id
        return f"{channel_url}/{message_id}?media={photo_id}"
    except:
        return None
