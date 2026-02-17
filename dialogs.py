# dialogs.py
from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, simpledialog, messagebox
from typing import Optional


def pick_source_folder(root) -> Optional[Path]:
    """Ask user to select a folder. Returns Path or None if cancelled."""
    folder = filedialog.askdirectory(title="Select Photo Folder")
    if not folder:
        return None
    return Path(folder)


def show_no_media_error() -> None:
    messagebox.showerror("Error", "No supported media found in this folder.")


def confirm_sort_another_folder() -> bool:
    return messagebox.askyesno(
        "All files sorted",
        "All files have been sorted.\n\nWould you like to sort another folder?"
    )


def ask_new_folder_name(root) -> Optional[str]:
    name = simpledialog.askstring("New Folder", "Folder name:", parent=root)
    if not name:
        return None
    return name.strip() or None


def show_file_exists_error() -> None:
    messagebox.showerror("Error", "File already exists in target folder.")


def show_folder_exists_error() -> None:
    messagebox.showerror("Error", "Folder already exists.")


def show_move_failed_error(msg: str) -> None:
    messagebox.showerror("Error", f"Move failed:\n{msg}")

def confirm_delete(filename: str) -> bool:
    return messagebox.askyesno(
        "Delete Photo",
        f"Move '{filename}' to Trash?"
    )