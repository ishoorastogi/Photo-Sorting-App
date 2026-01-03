## gui
import tkinter as tk
from deletion import delete_current_image


def _is_descendant(widget, ancestor):
    """Return True if widget is ancestor or inside ancestor."""
    w = widget
    while w is not None:
        if w == ancestor:
            return True
        w = w.master
    return False


def _install_folder_scrolling(app):
    root = app.root
    canvas = app.folder_canvas

    def _units_from_delta(delta):
        # Windows wheel: +/-120 per notch
        # macOS trackpad: small deltas (often +/-1..10)
        if delta == 0:
            return 0
        if abs(delta) < 120:
            return -1 if delta > 0 else 1
        return int(-delta / 120)

    def _on_mousewheel(event):
        # Which widget is the mouse currently over?
        widget = root.winfo_containing(
            root.winfo_pointerx(),
            root.winfo_pointery()
        )

        # Only scroll if mouse is over folder list (buttons included)
        if widget and _is_descendant(widget, canvas):
            units = _units_from_delta(getattr(event, "delta", 0))
            if units:
                canvas.yview_scroll(units, "units")
                return "break"

    def _on_linux_up(event):
        widget = root.winfo_containing(
            root.winfo_pointerx(),
            root.winfo_pointery()
        )
        if widget and _is_descendant(widget, canvas):
            canvas.yview_scroll(-3, "units")
            return "break"

    def _on_linux_down(event):
        widget = root.winfo_containing(
            root.winfo_pointerx(),
            root.winfo_pointery()
        )
        if widget and _is_descendant(widget, canvas):
            canvas.yview_scroll(3, "units")
            return "break"

    # Global binds (required so buttons receive scroll)
    root.bind_all("<MouseWheel>", _on_mousewheel)   # macOS / Windows
    root.bind_all("<Button-4>", _on_linux_up)       # Linux
    root.bind_all("<Button-5>", _on_linux_down)     # Linux


def build_ui(app):
    root = app.root
    

    # Main content frame
    app.content_frame = tk.Frame(root)
    app.content_frame.pack(side="top", fill="both", expand=True)

    # Image display frame
    app.image_frame = tk.Frame(app.content_frame, height=500)
    app.image_frame.pack(side="top", fill="x")
    app.image_frame.pack_propagate(False)

    # Image label
    app.image_label = tk.Label(app.image_frame)
    app.image_label.pack(expand=True)

    # Video overlay
    app.video_overlay = tk.Label(
        app.image_frame,
        text="▶",
        font=("Helvetica", 64, "bold"),
        fg="white",
        bg="black"
    )
    app.video_overlay.place_forget()

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

    # Update scroll region when folders change
    app.folder_frame.bind(
        "<Configure>",
        lambda e: app.folder_canvas.configure(
            scrollregion=app.folder_canvas.bbox("all")
        )
    )

    # ✅ INSTALL ROBUST SCROLLING
    _install_folder_scrolling(app)

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
