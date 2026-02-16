import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import shutil
from send2trash import send2trash
from PIL import Image, ImageTk
import cv2

from Keybinds import bind_keyboard_shortcuts
from ui import build_ui
from deletion import delete_current_image
import media_loader
from undo import UndoManager


###
#
# make it executable from outside unix
#
#
#
###

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".mp4")
PRIVATE_TRASH_NAME = "._trash-temp"


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

    def select_source_folder(self):
        folder = filedialog.askdirectory(title="Select Photo Folder")
        if not folder:
            self.root.quit()
            return

        self.source_dir = Path(folder)
        self.undo.clear()
        self.images = [
            p for p in self.source_dir.iterdir()
            if p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        if not self.images:
            messagebox.showerror("Error", "No images found.")
            self.root.quit()
            return

        self.index = 0
        self.load_image()
        self.refresh_folder_buttons()
   
    def load_image(self):
        if self.index >= len(self.images):
            from cleanup import cleanup_private_trash
            cleanup_private_trash(self)

            again = messagebox.askyesno(
                "All files sorted",
                "All files have been sorted.\n\nWould you like to sort another folder?"
            )

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
                media_loader.load_video_paused(self, self.current_image_path)
            else:
                media_loader.load_image(self, self.current_image_path)
        except Exception as e:
            print("MEDIA LOAD ERROR:", e)
            self.image_label.config(
                image="",
                text=f"Could not load file:\n{self.current_image_path.name}"
            )


    def refresh_folder_buttons(self):
        for widget in self.folder_frame.winfo_children():
            widget.destroy()
        
        for folder in sorted(self.source_dir.iterdir()):
            if folder.name == PRIVATE_TRASH_NAME:
                continue
            if folder.is_dir():
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
        destination = target_folder / self.current_image_path.name

        if destination.exists():
            messagebox.showerror("Error", "File already exists in target folder.")
            return

        shutil.move(self.current_image_path, destination)
        self.undo.push_move(moved_to=destination, restore_to=self.current_image_path)

        self.index += 1
        self.load_image()


    def create_new_folder(self):
        name = simpledialog.askstring("New Folder", "Folder name:")
        if not name:
            return

        new_folder = self.source_dir / name
        try:
            new_folder.mkdir()
            self.refresh_folder_buttons()
        except FileExistsError:
            messagebox.showerror("Error", "Folder already exists.")

    def undo_last_action(self):
        media_loader.stop_video(self)

        action = self.undo.undo()
        if action is None:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        try:
            self.undo.apply(action)  # does shutil.move(action.src, action.dst)
        except Exception as e:
            messagebox.showerror("Undo Error", f"Could not undo:\n{e}")
            return

        if action.type == "move":
            self.index = max(self.index - 1, 0)

        elif action.type == "delete":
            self.index = max(self.index - 1, 0)

        self.load_image()




if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSorterApp(root)

    from cleanup import cleanup_private_trash

    def on_close():
        cleanup_private_trash(app)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
