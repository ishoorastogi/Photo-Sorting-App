##gui

import tkinter as tk
from deletion import delete_current_image

def build_ui(app):
    root = app.root

    # Main content frame
    app.content_frame = tk.Frame(root)
    app.content_frame.pack(side="top", fill="both", expand=True)

    # Image display frame
    app.image_frame = tk.Frame(app.content_frame, height=500)
    app.image_frame.pack(side="top", fill="x")
    app.image_frame.pack_propagate(False)

    app.image_label = tk.Label(app.image_frame)
    app.image_label.pack(expand=True)

    # Scroll container for folders
    app.folder_canvas = tk.Canvas(app.content_frame, height=220)
    app.folder_scrollbar = tk.Scrollbar(
        app.content_frame,
        orient="vertical",
        command=app.folder_canvas.yview
    )

    app.folder_canvas.configure(
        yscrollcommand=app.folder_scrollbar.set
    )

    app.folder_scrollbar.pack(side="right", fill="y")
    app.folder_canvas.pack(side="left", fill="x", padx=10)

    app.folder_frame = tk.Frame(app.folder_canvas)
    app.folder_canvas.create_window(
        (0, 0),
        window=app.folder_frame,
        anchor="nw"
    )

    # Enable scrolling
    app.folder_frame.bind(
        "<Configure>",
        lambda e: app.folder_canvas.configure(
            scrollregion=app.folder_canvas.bbox("all")
        )
    )

    # Bottom action bar
    app.action_frame = tk.Frame(root)
    app.action_frame.pack(side="bottom", fill="x", pady=10)

    app.new_folder_btn = tk.Button(
        app.action_frame,
        text="➕ New Folder",
        command=app.create_new_folder
    )
    app.new_folder_btn.pack(side="left", padx=10)

    app.undo_btn = tk.Button(
        app.action_frame,
        text="↩ Undo",
        command=app.undo_last_action
    )
    app.undo_btn.pack(side="left", padx=10)

    app.delete_btn = tk.Button(
        app.action_frame,
        text="🗑 Delete Photo",
        fg="red",
        command=lambda: delete_current_image(app)
    )
    app.delete_btn.pack(side="right", padx=10)
