import tkinter as tk


def build_state_controls(app, parent_frame):
    if not hasattr(app, "show_videos"):
        app.show_videos = True

    app._show_videos_var = tk.BooleanVar(value=app.show_videos)

    def _on_toggle():
        app.set_show_videos(app._show_videos_var.get())

    app.videos_toggle = tk.Checkbutton(
        parent_frame,
        text="videos",
        variable=app._show_videos_var,
        command=_on_toggle
    )
    return app.videos_toggle
