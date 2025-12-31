##deletion

from tkinter import messagebox
from send2trash import send2trash


def delete_current_image(app):
    
    if not app.current_image_path:
        return

    confirm = messagebox.askyesno(
        "Delete Photo",
        f"Move '{app.current_image_path.name}' to Trash?"
    )

    # Prevent focus loss after dialog
    app.root.focus_force()

    if not confirm:
        return

    app.undo_stack = [{
        "type": "delete",
        "path": app.current_image_path
    }]

    send2trash(str(app.current_image_path))

    app.index += 1
    app.load_image()
