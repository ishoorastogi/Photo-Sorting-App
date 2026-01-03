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

###
# left to add:
# private delete folder that empties at the end
#
# make it executable from outside unix
#
# if the selected folder has no images, prompt to
# ask for different folder
#
#
###

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".mp4")
PRIVATE_TRASH_NAME = "._trash-temp"


class PhotoSorterApp:
    def is_video(self, path: Path):
        return path.suffix.lower() == ".mp4"
    
    def __init__(self, root):
        self.undo_stack = []
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
        self.video_overlay.place_forget()
        if self.index >= len(self.images):
            from cleanup import cleanup_private_trash
            cleanup_private_trash(self)

            messagebox.showinfo("Done", "All files sorted")
            self.root.quit()
            return
        self.current_image_path = self.images[self.index]
        if self.is_video(self.current_image_path):
            try:
                self.load_video_paused(self.current_image_path)
            except Exception as e:
                print("VIDEO ERROR:", e)
                self.image_label.config(
                    image="",
                    text=f"Video File\n\n{self.current_image_path.name}",
                    font=("Helvetica", 16),
                    justify="center"
                )
            return

        
        try:
            img = Image.open(self.current_image_path)
            img.thumbnail((900, 700))
            self.tk_image = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.tk_image, text="")
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Could not load file:\n{self.current_image_path.name}"
            )
            self.index += 1
            self.load_image()

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
        self.stop_video()
        destination = target_folder / self.current_image_path.name

        if destination.exists():
            messagebox.showerror("Error", "File already exists in target folder.")
            return

        shutil.move(self.current_image_path, destination)

        self.undo_stack.append ({
            "type": "move",
            "from": destination,
            "to": self.current_image_path
        })

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
        self.stop_video()
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        action = self.undo_stack.pop()

        if action["type"] == "move":
            shutil.move(action["from"], action["to"])
            self.index -= 1
            self.load_image()

        elif action["type"] == "delete":
            shutil.move(action["from"], action["to"])
            self.index = max(self.index - 1, 0)
            self.load_image()

    def load_video_paused(self, path):
        self.stop_video()

        self.video_cap = cv2.VideoCapture(str(path))
        if not self.video_cap.isOpened():
            raise RuntimeError("Could not open video")

        # Read ONE frame only
        success, frame = self.video_cap.read()
        if not success:
            raise RuntimeError("Could not read first frame")

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img.thumbnail((900, 700))

        self.tk_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_image, text="")
        self.image_label.pack(expand=True)

        # IMPORTANT: start paused
        self.video_playing = False
        self.video_overlay.place(relx=0.5, rely=0.5, anchor="center")

    
    def _play_next_frame(self):
        if not self.video_playing or self.video_cap is None:
            return

        success, frame = self.video_cap.read()

        if not success:
            # Loop video (or stop here if you prefer)
            self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.video_cap.read()
            if not success:
                self.stop_video()
                return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame)
        img.thumbnail((900, 700))

        self.tk_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_image, text="")
        self.image_label.pack(expand=True)

        # ~30 FPS
        self.root.after(33, self._play_next_frame)

    def stop_video(self):
        self.video_playing = False

        if self.video_cap is not None:
            self.video_cap.release()
            self.video_cap = None
    
    def toggle_video(self):
        if self.video_cap is None:
            return

        if self.video_playing:
            self.video_playing = False
            self.video_overlay.place(relx=0.5, rely=0.5, anchor="center")
        else:
            self.video_playing = True
            self.video_overlay.place_forget()
            self._play_next_frame()




if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSorterApp(root)

    from cleanup import cleanup_private_trash

    def on_close():
        cleanup_private_trash(app)
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
