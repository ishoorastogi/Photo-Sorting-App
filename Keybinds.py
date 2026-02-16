## Keybinds
from deletion import delete_current_image
import media_loader
import subprocess

def bind_keyboard_shortcuts(app):
        root = app.root
        
        #Delete + backspace delete photos
        root.bind("<Delete>", lambda e: (delete_current_image(app), "break"))
        root.bind("<BackSpace>", lambda e: (delete_current_image(app), "break"))

        
        #Tab makes new folder
        root.bind("<Tab>", lambda e: app.create_new_folder())

        #Spacebar is playing/pausing videos
        #enter shows them in native video app
        root.bind("<space>", lambda e: media_loader.toggle_video(app))

        root.bind(
                "<Return>",
                lambda e: subprocess.Popen(
                        ["open", str(app.current_image_path)]
                ) if app.current_image_path and app.is_video(app.current_image_path) else None
        )