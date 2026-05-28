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

        def _undo(event=None):
                app.undo_last_action()
                return "break"

        # Undo shortcuts
        root.bind("<Command-z>", _undo)
        root.bind("<Control-z>", _undo)

        # Also allow Escape to trigger undo (convenient alternative)
        root.bind("<Escape>", _undo)
        
        # Skip current photo "\"
        root.bind("\\", lambda e: (app.skip_current(), "break"))

        def _toggle_videos(event=None):
                app.set_show_videos(not app.show_videos)
                return "break"

        # Toggle videos visibility
        root.bind("<Command-v>", _toggle_videos)

        def _handle_quick_key(event, n):
                qa = getattr(app, "quick_actions", None)
                if not qa:
                        return "break"

                # If no modifiers, activate; if any modifier key pressed (e.g. Cmd), rename
                if getattr(event, "state", 0) == 0:
                        qa.activate(n-1)
                else:
                        qa.rename_action(n-1)
                return "break"

        for i in range(1, 5):
                # bind number key to handler that dispatches based on modifiers
                root.bind(str(i), lambda e, n=i: _handle_quick_key(e, n))
