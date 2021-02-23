from tkinter import *
import app_models
import confs
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter.messagebox import askokcancel
from shutil import copy
import os
from Bio.PDB import PDBList


class ListComponent(Frame):
    chosen_pdb = None
    """
    Create the file list component of the GUI.
    """

    def __init__(self, queryset, parent=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.grid(row=0, rowspan=6, column=0, columnspan=4, sticky=W+E+N+S)
        self.make_widgets(queryset)

    def identify_pdb(self, event):
        """
        Determine whether a PDB file in the list is selected by mouse cursor.
        """
        index = self.listbox.curselection()
        selection = self.listbox.get(index)

        pdb_id = int(selection.split("|")[0]) #acquire pdb id
        pdb = app_models.PdbDbInteraction().retrieve_pdb(pdb_id) # retrieve pbd from the database
        if pdb:
            pdb = pdb[0] # only display the title of the pdb entry in the main window data list.
            ListComponent.chosen_pdb = pdb

        DataDisplayComponent()

    def make_widgets(self, queryset):
        file_list= Listbox(self)
        scroll_bar= Scrollbar(self)
        file_list.config(yscrollcommand=scroll_bar.set, relief=SUNKEN, borderwidth=4, width=40, height=15)
        scroll_bar.config(command=file_list.yview)
        file_list.pack(side=LEFT, expand=YES, fill=BOTH)
        scroll_bar.pack(side=RIGHT, expand=YES, fill=BOTH)
        file_list.bind("<Double-Button-1>", self.identify_pdb)

        position_in_file_list = 0
        for query in queryset:
            file_list.insert(position_in_file_list, f"{query[0]}| {query[1]} | {query[2]}")
            position_in_file_list += 1
        self.listbox = file_list

        self.popup_menu = Menu()
        self.popup_menu.add_command(label="Edit", command=self.edit_selected_pdb)
        self.popup_menu.add_command(label="Delete", command=self.delete_selected_pdb)
        self.popup_menu.add_separator()
        self.popup_menu.add_command(label="Launch in Pymol", command=self.launch_pdb)
        file_list.bind("<Button-2>", self.popup)

    def _select_pdb(self):
        """
        helper method to indicate the selected PDB file in the file list.
        """
        index = self.listbox.curselection()
        selection = self.listbox.get(index)
        return selection

    def edit_selected_pdb(self):
        selection = ListComponent._select_pdb(self)
        pdb_id = int(selection.split("|")[0])
        pdb = app_models.PdbDbInteraction().retrieve_pdb(pdb_id)
        UpdatePDBFields(pdb)

    def delete_selected_pdb(self):
        selection = ListComponent._select_pdb(self)
        pdb_id = int(selection.split("|")[0])
        pdb_name = selection.split("|")[1].strip()
        ans = askokcancel("Verify delete", "Really delete?")
        if ans:
            app_models.PdbDbInteraction().delete_pdb(pdb_id)

            ListComponent(app_models.PdbDbInteraction().retrieve_pdb())
            file_path = os.path.join(confs.BASE_DIR, f'{pdb_name}.pdb')
            if file_path:
                os.remove(file_path)

    def launch_pdb(self):
        """
        Open the selected PDB file in Pymol for structure visualisation.
        """
        selection = ListComponent._select_pdb(self)
        pdb_name = selection.split("|")[1].strip()
        file_path = os.path.join(confs.BASE_DIR, f'{pdb_name}.pdb')
        command = f"open -a PyMOL {file_path}"
        os.system(command)

    def popup(self, event):
        if self.listbox.curselection():
            try:
                self.popup_menu.tk_popup(event.x_root, event.y_root, 0)
            finally:
                self.popup_menu.grab_release()


class MiddleButtonsComponent(Frame):
    def __init__(self, parent=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.grid(row=6, column=0, columnspan=4, sticky=W+E+N+S, pady=10)
        # self.config(relief=SUNKEN, borderwidth=2)
        self.make_widgets()

    def make_widgets(self):
        label_font = ("Helvetica", 16)
        add_pdb_button = Button(self, text="Add PDB")

        add_pdb_button.config(relief=RAISED, command=AddNewPDB, height=2, fg="#5900b3", font=label_font, width=15)
        add_pdb_button.pack(side=LEFT, expand=YES)

        refresh_button = Button(self, text="Refresh", height=2)
        # refresh_button.config(fg="black", font=('Helvetica', 12), relief=RAISED, command=None)
        refresh_button.config(relief=RAISED, command=self.refresh_list, height=2, fg="#5900b3", font=label_font, width=15)
        refresh_button.pack(side=LEFT, expand=YES)

    def refresh_list(self):
        ListComponent(app_models.PdbDbInteraction().retrieve_pdb())


class DataDisplayComponent(Frame):
    """
    Displaying the data for the chosen PDB file in GUI.
    """
    def __init__(self, parent=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        # self.config(relief=SUNKEN, borderwidth=2, width=200, height=10)
        self.chosen_pdb = ListComponent.chosen_pdb

        self.grid(row=0, rowspan=10, column=5, columnspan=8, sticky=W+E+N+S, padx=5)
        self.make_widgets()

    def make_widgets(self):
        label_font = ("Helvetica", 14)
        seq_font = ("Helvetica", 12)
        labels = confs.DISPLAY_LABELS
        for i, field_name in enumerate(labels):
            label = Label(self, text=field_name, font=label_font)

            label.grid(row=i, column=5, sticky=W, padx=5, pady=5)

        variable_list = [self.chosen_pdb[1], self.chosen_pdb[2], self.chosen_pdb[3],
                         self.chosen_pdb[4], self.chosen_pdb[5], self.chosen_pdb[6], self.chosen_pdb[7]]

        for i, value in enumerate(variable_list):
            position = 0
            label_value = Entry(self)

            label_value.insert(position, value)
            position += 1
            label_value.config(fg="blue", state="readonly", relief="flat", width=100, font=label_font)
            label_value.grid(row=i, column=8, sticky=E, padx=5, pady=5)

        seq = self.chosen_pdb[8]
        sbar = Scrollbar(self)
        seq_value = Text(self, width=50)
        sbar.config(command=seq_value.yview)
        seq_value.config(yscrollcommand=sbar.set, fg="blue", state="normal", relief="flat", font=seq_font, height=5)
        seq_value.insert(END, seq)
        seq_value.grid(row=7, rowspan=3, column=5, columnspan=6, sticky=N+W)


class SearchBarComponent(Frame):
    """
    Creating the search bar component of the GUI.
    """
    def __init__(self, parent=None, *args, **kwargs):
        Frame.__init__(self, parent, *args, **kwargs)
        self.grid(row=7, rowspan=3, column=0, columnspan=4, sticky=W+E+N+S)
        self.make_widgets()

    def make_widgets(self):
        label_font = ("Helvetica", 16)
        self.search_entry = Entry(self)
        self.search_entry.config(width=38)
        button1 = Button(self, text="Search", command=self.search, height=2, width=17, font=label_font, fg="#5900b3", relief=RAISED)
        button2 = Button(self, text="Clear", command=self.clear, height=2, width=17, font=label_font, fg="#5900b3", relief=RAISED)
        self.search_entry.pack(side=TOP, padx=4)
        button1.pack(side=LEFT, expand=YES)
        button2.pack(side=LEFT, expand=YES)

    def search(self):
        self.keywords = self.search_entry.get()
        queryset = app_models.PdbDbInteraction().search_pdb(self.keywords)
        ListComponent(queryset)

    def clear(self):
        self.search_entry.delete(0, "end")


class AddNewPDB(Toplevel):
    pdb_name = None
    protein_name=None
    species = None
    hi_res = None
    Rwork = None
    Rfree = None
    space_group = None
    sequence = None
    file_path_text = None

    def __init__(self, parent=None, *args, **kwargs):
        Toplevel.__init__(self, parent, *args, **kwargs)
        self.selected_file = None
        self.file_path_text = StringVar()
        self.title("Add a PDB")
        self.make_widgets()

    def make_widgets(self):
        label_font = ("Helvetica", 16)
        label_font2 = ("Helvetica", 14)
        left_frame = Frame(self)
        left_frame.config(relief=SUNKEN, borderwidth=2)
        left_frame.grid(row=0, rowspan=4, column=0, columnspan=2)

        fetch_pdb_by_id_label = Label(left_frame, text="Enter PDB ID", font=label_font)
        self.fetch_pdb_by_id_bar = Entry(left_frame, width=20)
        fetch_pdb_by_id_button = Button(left_frame, text="Fetch", command=self.fetch_pdb, font=label_font2, fg="#5900b3")
        fetch_pdb_by_id_label.pack(side=TOP, expand=YES)
        self.fetch_pdb_by_id_bar.pack(side=TOP, expand=YES)
        fetch_pdb_by_id_button.pack(side=TOP, expand=YES)

        middle_separator = Frame(self)
        middle_separator.grid(row=0, rowspan=4, column=2)
        middle_separator_label = Label(middle_separator, text="Or", font=label_font)
        middle_separator_label.pack(side=TOP, expand=YES)

        right_frame = Frame(self)
        right_frame.config(relief=SUNKEN, borderwidth=2)
        right_frame.grid(row=0, rowspan=4, column=3, columnspan=5)
        load_pdb_own_label = Label(right_frame, text="Load your own", font=label_font)

        load_pdb_own_browse_entry = Entry(right_frame, textvariable=self.file_path_text, width=30)
        load_pdb_own_browse_button = Button(right_frame, text="Browse", command=self.ask_file, font=label_font2, fg="#5900b3")
        load_pdb_own_button = Button(right_frame, text="Submit", command=self.submit_own_pdb, font=label_font2, fg="#5900b3")
        load_pdb_own_label.pack(side=TOP)
        load_pdb_own_browse_entry.pack(side=TOP)
        load_pdb_own_browse_button.pack(side=LEFT)
        load_pdb_own_button.pack(side=RIGHT)

    def ask_file(self):
        filepath = askopenfilename(filetypes=[("PDB", ".pdb")])
        self.file_path_text.set(filepath)

    def submit_own_pdb(self):
        if self.file_path_text:
            file_path_string = self.file_path_text.get()
            AddNewPDB.file_path_text = file_path_string

            AddNewPDB.pdb_name = os.path.basename(file_path_string)[:-4]
            AddNewPDBFields.fetch_or_own = 'own'
            AddNewPDBFields()

    def fetch_pdb(self):
        """
        Download the PDB file from PDB repository by the given PDB Accession code.
        """
        pdb_id = self.fetch_pdb_by_id_bar.get().lower()
        pdb_info = app_models.QueryPDBWebSite().retrieve_pdb_info(pdb_id)

        AddNewPDB.pdb_name = pdb_info[0]
        AddNewPDB.protein_name = pdb_info[2]
        AddNewPDB.species = pdb_info[3]
        AddNewPDB.hi_res = pdb_info[4]
        AddNewPDB.Rwork = pdb_info[5]
        AddNewPDB.Rfree = pdb_info[6]
        AddNewPDB.space_group = pdb_info[7]
        AddNewPDB.sequence = pdb_info[8]
        AddNewPDBFields.fetch_or_own = 'fetch'
        AddNewPDBFields()


class MenuBar(Menu):
    """
    Creating the menu on the top of the GUI window
    """
    def __init__(self, parent=None):
        Menu.__init__(self, parent)
        self.make_widgets(parent)

    def make_widgets(self, parent):
        top = Menu(parent)
        parent.config(menu=top)

        action_menu = Menu(parent)
        action_menu.add_command(label="Add PDB", command=AddNewPDB)
        action_menu.add_separator()
        action_menu.add_command(label="Set base directory", command=self.ask_directory)
        action_menu.add_separator()
        action_menu.add_command(label="Quit", command=parent.quit)
        top.add_cascade(label="Action", menu=action_menu, underline=0)

    def ask_directory(self):
        base_directory = askdirectory()
        confs.BASE_DIR = base_directory


class AddNewPDBFields(Toplevel):
    fetch_or_own = ""

    def __init__(self, parent=None, *args, **kwargs):
        Toplevel.__init__(self, parent, *args, **kwargs)
        self.id_value = IntVar()
        self.pdb_name_value = StringVar()
        self.protein_name_value = StringVar()
        self.species_value = StringVar()
        self.hi_res_value = DoubleVar()
        self.Rwork_value = DoubleVar()
        self.Rfree_value = DoubleVar()
        self.space_group_value = StringVar()
        self.sequence_value = StringVar()
        self.make_widgets()

    def make_widgets(self):
        label_font = ("Helvetica", 14)
        fields = confs.FIELD_VARIABLES
        for i, label_name, field_value in fields:
            label = Label(self, text=label_name)
            label.grid(row=i, column=0, sticky=W, padx=5, pady=5)
            field_entry = Entry(self, textvariable=eval(field_value))
            field_entry.grid(row=i, column=1, sticky=W, padx=5, pady=5)
        self.pdb_name_value.set(AddNewPDB.pdb_name)
        self.protein_name_value.set(AddNewPDB.protein_name)
        self.species_value.set(AddNewPDB.species)
        self.hi_res_value.set(AddNewPDB.hi_res)
        self.Rwork_value.set(AddNewPDB.Rwork)
        self.Rfree_value.set(AddNewPDB.Rfree)
        self.space_group_value.set(AddNewPDB.space_group)
        self.sequence_value.set(AddNewPDB.sequence)
        seq_label = Label(self, text="Sequence")
        seq_label.grid(row=7)
        seq_entry_field = Entry(self)
        seq_entry_field.config(borderwidth=2, relief=SUNKEN, textvariable=self.sequence_value)
        seq_entry_field.grid(row=8, column=0, columnspan=2)
        Button(self, text="Save", command=self.save_to_db, font=label_font).grid(row=10,column=0)
        Button(self, text="Cancel", command=self.destroy, font=label_font).grid(row=10,column=1)

    def save_to_db(self):
        if AddNewPDBFields.fetch_or_own == 'fetch':
            pdb_obj = PDBList()
            pdb_id = AddNewPDB.pdb_name
            fetched_filepath = pdb_obj.retrieve_pdb_file(pdb_id, pdir=confs.BASE_DIR, file_format="pdb")
            new_filename = f"{pdb_id}.pdb"
            os.rename(fetched_filepath, os.path.join(confs.BASE_DIR, new_filename))

        elif AddNewPDBFields.fetch_or_own == 'own':
            file_path_string = AddNewPDB.file_path_text
            copy(file_path_string, confs.BASE_DIR)

        pdb = app_models.CreatePDBfile(self.pdb_name_value.get(), self.protein_name_value.get(), self.species_value.get(), self.hi_res_value.get(),
                                       self.Rwork_value.get(), self.Rfree_value.get(), self.space_group_value.get(), self.sequence_value.get())

        app_models.PdbDbInteraction().save(pdb)
        self.destroy()


class UpdatePDBFields(Toplevel):
    def __init__(self, pdb, parent=None, *args, **kwargs):
        Toplevel.__init__(self, parent, *args, **kwargs)
        self.pdb=pdb[0]
        self.id_value = IntVar()
        self.pdb_name_value = StringVar()
        self.protein_name_value = StringVar()
        self.species_value = StringVar()
        self.hi_res_value = DoubleVar()
        self.Rwork_value = DoubleVar()
        self.Rfree_value = DoubleVar()
        self.space_group_value = StringVar()
        self.sequence_value = StringVar()
        self.make_widgets()

    def make_widgets(self):
        fields = confs.FIELD_VARIABLES

        for i, label_name, field_value in fields:
            label = Label(self, text=label_name)

            label.grid(row=i, column=0, sticky=W, padx=5, pady=5)

            field_entry = Entry(self, textvariable=eval(field_value))
            field_entry.grid(row=i, column=1, sticky=W, padx=5, pady=5)
        self.id_value.set(self.pdb[0])
        self.pdb_name_value.set(self.pdb[1])
        self.protein_name_value.set(self.pdb[2])
        self.species_value.set(self.pdb[3])
        self.hi_res_value.set(self.pdb[4])
        self.Rwork_value.set(self.pdb[5])
        self.Rfree_value.set(self.pdb[6])
        self.space_group_value.set(self.pdb[7])
        self.sequence_value.set(self.pdb[8])

        seq_label = Label(self, text="Sequence")
        seq_label.grid(row=7)
        seq_entry_field = Entry(self)
        seq_entry_field.config(borderwidth=2, relief=SUNKEN, textvariable=self.sequence_value)
        seq_entry_field.grid(row=8, rowspan=2, column=0, columnspan=2)
        Button(self, text="Save", command=self.save_to_db).grid(row=10,column=0)

    def save_to_db(self):
        pdb = app_models.CreatePDBfile(self.pdb_name_value.get(), self.protein_name_value.get(),
                                       self.species_value.get(), self.hi_res_value.get(),
                                       self.Rwork_value.get(), self.Rfree_value.get(), self.space_group_value.get(),
                                       self.sequence_value.get())
        pdb_id = int(self.id_value.get())

        app_models.PDB_db_interaction().update_pdb(pdb, pdb_id)
        print("updated")
        self.destroy()
