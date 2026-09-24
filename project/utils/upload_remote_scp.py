import os
import subprocess


REMOTE_MEDIA_SERVER = {
    "host": "192.168.0.62",
    "user": "rv",
    "remote_path": "/home/rv/media",
    "url": "http://192.168.0.62/media"
}


def upload_to_remote(local_path, remote_subpath):
    remote_full_path = os.path.join(REMOTE_MEDIA_SERVER['remote_path'], remote_subpath)
    remote_dir = os.path.dirname(remote_full_path)

    # Remote dizini oluştur
    subprocess.run(
        f"ssh {REMOTE_MEDIA_SERVER['user']}@{REMOTE_MEDIA_SERVER['host']} 'mkdir -p {remote_dir}'",
        shell=True, check=True
    )

    # Dosyayı SCP ile gönder
    subprocess.run(
        f"scp -q -C -p {local_path} {REMOTE_MEDIA_SERVER['user']}@{REMOTE_MEDIA_SERVER['host']}:{remote_full_path}",
        shell=True, check=True
    )

    # Remote URL döndür
    return f"{REMOTE_MEDIA_SERVER['url']}/{remote_subpath.replace(os.sep, '/')}"
