import media_loader
from cleanup import cleanup_private_trash


def exit_app(app, *, destroy: bool = False):
    media_loader.stop_video(app)
    if hasattr(app, "source_dir"):
        cleanup_private_trash(app)

    if destroy:
        app.root.destroy()
    else:
        app.root.quit()
