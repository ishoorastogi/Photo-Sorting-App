import tkinter as tk
from pathlib import Path

from keybinds import bind_keyboard_shortcuts
from ui import build_ui
from undo import UndoManager
from file_routing import FileRouter
import media_loader
import dialogs


###
#
# make it executable from outside unix
#state manager
#file ops layer
#session completion handler
#dialogs
###

class PhotoSorterApp:
    def is_video(self, path: Path):
        return path.suffix.lower() == ".mp4"
    
    def __init__(self, root):
        self.undo = UndoManager()
        self.root = root
        self.root.title("Photo Sorter")

        self.video_cap = None
        self.video_playing = False

        self.images = []
        self.index = 0
        self.current_image_path = None
        self.tk_image = None

        build_ui(self)
        bind_keyboard_shortcuts(self)
        self.select_source_folder()

        self._action_lock = False

    def select_source_folder(self):
        folder = dialogs.pick_source_folder(self.root)
        self.refocus_app()

        if not folder:
            self.root.quit()
            return

        media_loader.stop_video(self)
        if hasattr(self, "video_overlay"):
            self.video_overlay.place_forget()

        self.source_dir = Path(folder)

        self.router = FileRouter(self.source_dir)

        self.undo.clear()
        self.images = self.router.list_media()
        self.index = 0
        self.current_image_path = None
        self.tk_image = None

        if not self.images:
            dialogs.show_no_media_error()
            self.root.quit()
            return

        self.image_label.config(image="", text="")

        self.refresh_folder_buttons()
        self.load_image()


   
    def load_image(self):
        if self.index >= len(self.images):
            from cleanup import cleanup_private_trash
            cleanup_private_trash(self)

            again = dialogs.confirm_sort_another_folder()

            if again:
                self.undo.clear()
                self.images = []
                self.index = 0
                self.current_image_path = None

                # Clear UI
                self.image_label.config(image="", text="")
                if hasattr(self, "video_overlay"):
                    self.video_overlay.place_forget()

                # Ask for new folder
                self.select_source_folder()
            else:
                self.root.quit()

            return


        self.current_image_path = self.images[self.index]

        try:
            if self.is_video(self.current_image_path):
                media_loader.render_video_paused(self, self.current_image_path)
            else:
                media_loader.render_image(self, self.current_image_path)
        except Exception as e:
            print("MEDIA LOAD ERROR:", e)
            self.image_label.config(
                image="",
                text=f"Could not load file:\n{self.current_image_path.name}"
            )


    def refresh_folder_buttons(self):
        for widget in self.folder_frame.winfo_children():
            widget.destroy()

        for folder in self.router.list_target_folders():
            if folder == self.source_dir:
                continue

            btn = tk.Button(
                self.folder_frame,
                text=folder.name,
                width=25,
                command=lambda f=folder: self.move_image(f)
            )
            btn.pack(pady=2)

    def move_image(self, target_folder):
        media_loader.stop_video(self)

        try:
            result = self.router.move(self.current_image_path, target_folder, on_collision="error")
        except FileExistsError:
            dialogs.show_file_exists_error()
            return
        except Exception as e:
            # optional: add this dialog helper if you want
            dialogs.show_move_failed_error(str(e))
            return

        self.undo.push_move(moved_to=result.dst, restore_to=result.src)

        self.index += 1
        self.load_image()

    def create_new_folder(self):
        name = dialogs.ask_new_folder_name(self.root)
        
        self.refocus_app()
        
        if not name:
            return

        new_folder = self.source_dir / name
        try:
            new_folder.mkdir()
            self.refresh_folder_buttons()
        except FileExistsError:
            dialogs.show_folder_exists_error()

    def undo_last_action(self):
        if not self._try_lock():
            return

        try:
            media_loader.stop_video(self)

            action = self.undo.undo()
            if action is None:
                return

            self.undo.apply(action)

            self.index = max(self.index - 1, 0)
            self.load_image()

        finally:
            self.root.after(80, self._unlock)

    def _try_lock(self):
        if self._action_lock:
            return False
        self._action_lock = True
        return True

    def _unlock(self):
        self._action_lock = False
    
    def refocus_app(self):
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(10, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSorterApp(root)

    from cleanup import cleanup_private_trash

    def on_close():
        cleanup_private_trash(app)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()