import tkinter as tk
from pathlib import Path

from keybinds import bind_keyboard_shortcuts
from ui import build_ui
from undo import UndoManager
from file_routing import FileRouter
import media_loader
import dialogs
from exit import exit_app


###
#
# make it executable from outside unix
#state manager
#file ops layer
#session completion handler
#dialogs
###

class PhotoSorterApp:
    def is_video(self, path: Path):
        return path.suffix.lower() in (".mp4", ".mov")
    
    def __init__(self, root):
        self.undo = UndoManager()
        self.root = root
        self.root.title("Photo Sorter")

        self.video_cap = None
        self.video_playing = False
        self.show_videos = True

        self.images = []
        self.index = 0
        self.current_image_path = None
        self.tk_image = None
        self._pending_skip_end = False

        build_ui(self)
        bind_keyboard_shortcuts(self)
        self.select_source_folder()

        self._action_lock = False

    def select_source_folder(self):
        folder = dialogs.pick_source_folder(self.root)
        self.refocus_app()

        if not folder:
            exit_app(self)
            return

        media_loader.stop_video(self)
        if hasattr(self, "video_overlay"):
            self.video_overlay.place_forget()

        self.source_dir = Path(folder)

        self.router = FileRouter(self.source_dir)

        self.undo.clear()
        self.images = self.router.list_media()
        self.index = 0
        self.current_image_path = None
        self.tk_image = None

        if not self.images:
            choose_again = dialogs.confirm_pick_another_folder()
            if choose_again:
                self.select_source_folder()
            else:
                exit_app(self)
            return

        self.image_label.config(image="", text="")

        self.refresh_folder_buttons()
        self.load_image()

    def set_show_videos(self, show: bool):
        show = bool(show)
        if self.show_videos == show:
            return

        self.show_videos = show
        if hasattr(self, "_show_videos_var"):
            self._show_videos_var.set(self.show_videos)
        media_loader.stop_video(self)
        if hasattr(self, "video_overlay"):
            self.video_overlay.place_forget()

        if not hasattr(self, "router"):
            return

        self.load_image()

    def skip_current(self):
        if self.current_image_path is None:
            return
        self.refocus_app()
        media_loader.stop_video(self)
        self._pending_skip_end = True
        self.index += 1
        self.load_image()

    def restart_review_skipped(self):
        media_loader.stop_video(self)
        if hasattr(self, "video_overlay"):
            self.video_overlay.place_forget()
        if not hasattr(self, "router"):
            return
        self.images = self.router.list_media()
        self.index = 0
        self.current_image_path = None
        self.load_image()

    def restart_with_videos(self):
        self.show_videos = True
        if hasattr(self, "_show_videos_var"):
            self._show_videos_var.set(True)
        media_loader.stop_video(self)
        if hasattr(self, "video_overlay"):
            self.video_overlay.place_forget()
        if not hasattr(self, "router"):
            return
        self.images = self.router.list_media()
        self.index = 0
        self.current_image_path = None
        self.load_image()

    def _advance_past_videos(self):
        if self.show_videos:
            return
        while self.index < len(self.images) and self.is_video(self.images[self.index]):
            self.index += 1

    def _completion_dialog_text(self):
        default_title = "All files sorted"
        default_message = "All files have been sorted.\n\nWould you like to sort another folder?"

        if self.show_videos or not hasattr(self, "router"):
            return default_title, default_message

        remaining = self.router.list_media()
        remaining_videos = any(self.is_video(p) for p in remaining)
        if remaining_videos:
            title = "All photos sorted, videos may remain"
            message = "All photos sorted, videos may remain.\n\nWould you like to sort another folder?"
            return title, message

        return default_title, default_message

   
    def load_image(self):
        self._advance_past_videos()
        if self.index >= len(self.images):
            pending_skip = self._pending_skip_end
            self._pending_skip_end = False

            if pending_skip:
                has_supported = hasattr(self, "router") and bool(self.router.list_media())
                if has_supported:
                    choice = dialogs.choose_after_skips(self.root)
                    if choice == "review_skipped":
                        self.restart_review_skipped()
                    elif choice == "another":
                        from cleanup import cleanup_private_trash
                        cleanup_private_trash(self)
                        self.undo.clear()
                        self.images = []
                        self.index = 0
                        self.current_image_path = None

                        # Clear UI
                        self.image_label.config(image="", text="")
                        if hasattr(self, "video_overlay"):
                            self.video_overlay.place_forget()

                        # Ask for new folder
                        self.select_source_folder()
                    else:
                        exit_app(self)
                else:
                    again = dialogs.confirm_sort_another_folder()
                    if again:
                        from cleanup import cleanup_private_trash
                        cleanup_private_trash(self)
                        self.undo.clear()
                        self.images = []
                        self.index = 0
                        self.current_image_path = None

                        # Clear UI
                        self.image_label.config(image="", text="")
                        if hasattr(self, "video_overlay"):
                            self.video_overlay.place_forget()

                        # Ask for new folder
                        self.select_source_folder()
                    else:
                        exit_app(self)
            else:
                title, message = self._completion_dialog_text()
                if title == "All photos sorted, videos may remain":
                    choice = dialogs.choose_after_photos_sorted(self.root)
                    if choice == "another":
                        from cleanup import cleanup_private_trash
                        cleanup_private_trash(self)
                        self.undo.clear()
                        self.images = []
                        self.index = 0
                        self.current_image_path = None

                        # Clear UI
                        self.image_label.config(image="", text="")
                        if hasattr(self, "video_overlay"):
                            self.video_overlay.place_forget()

                        # Ask for new folder
                        self.select_source_folder()
                    elif choice == "review_videos":
                        self.restart_with_videos()
                    else:
                        exit_app(self)
                else:
                    again = dialogs.confirm_sort_another_folder(title, message)

                    if again:
                        from cleanup import cleanup_private_trash
                        cleanup_private_trash(self)
                        self.undo.clear()
                        self.images = []
                        self.index = 0
                        self.current_image_path = None

                        # Clear UI
                        self.image_label.config(image="", text="")
                        if hasattr(self, "video_overlay"):
                            self.video_overlay.place_forget()

                        # Ask for new folder
                        self.select_source_folder()
                    else:
                        exit_app(self)

            return
        self._pending_skip_end = False


        self.current_image_path = self.images[self.index]

        try:
            if self.is_video(self.current_image_path):
                media_loader.render_video_paused(self, self.current_image_path)
            else:
                media_loader.render_image(self, self.current_image_path)
        except Exception as e:
            print("MEDIA LOAD ERROR:", e)
            self.image_label.config(
                image="",
                text=f"Could not load file:\n{self.current_image_path.name}"
            )


    def refresh_folder_buttons(self):
        for widget in self.folder_frame.winfo_children():
            widget.destroy()

        for folder in self.router.list_target_folders():
            if folder == self.source_dir:
                continue

            btn = tk.Button(
                self.folder_frame,
                # show folder names in lower-case to match quick-actions behavior
                text=folder.name.lower(),
                width=25,
                command=lambda f=folder: self.move_image(f)
            )
            btn.pack(pady=2)

    def move_image(self, target_folder):
        self.refocus_app()
        media_loader.stop_video(self)
        # ensure the target folder exists (created by app logic, not the UI layer)
        try:
            target_folder.mkdir(exist_ok=True)

            result = self.router.move(self.current_image_path, target_folder, on_collision="error")
        except FileExistsError:
            dialogs.show_file_exists_error()
            return
        except Exception as e:
            # optional: add this dialog helper if you want
            dialogs.show_move_failed_error(str(e))
            return

        self.undo.push_move(moved_to=result.dst, restore_to=result.src)
        # refresh folder list (so newly created folders appear in the UI)
        self.refresh_folder_buttons()

        self.index += 1
        self.load_image()

    def create_new_folder(self):
        name = dialogs.ask_new_folder_name(self.root)
        
        self.refocus_app()
        
        if not name:
            return

        new_folder = self.source_dir / name
        try:
            new_folder.mkdir()
            self.refresh_folder_buttons()
        except FileExistsError:
            dialogs.show_folder_exists_error()

    def undo_last_action(self):
        if not self._try_lock():
            return

        try:
            media_loader.stop_video(self)

            action = self.undo.undo()
            if action is None:
                return

            self.undo.apply(action)

            try:
                self.index = self.images.index(action.dst)
            except ValueError:
                self.index = max(self.index - 1, 0)
            self.load_image()

        finally:
            self.root.after(80, self._unlock)

    def _try_lock(self):
        if self._action_lock:
            return False
        self._action_lock = True
        return True

    def _unlock(self):
        self._action_lock = False
    
    def refocus_app(self):
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(10, lambda: self.root.attributes("-topmost", False))
        self.root.focus_force()

    def rename_target_folder(self, old_name: str, new_name: str) -> bool:
        """Rename a target folder under source_dir from old_name to new_name.

        Returns True on success, False on failure (e.g., destination exists).
        """
        old_name = (old_name or "").strip().lower()
        new_name = (new_name or "").strip().lower()

        if not new_name:
            return False

        src = self.source_dir / old_name
        dst = self.source_dir / new_name

        # Nothing to do
        if old_name == new_name:
            # ensure dst exists
            dst.mkdir(exist_ok=True)
            self.refresh_folder_buttons()
            return True

        # If destination already exists, signal failure
        if dst.exists():
            dialogs.show_folder_exists_error()
            return False

        try:
            if src.exists():
                src.rename(dst)
            else:
                # if original folder missing, just create destination
                dst.mkdir(exist_ok=True)
        except Exception as e:
            dialogs.show_move_failed_error(str(e))
            return False

        # Refresh UI folder list
        self.refresh_folder_buttons()
        return True

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoSorterApp(root)

    def on_close():
        exit_app(app, destroy=True)
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()
