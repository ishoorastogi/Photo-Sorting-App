##deletion

from tkinter import messagebox
import shutil
import media_loader

PRIVATE_TRASH_NAME = "._trash-temp"

def ensure_private_trash(app):
    trash_dir = app.source_dir / PRIVATE_TRASH_NAME
    trash_dir.mkdir(exist_ok=True)
    return trash_dir


def delete_current_image(app):
    if not app._try_lock():
        return
    try:
        ...
    finally:
        app.root.after(80, app._unlock)
    media_loader.stop_video(app)
    if not app.current_image_path:
        return

    confirm = messagebox.askyesno(
        "Delete Photo",
        f"Move '{app.current_image_path.name}' to Trash?"
    )

    app.root.focus_force()

    if not confirm:
        return

    trash_dir = ensure_private_trash(app)
    destination = trash_dir / app.current_image_path.name

    # Handle name collisions
    counter = 1
    while destination.exists():
        destination = trash_dir / f"{destination.stem}_{counter}{destination.suffix}"
        counter += 1

    shutil.move(app.current_image_path, destination)

    app.undo.push_delete(moved_to=destination, restore_to=app.current_image_path)

    app.index += 1
    app.load_image()