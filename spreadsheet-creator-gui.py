import re
import os
import csv
import json

import tkinter
from tkinter import ttk, messagebox

import sv_ttk

import consts as c

LARGEFONT = ("Times New Roman", 35)

list_link_regex = re.compile(r"^https://rateyourmusic\.com/list/.+$")
release_link_regex = re.compile(r"^https://rateyourmusic\.com/release/.+$")
date_regex = re.compile(
    r"^(?:(?:0[13578]|1[02])/(?:0[1-9]|[12][0-9]|3[01])|"     # 31-day months
    r"(?:0[469]|11)/(?:0[1-9]|[12][0-9]|30)|"                 # 30-day months
    r"02/(?:0[1-9]|1[0-9]|2[0-8]))/\d{4}$|"                   # Feb 1–28
    r"^(?:02/29/(?:(?:(?:[02468][048]00)|"                    # Feb 29 leap years
    r"(?:[13579][26]00)|"
    r"(?:\d{2}(?:0[48]|[2468][048]|[13579][26])))))$"
)

class mainApp(tkinter.Tk):
    def __init__(self, *args, **kwargs):
        tkinter.Tk.__init__(self, *args, **kwargs)

        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for f in (MainMenu, CreateSheetPrompt, CreateSheet, EditSheet):
            frame = f(container, self)

            self.frames[f] = frame

            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(MainMenu)
    
    def show_frame(self, container):
        frame = self.frames[container]
        frame.tkraise()

class MainMenu(tkinter.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        ttk.Label(self, text="Main Menu", font=LARGEFONT).pack()
        ttk.Button(self, text="Create Sheet",
                    command=lambda : controller.show_frame(CreateSheetPrompt)).pack()
        ttk.Button(self, text="Edit Sheet",
                  command=lambda : controller.show_frame(EditSheet)).pack()
        ttk.Button(self, text="Quit",
                  command=lambda : quit()).pack()

class CreateSheetPrompt(tkinter.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        self.controller = controller

        ttk.Label(self, text="Create Sheet", font=LARGEFONT).grid(row=0, column=4, padx=10, pady=10)

        ttk.Label(self, text="Enter the name of your sheet: ").grid(row=1,column=1)
        ttk.Entry(self).grid(row=2, column=1)

        self.list_link_entry = tkinter.StringVar()
        ttk.Label(self, text="Enter URL to list on Rate Your Music: ").grid(row=4, column=1)
        ttk.Entry(self, textvariable=self.list_link_entry).grid(row=5, column=1)

        self.classical_prompt_choice = tkinter.IntVar()
        ttk.Label(self, text="Is this a classical music list?").grid(row=7, column=1)
        ttk.Radiobutton(
            self, 
            text="Yes", 
            variable=self.classical_prompt_choice, 
            value=1
        ).grid(
            row=8, 
            column=1
        )
        ttk.Radiobutton(
            self, 
            text="No", 
            variable=self.classical_prompt_choice, 
            value=2
        ).grid(
            row=9, 
            column=1
        )

        ttk.Button(self, text="Create Sheet", command=self.validateInput).grid(row=10, column=1)

        ttk.Button(
            self, 
            text="Back",
            command=lambda : controller.show_frame(MainMenu)
        ).grid(
            row=15, 
            column=3
        )

    def validateInput(self):
        link_value = self.list_link_entry.get()
        classical_sheet_choice = self.classical_prompt_choice.get()
        if self.isLinkValid(link_value) and classical_sheet_choice == 1:
            messagebox.showinfo(
                "Rate Your Music List Validated!",
                "Your Rate Your Music list link is VALID!"
            )
        elif self.isLinkValid(link_value) and classical_sheet_choice == 2:
            self.controller.show_frame(CreateSheet)
        elif self.isLinkValid(link_value) and classical_sheet_choice not in range(1, 3):
            messagebox.showerror(
                "ERROR", 
                "Please choose whether or not this is a classical list"
            )
        else:
            messagebox.showerror(
                "ERROR", 
                "Your Rate Your Music list link is INVALID!"
            )
    
    def isLinkValid(self, link):
        if list_link_regex.match(link):
            return True
        else:
            print("ERROR: Please enter a valid Rate Your Music link")
            return False

class CreateSheet(tkinter.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        # Loads in genre JSON data
        with open('genres.json', encoding='utf8') as file:
            self.json_data = json.load(file)

        # CreateSheet frame label
        ttk.Label(self, text="Create Sheet", font=LARGEFONT).grid(row=0, column=4, padx=10, pady=10)

        # Release artist label and entry
        ttk.Label(self, text="Enter name of release artist: ").grid(row=1, column=1)
        self.artist_entry = ttk.Entry(self).grid(row=1, column=2)

        # Release title label and entry
        ttk.Label(self, text="Enter title of release: ").grid(row=2, column=1)
        self.title_entry = ttk.Entry(self).grid(row=2, column=2)

        self.year_entry_var = tkinter.StringVar() # Initialize string variable for release year
        self.year_message = tkinter.StringVar() # Initialize string variable for year message
        # Release year label and entry
        ttk.Label(self, text="Enter year of release: ").grid(row=3, column=1)
        self.year_entry = ttk.Entry(
            self,
            textvariable=self.year_entry_var, 
            validate="focusout", 
            validatecommand=self.validateYear
        ).grid(
            row=3, 
            column=2
        )
        
        # Initialize message for reporting an invalid year entry
        self.year_invalid_message = tkinter.Message(
            self, 
            textvariable=self.year_message,
            fg="red"
        )

        # <genre>_tree Variables
        (
            self.blues_tree, 
            self.classical_tree, 
            self.country_tree, 
            self.electronic_tree,
            self.experimental_tree, 
            self.folk_tree, 
            self.hip_hop_tree, 
            self.industrial_tree,
            self.jazz_tree, 
            self.metal_tree, 
            self.pop_tree, 
            self.punk_tree, 
            self.r_and_b_tree, 
            self.reggae_tree, 
            self.regional_tree, 
            self.rock_tree, 
            self.soul_tree 
        ) = (ttk.Treeview(self) for _ in range(17))

        # <genre>_checked Variables
        (
            self.blues_checked,
            self.classical_checked,
            self.country_checked,
            self.electronic_checked,
            self.experimental_checked,
            self.folk_checked,
            self.hip_hop_checked,
            self.industrial_checked,
            self.jazz_checked,
            self.metal_checked,
            self.pop_checked,
            self.punk_checked,
            self.r_and_b_checked,
            self.reggae_checked,
            self.regional_checked,
            self.rock_checked,
            self.soul_checked
        ) = (tkinter.BooleanVar() for _ in range(17))

        self.added_trees = set() # For tracking the currently checked genres
        self.genre_families = list() # For tracking the genre(s) to be written to sheet

        # Genre Family Checkbuttons
        ttk.Label(self, text="Genre Families").grid(row=4, column=1)
        ttk.Checkbutton(
            self, 
            text=c.BLUES, 
            variable=self.blues_checked, 
            offvalue=False, 
            onvalue=True, 
            command=self.genreHandler
        ).grid(
            row=4,
            column=2
        )
        ttk.Checkbutton(
            self, 
            text=c.CLASSICAL, 
            variable=self.classical_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=4,
            column=3
        )
        ttk.Checkbutton(
            self,
            text=c.COUNTRY,
            variable=self.country_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=4,
            column=4
        )
        ttk.Checkbutton(
            self,
            text=c.ELECTRONIC,
            variable=self.electronic_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=4,
            column=5
        )
        ttk.Checkbutton(
            self,
            text=c.EXPERIMENTAL,
            variable=self.experimental_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=4,
            column=6
        )

        ttk.Checkbutton(
            self,
            text=c.FOLK,
            variable=self.folk_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=5,
            column=2
        )
        ttk.Checkbutton(
            self,
            text=c.HIP_HOP,
            variable=self.hip_hop_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=5,
            column=3
        )
        ttk.Checkbutton(
            self,
            text=c.INDUSTRIAL,
            variable=self.industrial_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=5,
            column=4
        )
        ttk.Checkbutton(
            self,
            text=c.JAZZ,
            variable=self.jazz_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=5,
            column=5
        )
        ttk.Checkbutton(
            self,
            text=c.METAL,
            variable=self.metal_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=5,
            column=6
        )
        
        ttk.Checkbutton(
            self,
            text=c.POP,
            variable=self.pop_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=6,
            column=2
        )
        ttk.Checkbutton(
            self,
            text=c.PUNK,
            variable=self.punk_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=6,
            column=3
        )
        ttk.Checkbutton(
            self,
            text=c.R_AND_B,
            variable=self.r_and_b_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=6,
            column=4
        )
        ttk.Checkbutton(
            self,
            text=c.REGGAE,
            variable=self.reggae_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=6,
            column=5
        )
        ttk.Checkbutton(
            self,
            text=c.REGIONAL,
            variable=self.regional_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=6,
            column=6
        )
        
        ttk.Checkbutton(
            self,
            text=c.ROCK,
            variable=self.rock_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=7,
            column=3
        )
        ttk.Checkbutton(
            self,
            text=c.SOUL,
            variable=self.soul_checked,
            offvalue=False,
            onvalue=True,
            command=self.genreHandler
        ).grid(
            row=7,
            column=5
        )

        # <format>_checked Variables
        (
            self.album_checked,
            self.ep_checked,
            self.split_checked,
            self.mixtape_checked,
            self.compilation_checked,
            self.collab_checked,
            self.live_checked,
            self.archival_checked,
            self.demo_checked,
            self.additional_release_checked
        ) = (tkinter.BooleanVar() for _ in range(10))

        self.added_formats = set() # For tracking currently checked formats
        self.formats = list() # For tracking the format(s) that will be written to sheet

        # Release Format Checkbuttons
        ttk.Label(self, text="Format(s) [check all that apply]").grid(row=8, column=1)
        ttk.Checkbutton(
            self, 
            text="Album", 
            variable=self.album_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=2
        )
        ttk.Checkbutton(
            self, 
            text="EP", 
            variable=self.ep_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=3
        )
        ttk.Checkbutton(
            self, 
            text="Split", 
            variable=self.split_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=4
        )
        ttk.Checkbutton(
            self, 
            text="Mixtape", 
            variable=self.mixtape_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=5
        )
        ttk.Checkbutton(
            self, 
            text="Compilation", 
            variable=self.compilation_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=6
        )
        ttk.Checkbutton(
            self, 
            text="Collab", 
            variable=self.collab_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=7
        )
        ttk.Checkbutton(
            self, 
            text="Live", 
            variable=self.live_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=8
        )
        ttk.Checkbutton(
            self, 
            text="Archival", 
            variable=self.archival_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=9
        )
        ttk.Checkbutton(
            self, 
            text="Demo", 
            variable=self.demo_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=10
        )
        ttk.Checkbutton(
            self, 
            text="Additional Release", 
            variable=self.additional_release_checked, 
            offvalue=False, 
            onvalue=True,
            command=self.formatHandler
        ).grid(
            row=8,
            column=11
        )

        self.url_entry_var = tkinter.StringVar()
        ttk.Label(self, text="Enter the Rate Your Music URL of the release").grid(row=9, column=1)
        ttk.Entry(
            self, 
            textvariable=self.url_entry_var, 
            validate="focusout", 
            validatecommand=self.isLinkValid
        ).grid(
            row=9, 
            column=2
        )

        self.url_message = tkinter.StringVar()
        self.url_invalid_message = tkinter.Message(
            self,
            textvariable=self.url_message,
            fg="red"
        )

    # Function to:
    #   - Create genre treeviews
    #   - Populate them with subgenres
    #   - Add genres to genre_families
    def genreHandler(self): 
        # Blues
        if self.blues_checked.get():
            if c.BLUES not in self.added_trees:
                self.genreTreeviewAdd(self.blues_tree, c.BLUES, 10, 2)
                self.added_trees.add(c.BLUES)
                self.genreFamilyAdd(c.BLUES)
        else:
            if c.BLUES in self.added_trees:
                self.genreTreeviewRemove(self.blues_tree)
                self.added_trees.remove(c.BLUES)
                self.genreFamilyRemove(c.BLUES)
        
        # Classical
        if self.classical_checked.get():
            if c.CLASSICAL not in self.added_trees:
                self.genreTreeviewAdd(self.classical_tree, c.CLASSICAL, 10, 3)
                self.added_trees.add(c.CLASSICAL)
                self.genreFamilyAdd(c.CLASSICAL)
        else:
            if c.CLASSICAL in self.added_trees:
                self.genreTreeviewRemove(self.classical_tree)
                self.added_trees.remove(c.CLASSICAL)
                self.genreFamilyRemove(c.CLASSICAL)

        # Country
        if self.country_checked.get():
            if c.COUNTRY not in self.added_trees:
                self.genreTreeviewAdd(self.country_tree, c.COUNTRY, 10, 4)
                self.added_trees.add(c.COUNTRY)
                self.genreFamilyAdd(c.COUNTRY)
        else:
            if c.COUNTRY in self.added_trees:
                self.genreTreeviewRemove(self.country_tree)
                self.added_trees.remove(c.COUNTRY)
                self.genreFamilyRemove(c.COUNTRY)

        # Electronic
        if self.electronic_checked.get():
            if c.ELECTRONIC not in self.added_trees:
                self.genreTreeviewAdd(self.electronic_tree, c.ELECTRONIC, 10, 5)
                self.added_trees.add(c.ELECTRONIC)
                self.genreFamilyAdd(c.ELECTRONIC)
        else:
            if c.ELECTRONIC in self.added_trees:
                self.genreTreeviewRemove(self.electronic_tree)
                self.added_trees.remove(c.ELECTRONIC)
                self.genreFamilyRemove(c.ELECTRONIC)
        
        # Experimental
        if self.experimental_checked.get():
            if c.EXPERIMENTAL not in self.added_trees:
                self.genreTreeviewAdd(self.experimental_tree, c.EXPERIMENTAL, 10, 6)
                self.added_trees.add(c.EXPERIMENTAL)
                self.genreFamilyAdd(c.EXPERIMENTAL)
        else:
            if c.EXPERIMENTAL in self.added_trees:
                self.genreTreeviewRemove(self.experimental_tree)
                self.added_trees.remove(c.EXPERIMENTAL)
                self.genreFamilyRemove(c.EXPERIMENTAL)

        # Folk
        if self.folk_checked.get():
            if c.FOLK not in self.added_trees:
                self.genreTreeviewAdd(self.folk_tree, c.FOLK, 11, 2)
                self.added_trees.add(c.FOLK)
                self.genreFamilyAdd(c.FOLK)
        else:
            if c.FOLK in self.added_trees:
                self.genreTreeviewRemove(self.folk_tree)
                self.added_trees.remove(c.FOLK)
                self.genreFamilyRemove(c.FOLK)
        
        # Hip-Hop
        if self.hip_hop_checked.get():
            if c.HIP_HOP not in self.added_trees:
                self.genreTreeviewAdd(self.hip_hop_tree, c.HIP_HOP, 11, 3)
                self.added_trees.add(c.HIP_HOP)
                self.genreFamilyAdd(c.HIP_HOP)
        else:
            if c.HIP_HOP in self.added_trees:
                self.genreTreeviewRemove(self.hip_hop_tree)
                self.added_trees.remove(c.HIP_HOP)
                self.genreFamilyRemove(c.HIP_HOP)
        
        # Industrial
        if self.industrial_checked.get():
            if c.INDUSTRIAL not in self.added_trees:
                self.genreTreeviewAdd(self.industrial_tree, c.INDUSTRIAL, 11, 4)
                self.added_trees.add(c.INDUSTRIAL)
                self.genreFamilyAdd(c.INDUSTRIAL)
        else:
            if c.INDUSTRIAL in self.added_trees:
                self.genreTreeviewRemove(self.industrial_tree)
                self.added_trees.remove(c.INDUSTRIAL)
                self.genreFamilyRemove(c.INDUSTRIAL)
        
        # Jazz
        if self.jazz_checked.get():
            if c.JAZZ not in self.added_trees:
                self.genreTreeviewAdd(self.jazz_tree, c.JAZZ, 11, 5)
                self.added_trees.add(c.JAZZ)
                self.genreFamilyAdd(c.JAZZ)
        else:
            if c.JAZZ in self.added_trees:
                self.genreTreeviewRemove(self.jazz_tree)
                self.added_trees.remove(c.JAZZ)
                self.genreFamilyRemove(c.JAZZ)

        # Metal
        if self.metal_checked.get():
            if c.METAL not in self.added_trees:
                self.genreTreeviewAdd(self.metal_tree, c.METAL, 11, 6)
                self.added_trees.add(c.METAL)
                self.genreFamilyAdd(c.METAL)
        else:
            if c.METAL in self.added_trees:
                self.genreTreeviewRemove(self.metal_tree)
                self.added_trees.remove(c.METAL)
                self.genreFamilyRemove(c.METAL)
        
        # Pop
        if self.pop_checked.get():
            if c.POP not in self.added_trees:
                self.genreTreeviewAdd(self.pop_tree, c.POP, 12, 2)
                self.added_trees.add(c.POP)
                self.genreFamilyAdd(c.POP)
        else:
            if c.POP in self.added_trees:
                self.genreTreeviewRemove(self.pop_tree)
                self.added_trees.remove(c.POP)
                self.genreFamilyRemove(c.POP)

        # Punk
        if self.punk_checked.get():
            if c.PUNK not in self.added_trees:
                self.genreTreeviewAdd(self.punk_tree, c.PUNK, 12, 3)
                self.added_trees.add(c.PUNK)
                self.genreFamilyAdd(c.PUNK)
        else:
            if c.PUNK in self.added_trees:
                self.genreTreeviewRemove(self.punk_tree)
                self.added_trees.remove(c.PUNK)
                self.genreFamilyRemove(c.PUNK)
        
        # R&B
        if self.r_and_b_checked.get():
            if c.R_AND_B not in self.added_trees:
                self.genreTreeviewAdd(self.r_and_b_tree, c.R_AND_B, 12, 4)
                self.added_trees.add(c.R_AND_B)
                self.genreFamilyAdd(c.R_AND_B)
        else:
            if c.R_AND_B in self.added_trees:
                self.genreTreeviewRemove(self.r_and_b_tree)
                self.added_trees.remove(c.R_AND_B)
                self.genreFamilyRemove(c.R_AND_B)
        
        # Reggae
        if self.reggae_checked.get():
            if c.REGGAE not in self.added_trees:
                self.genreTreeviewAdd(self.reggae_tree, c.REGGAE, 12, 5)
                self.added_trees.add(c.REGGAE)
                self.genreFamilyAdd(c.REGGAE)
        else:
            if c.REGGAE in self.added_trees:
                self.genreTreeviewRemove(self.reggae_tree)
                self.added_trees.remove(c.REGGAE)
                self.genreFamilyRemove(c.REGGAE)
        
        # Regional
        if self.regional_checked.get():
            if c.REGIONAL not in self.added_trees:
                self.genreTreeviewAdd(self.regional_tree, c.REGIONAL, 12, 6)
                self.added_trees.add(c.REGIONAL)
                self.genreFamilyAdd(c.REGIONAL)
        else:
            if c.REGIONAL in self.added_trees:
                self.genreTreeviewRemove(self.regional_tree)
                self.added_trees.remove(c.REGIONAL)
                self.genreFamilyRemove(c.REGIONAL)

        # Rock
        if self.rock_checked.get():
            if c.ROCK not in self.added_trees:
                self.genreTreeviewAdd(self.rock_tree, c.ROCK, 13, 3)
                self.added_trees.add(c.ROCK)
                self.genreFamilyAdd(c.ROCK)
        else:
            if c.ROCK in self.added_trees:
                self.genreTreeviewRemove(self.rock_tree)
                self.added_trees.remove(c.ROCK)
                self.genreFamilyRemove(c.ROCK)
        
        # Soul
        if self.soul_checked.get():
            if c.SOUL not in self.added_trees:
                self.genreTreeviewAdd(self.soul_tree, c.SOUL, 13, 5)
                self.added_trees.add(c.SOUL)
                self.genreFamilyAdd(c.SOUL)
        else:
            if c.SOUL in self.added_trees:
                self.genreTreeviewRemove(self.soul_tree)
                self.added_trees.remove(c.SOUL)
                self.genreFamilyRemove(c.SOUL)

    def genreTreeviewAdd(self, tree, genre, row_num, col_num):
        tree.insert("", tkinter.END, text=genre)
        self.genreTreeviewGenerator(
            tree,
            "",
            self.json_data[genre]
        )
        tree.grid(row=row_num, column=col_num)

    def genreTreeviewRemove(self, tree):
        if tree.winfo_ismapped():
            tree.delete(*tree.get_children())
            tree.grid_remove()

    def genreFamilyAdd(self, genre):
        if self.genre_families.count(genre) == 0:
            self.genre_families.append(genre)
        
    def genreFamilyRemove(self, genre):
        if self.genre_families.count(genre) > 0:
            self.genre_families.remove(genre)

    def formatHandler(self):
        # Album
        if self.album_checked.get():
            if c.ALBUM not in self.added_formats:
                self.formatAdd(c.ALBUM)
                self.added_formats.add(c.ALBUM)
        else:
            if c.ALBUM in self.added_formats:
                self.formatRemove(c.ALBUM)
                self.added_formats.remove(c.ALBUM)

        # EP
        if self.ep_checked.get():
            self.formatAdd(c.EP)
        else:
            self.formatRemove(c.EP)

        # Split
        if self.split_checked.get():
            self.formatAdd(c.SPLIT)
        else:
            self.formatRemove(c.SPLIT)

        # Mixtape
        if self.mixtape_checked.get():
            self.formatAdd(c.MIXTAPE)
        else:
            self.formatRemove(c.MIXTAPE)

        # Compilation
        if self.compilation_checked.get():
            self.formatAdd(c.COMPILATION)
        else:
            self.formatRemove(c.COMPILATION)
        
        # Collab
        if self.collab_checked.get():
            self.formatAdd(c.COLLAB)
        else:
            self.formatRemove(c.COLLAB)
        
        # Live
        if self.live_checked.get():
            self.formatAdd(c.LIVE)
        else:
            self.formatRemove(c.LIVE)
        
        # Archival
        if self.archival_checked.get():
            self.formatAdd(c.ARCHIVAL)
        else:
            self.formatRemove(c.ARCHIVAL)
        
        # Demo
        if self.demo_checked.get():
            self.formatAdd(c.DEMO)
        else:
            self.formatRemove(c.DEMO)

        # Additional Release
        if self.additional_release_checked.get():
            self.formatAdd(c.ADDITIONAL_RELEASE)
        else:
            self.formatRemove(c.ADDITIONAL_RELEASE)

    def formatAdd(self, format):
        if self.formats.count(format) == 0:
            self.formats.append(format)
    
    def formatRemove(self, format):
        if self.formats.count(format) > 0:
            self.formats.remove(format)

    def genreTreeviewGenerator(self, tree, parent, genre_list):
        for genre in genre_list:
            if "simplified-name" in genre:
                id = tree.insert(
                    parent, 
                    tkinter.END, 
                    text=genre["simplified-name"]
                )
            else:
                id = tree.insert(
                    parent, 
                    tkinter.END, 
                    text=genre["name"]
                )
            
            if "subgenres" in genre and genre["subgenres"]:
                self.genreTreeviewGenerator(
                    tree, 
                    id, 
                    genre["subgenres"]
                )

    def validateYear(self):
        year = self.year_entry_var.get().strip()

        # handle if input is blank
        if year == "":
            self.year_message.set("")
            return True

        try:
            year = int(year)
            self.year_message.set("")
            if self.year_invalid_message.winfo_ismapped():
                self.year_invalid_message.grid_remove()
        except:
            self.year_message.set("ERROR: Please enter a valid integer for the year")
            self.year_invalid_message.grid(row=3, column=3)
        finally:
            # return True because a failure thrown in except permanently stops validation
            return True

    def isLinkValid(self):
        link = self.url_entry_var.get().strip()

        if link == "":
            self.url_message.set("")
            return True
        
        if release_link_regex.match(link):
            self.url_message.set("")
            if self.url_invalid_message.winfo_ismapped():
                self.url_invalid_message.grid_remove()
        else:
            self.url_message.set("ERROR: Please enter a valid Rate Your Music URL for this release")
            self.url_invalid_message.grid(row=9, column=3)
            return False

        return True


class EditSheet(tkinter.Frame):
    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)

        ttk.Label(
            self, 
            text="Coming Soon!", 
            font=LARGEFONT
        ).grid(
            row=0, 
            column=4, 
            padx=10, 
            pady=10)
        
        ttk.Button(
            self, 
            text="Back",
            command=lambda : controller.show_frame(MainMenu)
        ).grid(
            row=15, 
            column=3
        )





app = mainApp()
app.geometry("1500x750")
sv_ttk.set_theme("dark")
app.mainloop()
