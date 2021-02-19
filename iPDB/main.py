from tkinter import *
import app_models
import app_views

def start_app():
    root = Tk()
    root.title("Integrated PDB DB")
    root.geometry("800x420")
    root.config(relief=SUNKEN)

    app_views.ListComponent(app_models.PdbDbInteraction().retrieve_pdb()) # load existing pdb structures
    app_views.MiddleButtonsComponent(root)

    app_views.SearchBarComponent(root)
    app_views.MenuBar(root)

    root.mainloop()


if __name__ == '__main__':
    start_app()
