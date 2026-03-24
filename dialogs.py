# dialogs.py
from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, simpledialog, messagebox
import tkinter as tk
from typing import Optional


def pick_source_folder(root) -> Optional[Path]:
    """Ask user to select a folder. Returns Path or None if cancelled."""
    folder = filedialog.askdirectory(title="Select Photo Folder")
    if not folder:
        return None
    return Path(folder)


def show_no_media_error() -> None:
    messagebox.showerror("Error", "No supported media found in this folder.")

def confirm_pick_another_folder() -> bool:
    return messagebox.askyesno(
        "No Supported Media",
        "No supported media found in this folder.\n\nWould you like to choose another folder?"
    )


def confirm_sort_another_folder(title: str = "All files sorted", message: str | None = None) -> bool:
    if message is None:
        message = "All files have been sorted.\n\nWould you like to sort another folder?"
    return messagebox.askyesno(title, message)

def choose_after_photos_sorted(root) -> str:
    """Return one of: 'another', 'review_videos', 'exit'."""
    result = {"value": "exit"}

    dialog = tk.Toplevel(root)
    dialog.title("All photos sorted, videos may remain")
    dialog.transient(root)
    dialog.grab_set()

    msg = "All photos sorted, videos may remain.\n\nWhat would you like to do?"
    tk.Label(dialog, text=msg, justify="left").pack(padx=20, pady=(15, 10))

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(padx=20, pady=(0, 15))

    def _set(val: str):
        result["value"] = val
        dialog.destroy()

    tk.Button(
        btn_frame,
        text="Sort Another Folder",
        width=26,
        command=lambda: _set("another")
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text="Review Videos",
        width=26,
        command=lambda: _set("review_videos")
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text="Exit App",
        width=26,
        command=lambda: _set("exit")
    ).pack(fill="x", pady=2)

    dialog.protocol("WM_DELETE_WINDOW", lambda: _set("exit"))
    root.wait_window(dialog)
    return result["value"]

def choose_after_skips(root) -> str:
    """Return one of: 'review_skipped', 'another', 'exit'."""
    result = {"value": "exit"}

    dialog = tk.Toplevel(root)
    dialog.title("End of Folder")
    dialog.transient(root)
    dialog.grab_set()

    msg = "You reached the end of the folder.\n\nWhat would you like to do?"
    tk.Label(dialog, text=msg, justify="left").pack(padx=20, pady=(15, 10))

    btn_frame = tk.Frame(dialog)
    btn_frame.pack(padx=20, pady=(0, 15))

    def _set(val: str):
        result["value"] = val
        dialog.destroy()

    tk.Button(
        btn_frame,
        text="Review Skipped",
        width=26,
        command=lambda: _set("review_skipped")
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text="Sort Another Folder",
        width=26,
        command=lambda: _set("another")
    ).pack(fill="x", pady=2)

    tk.Button(
        btn_frame,
        text="Exit App",
        width=26,
        command=lambda: _set("exit")
    ).pack(fill="x", pady=2)

    dialog.protocol("WM_DELETE_WINDOW", lambda: _set("exit"))
    root.wait_window(dialog)
    return result["value"]


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
