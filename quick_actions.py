# quick_actions.py
import tkinter as tk
from pathlib import Path

class QuickActionsBar:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = tk.Frame(parent_frame)
        self.frame.pack(fill="x", pady=5)

        # Default quick folders (can be made configurable later)
        self.quick_folders = {
            "Misc": "Misc",
            "Gym": "Gym",
            "Buddy": "Buddy",
            "Travel": "Travel"
        }

        self.build_buttons()

    def build_buttons(self):
        for label, folder_name in self.quick_folders.items():
            btn = tk.Button(
                self.frame,
                text=label,
                width=12,
                command=lambda f=folder_name: self.quick_move(f)
            )
            btn.pack(side="left", padx=5)

    def quick_move(self, folder_name):
        if not self.app.current_image_path:
            return

        target_dir = self.app.source_dir / folder_name
        target_dir.mkdir(exist_ok=True)

        # move using your routing layer
        move_result = self.app.router.move(
            self.app.current_image_path,
            target_dir,
            on_collision="rename"
        )

        # update app state + undo + UI
        self.app.on_file_moved(move_result)