import cv2
from PIL import Image, ImageTk


def stop_video(app):
    app.video_playing = False

    if app.video_cap is not None:
        app.video_cap.release()
        app.video_cap = None


def load_image(app, path):
    stop_video(app)
    app.video_overlay.place_forget()

    img = Image.open(path)
    img.thumbnail((900, 700))

    app.tk_image = ImageTk.PhotoImage(img)
    app.image_label.config(image=app.tk_image, text="")
    app.image_label.pack(expand=True)


def load_video_paused(app, path):
    stop_video(app)

    app.video_cap = cv2.VideoCapture(str(path))
    if not app.video_cap.isOpened():
        raise RuntimeError("Could not open video")

    success, frame = app.video_cap.read()
    if not success:
        raise RuntimeError("Could not read first frame")

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img.thumbnail((900, 700))

    app.tk_image = ImageTk.PhotoImage(img)
    app.image_label.config(image=app.tk_image, text="")
    app.image_label.pack(expand=True)

    app.video_playing = False
    app.video_overlay.place(relx=0.5, rely=0.5, anchor="center")


def play_next_frame(app):
    if not app.video_playing or app.video_cap is None:
        return

    success, frame = app.video_cap.read()

    if not success:
        app.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, frame = app.video_cap.read()
        if not success:
            stop_video(app)
            return

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    img.thumbnail((900, 700))

    app.tk_image = ImageTk.PhotoImage(img)
    app.image_label.config(image=app.tk_image)
    app.image_label.pack(expand=True)

    app.root.after(33, lambda: play_next_frame(app))


def toggle_video(app):
    if app.video_cap is None:
        return

    if app.video_playing:
        app.video_playing = False
        app.video_overlay.place(relx=0.5, rely=0.5, anchor="center")
    else:
        app.video_playing = True
        app.video_overlay.place_forget()
        play_next_frame(app)
