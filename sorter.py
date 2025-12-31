import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import shutil
from send2trash import send2trash

from Keybinds import bind_keyboard_shortcuts

###
# left to add:
# private delete folder that empties at the end
#
# make it executable from outside unix
#
# if the selected folder has no images, prompt to
# ask for different folder
#
# delete + backspace delete photos
#
# tab makes new folder
###

SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", "mp4")

class PhotoSorterApp:
    def is_video(self, path: Path):
        return path.suffix.lower() == ".mp4"
    
    def __init__(self, root):
        self.undo_stack = []
        self.root = root
        self.root.title("Photo Sorter")

        #self.home_dir = Path.home()
        self.images = []
        self.index = 0
        self.current_image_path = None
        self.tk_image = None

        self.build_ui()
        bind_keyboard_shortcuts(self)
        self.select_source_folder()

    def build_ui(self):
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side="top", fill="both", expand=True)

        self.image_frame = tk.Frame(self.content_frame, height=500)
        self.image_frame.pack(side="top", fill="x")
        self.image_frame.pack_propagate(False)

        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack(expand=True)
        
        

        # Scroll container
        self.folder_canvas = tk.Canvas(self.content_frame, height=220)
        self.folder_scrollbar = tk.Scrollbar(
            self.content_frame, orient="vertical", command=self.folder_canvas.yview
        )

        self.folder_canvas.configure(yscrollcommand=self.folder_scrollbar.set)

        self.folder_scrollbar.pack(side="right", fill="y")
        self.folder_canvas.pack(side="left", fill="x", padx=10)

        self.folder_frame = tk.Frame(self.folder_canvas)
        self.folder_canvas.create_window(
            (0, 0), window=self.folder_frame, anchor="nw"
        )

        # Ensure scrolling works
        self.folder_frame.bind(
            "<Configure>",
            lambda e: self.folder_canvas.configure(
                scrollregion=self.folder_canvas.bbox("all")
            )
        )

                # Fixed bottom action bar
        self.action_frame = tk.Frame(self.root)
        self.action_frame.pack(side="bottom", fill="x", pady=10)

        self.new_folder_btn = tk.Button(
            self.action_frame,
            text="➕ New Folder",
            command=self.create_new_folder
        )
        self.new_folder_btn.pack(side="left", padx=10)

        self.undo_btn = tk.Button(
            self.action_frame,
            text="↩ Undo",
            command=self.undo_last_action
        )
        self.undo_btn.pack(side="left", padx=10)

        self.delete_btn = tk.Button(
            self.action_frame,
            text="🗑 Delete Photo",
            fg="red",
            command=self.delete_image
        )
        self.delete_btn.pack(side="right", padx=10)


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

    # def load_image(self):
    #     if self.index >= len(self.images):
    #         messagebox.showinfo("Done", "All photos sorted!")
    #         self.root.quit()
    #         return

    #     self.current_image_path = self.images[self.index]

    #     img = Image.open(self.current_image_path)
    #     img.thumbnail((900, 700))
    #     self.tk_image = ImageTk.PhotoImage(img)

    #     self.image_label.config(image=self.tk_image)
        
    def load_image(self):
        if self.index >= len(self.images):
            messagebox.showinfo("Done", "All files sorted")
            self.root.quit()
            return
        self.current_image_path = self.images[self.index]
        if self.is_video(self.current_image_path):
            self.image_label.config(
                image = "",
                text = f"Video File\n\n{self.current_image_path.name}",
                font = ("Helvetica", 16),
                justify = "center"
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
        destination = target_folder / self.current_image_path.name

        if destination.exists():
            messagebox.showerror("Error", "File already exists in target folder.")
            return

        shutil.move(self.current_image_path, destination)

        self.undo_stack = [{
            "type": "move",
            "from": destination,
            "to": self.current_image_path
        }]

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
    
    def delete_image(self):
        if not self.current_image_path:
            return

        confirm = messagebox.askyesno(
            "Delete Photo",
            f"Move '{self.current_image_path.name}' to Trash?"
        )

        self.root.focus_force()

        if not confirm:
            return

        self.undo_stack = [{
            "type": "delete",
            "path": self.current_image_path
        }]

        send2trash(str(self.current_image_path))

        self.index += 1
        self.load_image()

    def undo_last_action(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        action = self.undo_stack.pop()

        if action["type"] == "move":
            shutil.move(action["from"], action["to"])
            self.index -= 1
            self.load_image()

        elif action["type"] == "delete":
            messagebox.showinfo(
                "Undo Delete",
                "Undo for delete requires restoring from Trash manually."
            )



if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSorterApp(root)
    root.mainloop()
