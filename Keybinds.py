## Keybinds
from deletion import delete_current_image

def bind_keyboard_shortcuts(app):
        root = app.root
        
        #Delete + backspace delete photos
        root.bind("<Delete>", lambda e: delete_current_image(app))
        root.bind("<BackSpace>", lambda e: delete_current_image(app))
        
        #Tab makes new folder
        root.bind("<Tab>", lambda e: app.create_new_folder())