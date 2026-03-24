## gui
import tkinter as tk
from deletion import delete_current_image
from quick_actions import QuickActionsBar
from state import build_state_controls
from exit import exit_app


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

    # Track a precise scroll position (0.0 → 1.0)
    app._scroll_pos = 0.0

    def _on_mousewheel(event):
        widget = root.winfo_containing(
            root.winfo_pointerx(),
            root.winfo_pointery()
        )

        if not widget or not _is_descendant(widget, canvas):
            return

        delta = getattr(event, "delta", 0)
        if delta == 0:
            return

        # Normalize delta (macOS trackpad safe)
        step = -delta / 100.0   # smaller = slower, smoother

        # Update position
        app._scroll_pos += step

        # Clamp to valid range
        app._scroll_pos = max(0.0, min(1.0, app._scroll_pos))

        canvas.yview_moveto(app._scroll_pos)
        return "break"

    def _on_linux_up(event):
        widget = root.winfo_containing(
            root.winfo_pointerx(),
            root.winfo_pointery()
        )
        if widget and _is_descendant(widget, canvas):
            app._scroll_pos = max(0.0, app._scroll_pos - 0.05)
            canvas.yview_moveto(app._scroll_pos)
            return "break"

    def _on_linux_down(event):
        widget = root.winfo_containing(
            root.winfo_pointerx(),
            root.winfo_pointery()
        )
        if widget and _is_descendant(widget, canvas):
            app._scroll_pos = min(1.0, app._scroll_pos + 0.05)
            canvas.yview_moveto(app._scroll_pos)
            return "break"

    # Global binds (required so buttons receive scroll)
    root.bind_all("<MouseWheel>", _on_mousewheel)   # macOS / Windows
    root.bind_all("<Button-4>", _on_linux_up)       # Linux
    root.bind_all("<Button-5>", _on_linux_down)     # Linux

def build_ui(app):
    root = app.root
    app._scroll_after_id = None

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
    app.quick_actions = QuickActionsBar(app, root)
    app.action_frame = tk.Frame(root)
    app.action_frame.pack(side="bottom", fill="x", pady=10)
    app.action_frame.pack_propagate(False)

    videos_toggle = build_state_controls(app, app.action_frame)

    app.new_folder_btn = tk.Button(
        app.action_frame,
        text="➕ New Folder",
        command=app.create_new_folder
    )

    app.skip_btn = tk.Button(
        app.action_frame,
        text="Skip",
        command=app.skip_current
    )

    app.undo_btn = tk.Button(
        app.action_frame,
        text="↩ Undo",
        command=app.undo_last_action
    )

    app.delete_btn = tk.Button(
        app.action_frame,
        text="🗑 Delete Photo",
        fg="red",
        command=lambda: delete_current_image(app)
    )

    app.exit_btn = tk.Button(
        app.action_frame,
        text="Exit",
        command=lambda: exit_app(app)
    )
    app._action_buttons = [
        videos_toggle,
        app.new_folder_btn,
        app.skip_btn,
        app.undo_btn,
        app.exit_btn,
        app.delete_btn,
    ]

    def _layout_action_buttons(event=None):
        buttons = app._action_buttons
        if not buttons:
            return

        frame = app.action_frame
        frame.update_idletasks()
        available = frame.winfo_width()
        if available <= 1:
            return

        gap = 10
        max_w = max(b.winfo_reqwidth() for b in buttons)
        max_h = max(b.winfo_reqheight() for b in buttons)
        min_w = max(1, max_w // 2)

        cols = max(1, (available + gap) // (min_w + gap))
        cols = min(cols, len(buttons))
        width = min(max_w, max(min_w, int((available - gap * (cols - 1)) / cols)))
        width = min(width, available)

        for i, btn in enumerate(buttons):
            row = i // cols
            col = i % cols
            x = col * (width + gap)
            y = row * (max_h + gap)
            btn.place(x=x, y=y, width=width, height=max_h)

        rows = (len(buttons) + cols - 1) // cols
        frame.configure(height=rows * max_h + gap * (rows - 1))

    app.action_frame.bind("<Configure>", _layout_action_buttons)
    app.root.after(0, _layout_action_buttons)
