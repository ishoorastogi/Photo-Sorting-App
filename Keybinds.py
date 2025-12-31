## Keybinds

def bind_keyboard_shortcuts(app):
        root = app.root
        
        #Delete + backspace delete photos
        root.bind("<Delete>", lambda e: app.delete_image())
        root.bind("<BackSpace>", lambda e: app.delete_image())
        
        #Tab makes new folder
        root.bind("<Tab>", lambda e: app.create_new_folder())