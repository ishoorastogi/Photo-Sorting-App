# quick_actions.py
import tkinter as tk
from pathlib import Path
import dialogs

class QuickActionsBar:
    def __init__(self, app, parent_frame):
        self.app = app
        self.frame = tk.Frame(parent_frame)
        self.frame.pack(fill="x", pady=5)

        # Default quick folders (can be made configurable later)
        # keys are labels shown on buttons, values are target folder names
        # use lower-case for both display and actual folder names
        self.quick_folders = {
            "misc": "misc",
            "gym": "gym",
            "buddy": "buddy",
            "travel": "travel",
        }

        self.build_buttons()

    def build_buttons(self):
        for i, (label, folder_name) in enumerate(self.quick_folders.items()):
            # show the numeric key mapping on the button (1-based)
            display = f"({i+1}) {label}"
            btn = tk.Button(
                self.frame,
                text=display,
                width=12,
                command=lambda f=folder_name: self.quick_move(f)
            )
            btn.pack(side="left", padx=5)

    def quick_move(self, folder_name):
        if not self.app.current_image_path:
            return
        # create target folder if missing, then delegate movement to the app
        target_dir = self.app.source_dir / folder_name

        # Delegate actual move and UI updates to the app (folder creation + routing/undo handled there)
        self.app.move_image(target_dir)

    def activate(self, index: int):
        """Trigger the quick action by index (0-based). Keybinds call this."""
        if index < 0:
            return

        try:
            folder_name = list(self.quick_folders.values())[index]
        except IndexError:
            return

        target_dir = self.app.source_dir / folder_name
        self.app.move_image(target_dir)

    def rename_action(self, index: int):
        """Prompt for a new name for the quick action at `index` (0-based).

        This updates the quick_folders mapping label only (the underlying folder
        stays the same) and rebuilds the buttons so the UI reflects the change.
        """
        if index < 0:
            return

        try:
            old_label, old_folder = list(self.quick_folders.items())[index]
        except IndexError:
            return

        # Ask user for new folder name
        new_name = dialogs.ask_new_folder_name(self.app.root)
        if not new_name:
            return

        new_name = new_name.strip().lower()
        if not new_name:
            return

        # If label already exists elsewhere, don't clobber another quick action
        if new_name in self.quick_folders and new_name != old_label:
            dialogs.show_folder_exists_error()
            return

        target_dir = self.app.source_dir / new_name
        try:
            if target_dir.exists():
                if not target_dir.is_dir():
                    dialogs.show_move_failed_error(f"Not a folder: {target_dir}")
                    return
            else:
                target_dir.mkdir()
        except Exception as e:
            dialogs.show_move_failed_error(str(e))
            return

        # Update in-memory mapping label only (keep existing folder target)
        items = list(self.quick_folders.items())
        items[index] = (new_name, new_name)
        # preserve order
        self.quick_folders = dict(items)

        # rebuild buttons
        for w in self.frame.winfo_children():
            w.destroy()
        self.build_buttons()
