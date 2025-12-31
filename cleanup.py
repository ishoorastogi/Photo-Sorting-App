##cleanup

from send2trash import send2trash
from pathlib import Path

PRIVATE_TRASH_NAME = "._trash-temp"

def cleanup_private_trash(app):
    trash_dir = app.source_dir / PRIVATE_TRASH_NAME

    if trash_dir.exists() and any(trash_dir.iterdir()):
        send2trash(str(trash_dir))