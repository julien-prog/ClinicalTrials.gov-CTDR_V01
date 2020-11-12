"""
Program made in mid-2020
            -----------------------------------------------------------------------------------------
            Download trials from ClinicalTrials.gov database and store selected data into a CSV file
            -----------------------------------------------------------------------------------------

The code is written using a system of frames, each frames has the same shape and size and are generated
in the init method ; the user have to select the page to raise up the corresponding frame. 
Each Frame is a different object linked by the main object interface through the controller method
Syntax for each frame:
    1st order frame : 
                    LabelFrame(self.NW02, text='Automatically from the web', labelanchor=N, bg='white',
                                         relief='sunken', font=('helvetica', 13, 'bold')).pack(fill='both', padx=10, 
                                         pady=4, anchor=NW, side='left')
    2nd order frame: 
                    LabelFrame(NorthWestFrame, text=' Select New XML Schema', relief="raise",
                               font=('helvetica', 14, 'bold'), labelanchor=NW, bg='white').pack(fill='x', padx=10, 
                               pady=10, anchor=NW)
    3rd order frame: 
                    LabelFrame(self, text='Select XML Schema', relief="solid", font=('helvetica', 16, 'bold')
                                    , labelanchor=N, bg='white').pack(side=TOP, fill='x', padx=5, pady=4, anchor=NW)
"""
import csv
import os
import sqlite3
import time
import tkinter as tk
import urllib.error as error
import urllib.request as R
import xml.etree.ElementTree as ET
from datetime import date
from io import BytesIO
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from zipfile import ZipFile, is_zipfile
from PIL import ImageTk, Image
from Parse_Model_Code import get_major_titles, parse_model, take_name, main_search_v01, number_of_lines, \
    write_all_rows_v01, single_row, realign_all_headers, headers, retrieve_nct_number


class WParent:
    """Creation of object which has a parent an item tag and a name tag, used in treeview"""

    def __init__(self, item, name, name_parent):
        self.item = item
        self.child_name = name
        self.parent_name = name_parent


# Font and background
# ------->

large_font = ("Times New Roman", 18, 'bold')
big_title = ("Times New Roman", 20, 'bold')
side_rep = ("Times New Roman", 15, 'bold')
side_rep_magnified = ("Times New Roman", 18, 'bold')
width, height = 800, 300
width_main, height_main = width * 0.7, height * 7
local_path = "/Images/Logo_F4J_EN.png"
dir_Script = os.path.dirname(os.path.abspath(__file__))
image_path = dir_Script + local_path


# Background color: #87AADE

# /------->
class PicturesPackage(object):
    """Object embed all the picture needed"""

    def __init__(self):
        self.main_icon = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Logo_F4J_Long_EN.png").resize((200, 35), Image.ANTIALIAS))
        self.home = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Home.png").resize((50, 50), Image.ANTIALIAS))
        self.home_magnified = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Home.png").resize((60, 60), Image.ANTIALIAS))
        self.user_setting = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/User_Setting.png").resize((50, 50), Image.ANTIALIAS))
        self.user_setting_magnified = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/User_Setting.png").resize((60, 60), Image.ANTIALIAS))
        self.data_setting = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Check_List.png").resize((50, 50), Image.ANTIALIAS))
        self.data_setting_magnified = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Check_List.png").resize((60, 60), Image.ANTIALIAS))
        self.launch_board = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Launch.png").resize((50, 50), Image.ANTIALIAS))
        self.launch_board_magnified = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Launch.png").resize((60, 60), Image.ANTIALIAS))
        self.exit = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Exit_Prog.png").resize((40, 40), Image.ANTIALIAS))
        self.exit_magnified = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Exit_Prog.png").resize((50, 50), Image.ANTIALIAS))
        self.info = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Info.png").resize((40, 40), Image.ANTIALIAS))
        self.info_magnified = ImageTk.PhotoImage(
            Image.open(dir_Script + "/Images/Info.png").resize((50, 50), Image.ANTIALIAS))


class Interface(tk.Tk):
    """Main Class trigger and call the other classes"""

    def __init__(self, *args, **kwargs):
        """initialisation method ; """
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("ClinicalTrials.gov data retriever")
        # container is the main box for all the frames(Pages).
        container = Frame(self)
        container.configure(background='white')
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.frames = {}
        for F in (StartPage, PageOne, PageTwo, PageThree):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="NSEW")
            frame.configure(bg='white')
        self.show_frame(StartPage)
        self.images = PicturesPackage()  # calling the image object
        self.frame_lower_button = Frame(self, relief=SOLID, borderwidth=0,
                                        background='#87AADE', bg='white')
        self.frame_lower_button.pack(fill=X, side=BOTTOM, anchor=CENTER)
        self.button_quit_window = Label(self.frame_lower_button, image=self.images.exit, bg='white')
        self.button_quit_window.pack(side=LEFT, anchor=CENTER, ipadx=5)
        self.button_quit_window.bind('<Button-1>', self.destroy_window)
        self.button_quit_window.bind("<Enter>", self.on_enter_exit)
        self.button_quit_window.bind("<Leave>", self.on_leave_exit)
        self.button_info = Label(self.frame_lower_button, image=self.images.info, bg='white')
        self.button_info.pack(side=RIGHT, anchor=CENTER, ipadx=5)
        self.button_info.bind('<Button-1>', self.show_info)
        self.button_info.bind("<Enter>", self.on_enter_info)
        self.button_info.bind("<Leave>", self.on_leave_info)
        self.icon_designer = Label(self.frame_lower_button, image=self.images.main_icon, bg='white')
        self.icon_designer.pack(side=TOP, pady=8)

    def destroy_window(self, event):
        """Close the app"""
        self.destroy()

    def destroy_top(self, root):
        """Close the top window"""
        root.destroy()

    def show_info(self, event):
        """Open a pop up window"""
        # global info_top_level
        info_top_level = Toplevel()
        info_top_level.title("Info & Credit")
        x = self.winfo_x()
        y = self.winfo_y()
        info_top_level.geometry("+%d+%d" % (x + 300, y + 200))
        info = Text(info_top_level, font=('helvetica', 14, 'italic'), height=16, bg='white', fg='black')
        info.insert(INSERT, "Current Tool Version : CTDR_V01 \n\n"
                            "Versions: \n\n"
                            "    - CTDR First Release,  August 18th, 2020 \n\n"
                            "    - CTDR V01,                August 30th, 2020 : \n"
                            "               * Minor widget arrangement \n"
                            "               * Add option to insert NCT ID on each row of the first column of csv \n"
                            "               * Add info section \n"
                            "               * Update Functions to retrieve all clinical results elements:\n"
                            "               * Fix freezing screen "
                            "               * Add progression status of running code\n\n"
                            " Design and programing : 2020\n")
        info.config(state='disabled')
        info.pack(fill='x', anchor=CENTER)
        button_exit_top = ttk.Button(info_top_level, text="Close", command=lambda: self.destroy_top(info_top_level))
        button_exit_top.pack()

    def on_enter_exit(self, event):
        self.button_quit_window.configure(image=self.images.exit_magnified)
        self.button_quit_window.pack(side=LEFT, anchor=CENTER, ipadx=0)

    def on_leave_exit(self, enter):
        self.button_quit_window.configure(image=self.images.exit)
        self.button_quit_window.pack(side=LEFT, anchor=CENTER, ipadx=5)

    def on_enter_info(self, event):
        self.button_info.configure(image=self.images.info_magnified)
        self.button_info.pack(side=RIGHT, anchor=CENTER, ipadx=0)

    def on_leave_info(self, enter):
        self.button_info.configure(image=self.images.info)
        self.button_info.pack(side=RIGHT, anchor=CENTER, ipadx=5)

    def show_frame(self, cont):
        """ Raise the frame you want to bring forward"""
        frame = self.frames[cont]
        frame.tkraise()
        time.sleep(0.1)

    def go_home(self, event):
        """bring home page forward"""
        self.show_frame(StartPage)

    def go_user(self, event):
        """bring First Page page forward"""
        self.show_frame(PageOne)

    def go_setting(self, event):
        """bring Second page forward"""
        self.show_frame(PageTwo)

    def go_launch(self, event):
        """bring third page forward"""
        self.show_frame(PageThree)

    def get_page(self, page_class):
        """This function is essential to share variables between the class"""
        return self.frames[page_class]


class StartPage(tk.Frame):
    """Main Page"""

    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        Pilimg = Image.open(image_path)
        self.img = ImageTk.PhotoImage(Pilimg.resize((width, height), Image.ANTIALIAS))
        Label(self, image=self.img, bg='white').place(relwidth=1, relheight=1)
        self.images = PicturesPackage()
        self.header_frame = LabelFrame(self, borderwidth=0, background='#87AADE')
        self.header_frame.pack(fill='both')
        header_title = Label(self.header_frame, text='ClinicalTrials.gov Data Retriever Tool',
                             font=large_font,
                             background='#87AADE', foreground="white")
        header_title.pack(side=TOP, padx=(0, 0), pady=(5, 5))
        button_frame = LabelFrame(self, relief='sunken', borderwidth=2, background='#87AADE')
        button_frame.pack(side=BOTTOM, anchor=CENTER, pady=60)
        button_frame.tkraise()
        welcome = Label(self, text='Welcome to the ClinicalTrials.gov Data Retriever Tool',
                        font=big_title, bg='white',foreground='#8C6604')
        welcome.pack(side=TOP, fill='both', pady=40)
        label_file = Label(button_frame, bg="#87AADE")
        label_file.pack(side=LEFT, anchor=CENTER, fill='both', padx=10)
        label_setting = Label(button_frame, bg="#87AADE")
        label_setting.pack(side=LEFT, anchor=CENTER, fill='both', padx=10)
        label_launch = Label(button_frame, bg="#87AADE")
        label_launch.pack(side=LEFT, anchor=CENTER, fill='both', padx=10)
        style_button_int = ttk.Style()
        style_button_int_2 = ttk.Style()
        style_button_int.map("C.TButton",
                             foreground=[('active', 'brown4'), ('pressed', 'blue')],
                             background=[('active', 'brown4'), ('pressed', '!disabled', 'black')],
                             filedbackground=[('active', 'brown4')]
                             )
        style_button_int_2.configure('W.TButton', font=('calibri', 10, 'bold', 'underline'),
                                     foreground='red', background='blue')
        self.menu_file_image = Label(label_file, image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=5, pady=(10, 5))
        self.menu_file_image.bind('<Button-1>', self.controller.go_user)
        self.menu_file = Label(label_file, text='XML Schema', bg="#87AADE", fg='white', font=side_rep)
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))
        self.menu_file.bind('<Button-1>', self.controller.go_user)
        self.menu_file_image.bind("<Enter>", self.on_enter_B_file)
        self.menu_file_image.bind("<Leave>", self.on_leave_B_file)
        self.menu_setting_image = Label(label_setting, image=self.images.data_setting, bg='white')
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting_image.bind('<Button-1>', self.controller.go_setting)
        self.menu_setting_image.bind("<Enter>", self.on_enter_B_setting)
        self.menu_setting_image.bind("<Leave>", self.on_leave_B_setting)
        self.menu_setting = Label(label_setting, text='User Settings', bg="#87AADE", fg='white', font=side_rep)
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))
        self.menu_setting.bind('<Button-1>', self.controller.go_setting)
        self.menu_launch_image = Label(label_launch, image=self.images.launch_board, bg='white')
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch_image.bind('<Button-1>', self.controller.go_launch)
        self.menu_launch_image.bind("<Enter>", self.on_enter_B_launch)
        self.menu_launch_image.bind("<Leave>", self.on_leave_B_launch)
        self.menu_launch = Label(label_launch, text='LaunchBoard', bg="#87AADE", fg='white', font=side_rep)
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))
        self.menu_launch.bind('<Button-1>', self.controller.go_launch)

    def on_enter_B_file(self, event):
        self.menu_file_image.configure(image=self.images.user_setting_magnified)
        self.menu_file_image.pack(padx=0, pady=(5, 0))
        self.menu_file.configure(font=side_rep_magnified, fg="gold")
        self.menu_file.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_file(self, enter):
        self.menu_file_image.configure(image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=5, pady=(10, 5))
        self.menu_file.configure(font=side_rep, fg='white')
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_setting(self, event):
        self.menu_setting_image.configure(image=self.images.data_setting_magnified)
        self.menu_setting_image.pack(padx=0, pady=(5, 0))
        self.menu_setting.configure(font=side_rep_magnified, fg="gold")
        self.menu_setting.pack(pady=(0, 1), padx=(1, 1))

    def on_leave_B_setting(self, enter):
        self.menu_setting_image.configure(image=self.images.data_setting)
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting.configure(font=side_rep, fg='white')
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_launch(self, event):
        self.menu_launch_image.configure(image=self.images.launch_board_magnified)
        self.menu_launch_image.pack(padx=0, pady=(5, 0))
        self.menu_launch.configure(font=side_rep_magnified, fg="gold")
        self.menu_launch.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_launch(self, enter):
        self.menu_launch_image.configure(image=self.images.launch_board)
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch.configure(font=side_rep, fg='white')
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))


class PageOne(tk.Frame):
    """First Page"""

    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        # calling other class
        self.images = PicturesPackage()

        # setting headers and icon
        self.header_frame = LabelFrame(self, borderwidth=0, background='#87AADE')
        self.header_frame.pack(fill='both')
        header_title = Label(self.header_frame, text='ClinicalTrials.gov Data Retriever Tool',
                             font=large_font,
                             background='#87AADE', foreground="white")
        header_title.pack(side=TOP, padx=(0, 0), pady=(5, 5))
        button_frame = LabelFrame(self, relief=None, font=('helvetica', 16, 'bold'), borderwidth=0,
                                  background='#87AADE')
        button_frame.pack(side='left', fill='y')
        button_frame.tkraise()
        self.menu_home_image = Label(button_frame, image=self.images.home, bg='white')
        self.menu_home_image.pack(pady=(80, 5))
        self.menu_home_image.bind('<Button-1>', self.controller.go_home)
        self.menu_home_image.bind("<Enter>", self.on_enter_B_Home)
        self.menu_home_image.bind("<Leave>", self.on_leave_B_Home)
        self.menu_home = Label(button_frame, text='Home', bg="#87AADE", fg='white', font=side_rep)
        self.menu_home.pack(pady=(0, 5))
        self.menu_home.bind('<Button-1>', self.controller.go_home)
        self.menu_file_image = Label(button_frame, image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=10, pady=(10, 5))
        self.menu_file_image.bind('<Button-1>', self.controller.go_user)
        self.menu_file = Label(button_frame, text='XML Schema', bg="#87AADE", fg='gold', font=side_rep)
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))
        self.menu_file.bind('<Button-1>', self.controller.go_user)
        self.menu_setting_image = Label(button_frame, image=self.images.data_setting, bg='white')
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting_image.bind('<Button-1>', self.controller.go_setting)
        self.menu_setting_image.bind("<Enter>", self.on_enter_B_setting)
        self.menu_setting_image.bind("<Leave>", self.on_leave_B_setting)
        self.menu_setting = Label(button_frame, text='User Settings', bg="#87AADE", fg='white', font=side_rep)
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))
        self.menu_setting.bind('<Button-1>', self.controller.go_setting)
        self.menu_launch_image = Label(button_frame, image=self.images.launch_board, bg='white')
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch_image.bind('<Button-1>', self.controller.go_launch)
        self.menu_launch_image.bind("<Enter>", self.on_enter_B_launch)
        self.menu_launch_image.bind("<Leave>", self.on_leave_B_launch)
        self.menu_launch = Label(button_frame, text='LaunchBoard', bg="#87AADE", fg='white', font=side_rep)
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))
        self.menu_launch.bind('<Button-1>', self.controller.go_launch)

        # Init Variables
        self.var_file_pattern = StringVar()
        self.file_name = ''
        # Add Widget to the Frame
        north_west_frame = LabelFrame(self, text="Select XML Schema", relief="solid", font=('helvetica', 16, 'bold'),
                                      labelanchor=N, bg='white')
        north_west_frame.pack(side=TOP, fill='x', padx=5, pady=4, anchor=NW)
        explanation_one = Text(north_west_frame, font=('helvetica', 14, 'italic'), height=3, bg='white', fg='black')
        explanation_one.insert(INSERT, "The tool uses an XML Schema that retrieves all the input of the database.\n "
                                       "When ClinicalTrials.gov updates their XML Schema,"
                                       " you need to download the new XML Schema to have access to the added input;\n "
                                       "see: https://clinicaltrials.gov/ct2/resources/download")
        explanation_one.config(state='disabled')
        explanation_one.pack(fill='x', anchor=CENTER)
        self.north_west_one = LabelFrame(north_west_frame, text=' XML Schema Currently Used', relief="raise",
                                         font=('helvetica', 14, 'bold'), labelanchor=NW, bg='white')
        self.north_west_one.pack(fill='x', padx=10, pady=10, anchor=NW)
        self.XML_scheme = Label(self.north_west_one, text=str(self.var_file_pattern.get()),
                                font=('helvetica', 13), bg='white')
        self.XML_scheme.pack(fill='x', padx=10, anchor=NW)
        self.north_west_two = LabelFrame(north_west_frame, text=' Select New XML Schema', relief="raise",
                                         font=('helvetica', 14, 'bold'), labelanchor=NW, bg='white')
        self.north_west_two.pack(fill='x', padx=10, pady=10, anchor=NW)
        self.selection_auto = LabelFrame(self.north_west_two, text='Automatically from the web', labelanchor=N,
                                         bg='white',
                                         relief='sunken', font=('helvetica', 13, 'bold'))
        self.selection_auto.pack(fill='both', padx=10, pady=4, anchor=NW, side='left')
        self.add_from_web = ttk.Button(self.selection_auto,
                                       text="Download the latest XML schema version",
                                       command=lambda: self.add_xml_schema_from_web(), style='C.TButton')
        self.add_from_web.pack(padx=10, pady=4, anchor=NW, side=LEFT)
        self.selection = LabelFrame(self.north_west_two, text='Manually from folder', labelanchor=N, bg='white',
                                    relief='sunken',
                                    font=('helvetica', 13, 'bold'))
        self.selection.pack(fill='both', padx=10, pady=4, anchor=NW)
        select_XML_file = ttk.Button(self.selection, text="Select XML File", command=lambda: self.browse_pattern(),
                                     style='C.TButton')
        select_XML_file.pack(padx=10, pady=4, anchor=NW)
        self.file_directory = Label(self.selection, text='File directory:', font=('helvetica', 13, 'bold'), bg='white')
        self.file_directory.pack(padx=10, pady=4, anchor=W)
        self.add_file = ttk.Button(self.selection, text="Add XML Schema to database",
                                   command=lambda: self.add_to_database(), style='C.TButton')
        self.add_file.pack(padx=10, pady=4, anchor=NW)
        self.file_dir_lab = Label(self.selection, text='', font=('helvetica', 13), bg='white')
        self.file_dir_lab.pack(side=LEFT, fill='x', padx=10, pady=4, anchor=NW)
        self.list_combo = ttk.Combobox(self.north_west_one, width=70)
        self.list_combo.bind("<<ComboboxSelected>>", self.select_it)
        self.list_combo.pack()
        apply_change = ttk.Button(self.north_west_one, text="Apply Change", command=lambda: self.applychange(),
                                  style='C.TButton')
        apply_change.pack(padx=10, pady=4, anchor=NW)
        delete_from_db = ttk.Button(self.north_west_one, text="Delete schema from database",
                                    command=lambda: self.delete_file_db(), style='C.TButton')
        delete_from_db.pack(padx=10, pady=4, anchor=NW)
        '''----Interacting with database embedding XML schema name and path :----'''
        self.list_product = []
        self.connection = sqlite3.connect(dir_Script + "/XMLSchema/XMLSchema.db")
        self.c = self.connection.cursor()
        self.c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='XMLSchema' ''')
        if self.c.fetchone()[0] == 1:
            pass
        else:
            self.c.execute("""CREATE TABLE XMLSchema (
                    File_Name text,  
                    file_path text
                    )""")
        self.c.execute("SELECT file_path FROM XMLSchema")
        file_path = self.c.fetchall()
        if file_path is None:
            pass
        else:
            for row in file_path:
                if os.path.isfile(row[0]):
                    self.c.execute("SELECT File_Name FROM XMLSchema where file_path=?", (row[0],))
                    self.list_product.append(self.c.fetchone()[0])
                else:
                    self.c.execute("""DELETE from XMLSchema where file_path=?""", (row[0],))
        if self.list_product != []:
            self.list_combo.config(values=self.list_product)
            self.list_combo.current(0)
            selection = self.list_combo.get()
            self.c.execute(''' SELECT file_path FROM XMLSchema WHERE File_Name=?''', (selection,))
            self.var_file_pattern.set(self.c.fetchone()[0])
            self.XML_scheme.config(text=str(self.list_combo.get()), font=('helvetica', 13), fg='black')
        else:
            self.XML_scheme.config(
                text="No XML schema to follow, please add the last version automatically or manually with the "
                     "commands below",
                font=('helvetica', 13, 'italic'), fg='red')
        self.connection.commit()
        self.connection.close()

    def on_enter_B_Home(self, event):
        self.menu_home_image.configure(image=self.images.home_magnified)
        self.menu_home_image.pack(pady=(76, 0))
        self.menu_home.configure(font=side_rep_magnified, fg="gold")
        self.menu_home.pack(pady=(0, 0))

    def on_leave_B_Home(self, enter):
        self.menu_home_image.configure(image=self.images.home, bg='white')
        self.menu_home_image.pack(pady=(80, 5))
        self.menu_home.configure(font=side_rep, fg='white')
        self.menu_home.pack(pady=(0, 5))

    def on_enter_B_file(self, event):
        self.menu_file_image.configure(image=self.images.user_setting_magnified)
        self.menu_file_image.pack(padx=0, pady=(5, 0))
        self.menu_file.configure(font=side_rep_magnified, fg="gold")
        self.menu_file.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_file(self, enter):
        self.menu_file_image.configure(image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=5, pady=(10, 5))
        self.menu_file.configure(font=side_rep, fg='gold')
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_setting(self, event):
        self.menu_setting_image.configure(image=self.images.data_setting_magnified)
        self.menu_setting_image.pack(padx=0, pady=(5, 0))
        self.menu_setting.configure(font=side_rep_magnified, fg="gold")
        self.menu_setting.pack(pady=(0, 1), padx=(1, 1))

    def on_leave_B_setting(self, enter):
        self.menu_setting_image.configure(image=self.images.data_setting)
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting.configure(font=side_rep, fg='white')
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_launch(self, event):
        self.menu_launch_image.configure(image=self.images.launch_board_magnified)
        self.menu_launch_image.pack(padx=0, pady=(5, 0))
        self.menu_launch.configure(font=side_rep_magnified, fg="gold")
        self.menu_launch.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_launch(self, enter):
        self.menu_launch_image.configure(image=self.images.launch_board)
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch.configure(font=side_rep, fg='white')
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))

    def select_it(self, event):
        Selection = self.list_combo.get()
        self.connection = sqlite3.connect(dir_Script + "/XMLSchema/XMLSchema.db")
        self.c = self.connection.cursor()
        self.c.execute(''' SELECT File_Path FROM XMLSchema WHERE File_Name=?''', (Selection,))
        self.var_file_pattern.set(self.c.fetchone()[0])
        self.XML_scheme.config(text=str(Selection), font=('helvetica', 13), fg='black')
        self.connection.commit()
        self.connection.close()

    def add_to_database(self):
        # Interact with data base :
        self.connection = sqlite3.connect(dir_Script + "/XMLSchema/XMLSchema.db")
        self.c = self.connection.cursor()
        if self.file_name and self.file_path != '':
            self.c.execute("SELECT * FROM XMLSchema WHERE File_Name=?", (self.file_name,))
            if self.c.fetchone() is None:
                self.c.execute("INSERT INTO XMLSchema(File_Name,File_Path) VALUES (?,?)",
                               (self.file_name, self.file_path))
                self.list_product.append(self.file_name)
                self.list_combo.config(values=self.list_product)
                self.list_combo.set(self.file_name)
                Selection = self.list_combo.get()
                self.c.execute(''' SELECT File_Path FROM XMLSchema WHERE File_Name=?''', (Selection,))
                self.var_file_pattern.set(self.c.fetchone()[0])
                self.XML_scheme.config(fg='black', text=str(self.list_combo.get()))
                self.connection.commit()
                self.connection.close()
            else:
                print("Already exist!")
        else:
            print('one argument is missing')

    def applychange(self):
        if self.list_combo.get() != '' and self.var_file_pattern.get() != '':
            self.page_two = self.controller.get_page(PageTwo)
            self.page_two.full_list_unchanged = get_major_titles(self.var_file_pattern.get())
            self.page_two.full_list = self.page_two.full_list_unchanged[:]
            self.page_two.model_structural_list = take_name(
                parse_model(self.var_file_pattern.get(),
                            self.page_two.full_list))
            self.page_two.plot_data_header(2)
            self.page_two.actualise_treeview()

    def delete_file_db(self):
        if self.list_combo.get() != '':
            self.connection = sqlite3.connect(dir_Script + "/XMLSchema/XMLSchema.db")
            self.c = self.connection.cursor()
            self.c.execute("""DELETE from XMLSchema where File_Name=?""", (self.list_combo.get(),))
            self.connection.commit()
            self.connection.close()
            self.list_product.remove(self.list_combo.get())
            self.list_combo.config(values=self.list_product)
            if self.list_product != []:
                self.list_combo.set(self.list_product[0])
                self.applychange()
            else:
                self.XML_scheme.config(
                    text="No XML schema to follow, please add the last version automatically or manually with the "
                         "commands below ",
                    font=('helvetica', 13, 'italic'), fg='red')
                self.list_combo.set("")

    def add_xml_schema_from_web(self):
        today = date.today()
        year = today.strftime("%Y")
        month = today.strftime("%m")
        R.urlretrieve("https://clinicaltrials.gov/ct2/html/images/info/public.xsd", dir_Script + "/XMLSchema/" +
                      str(year) + "_" + str(month) + "_" + "ClinicalTrials_XML_Schema.xml")
        self.file_path = dir_Script + "/XMLSchema/" + str(year) + "_" + str(month) + "_" + "ClinicalTrials_XML_Schema.xml"
        self.file_name = str(year) + "_" + str(month) + "_" + "ClinicalTrials_XML_Schema.xml"
        self.connection = sqlite3.connect(dir_Script + "/XMLSchema/XMLSchema.db")
        self.c = self.connection.cursor()
        self.c.execute("SELECT * FROM XMLSchema WHERE File_Name=?", (self.file_name,))
        if self.c.fetchone() is None:
            self.c.execute("INSERT INTO XMLSchema(File_Name,File_Path) VALUES (?,?)",
                           (self.file_name, self.file_path))
            self.list_product.append(self.file_name)
            self.list_combo.config(values=self.list_product)
            self.list_combo.set(self.file_name)
            Selection = self.list_combo.get()
            self.c.execute(''' SELECT File_Path FROM XMLSchema WHERE File_Name=?''', (Selection,))
            self.var_file_pattern.set(self.c.fetchone()[0])
            print(self.var_file_pattern.get())
            self.XML_scheme.config(fg='black', text=str(self.list_combo.get()))
            self.connection.commit()
            self.connection.close()
        else:
            print("Already exist!")

    def browse_pattern(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("xml schema files", ".xml")])
        print(self.file_path)
        self.file_dir_lab.config(text=self.file_path)
        self.file_name = os.path.basename(self.file_path)


class PageTwo(tk.Frame):
    """Second Page"""

    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)

        # calling other classes
        self.images = PicturesPackage()
        self.page_one = self.controller.get_page(PageOne)
        self.images = PicturesPackage()

        # setting headers
        self.header_frame = LabelFrame(self, borderwidth=0, background='#87AADE')
        self.header_frame.pack(fill='both')
        header_title = Label(self.header_frame, text='ClinicalTrials.gov Data Retriever Tool',
                            font=large_font,
                            background='#87AADE', foreground="white")
        header_title.pack(side=TOP, padx=(0, 0), pady=(5, 5))
        buttonframe = LabelFrame(self, relief=None, font=('helvetica', 16, 'bold'), borderwidth=0, background='#87AADE')
        buttonframe.pack(side='left', fill='y')
        buttonframe.tkraise()

        # Navigation
        self.menu_home_image = Label(buttonframe, image=self.images.home, bg='white')
        self.menu_home_image.pack(pady=(80, 5))
        self.menu_home_image.bind('<Button-1>', self.controller.go_home)
        self.menu_home_image.bind("<Enter>", self.on_enter_B_Home)
        self.menu_home_image.bind("<Leave>", self.on_leave_B_Home)
        self.menu_home = Label(buttonframe, text='Home', bg="#87AADE", fg='white', font=side_rep)
        self.menu_home.pack(pady=(0, 5))
        self.menu_home.bind('<Button-1>', self.controller.go_home)
        self.menu_file_image = Label(buttonframe, image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=10, pady=(10, 5))
        self.menu_file_image.bind('<Button-1>', self.controller.go_user)
        self.menu_file = Label(buttonframe, text='XML Schema', bg="#87AADE", fg='white', font=side_rep)
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))
        self.menu_file.bind('<Button-1>', self.controller.go_user)
        self.menu_file_image.bind("<Enter>", self.on_enter_B_file)
        self.menu_file_image.bind("<Leave>", self.on_leave_B_file)
        self.menu_setting_image = Label(buttonframe, image=self.images.data_setting, bg='white')
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting_image.bind('<Button-1>', self.controller.go_setting)
        self.menu_setting = Label(buttonframe, text='User Settings', bg="#87AADE", fg='gold', font=side_rep)
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))
        self.menu_setting.bind('<Button-1>', self.controller.go_setting)
        self.menu_launch_image = Label(buttonframe, image=self.images.launch_board, bg='white')
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch_image.bind('<Button-1>', self.controller.go_launch)
        self.menu_launch_image.bind("<Enter>", self.on_enter_B_launch)
        self.menu_launch_image.bind("<Leave>", self.on_leave_B_launch)
        self.menu_launch = Label(buttonframe, text='LaunchBoard', bg="#87AADE", fg='white', font=side_rep)
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))
        self.menu_launch.bind('<Button-1>', self.controller.go_launch)

        # Set Variables

        """ Get the pattern from page one """
        self.pattern = self.page_one.var_file_pattern.get()
        self.main_list = ['id_info', 'official_title', 'overall_status', 'condition', 'intervention',
                         'primary_outcome', 'sponsors', 'eligibility', 'phase', 'enrollment', 'study_type',
                         'study_design_info', 'start_date',
                         'primary_completion_date', 'completion_date', 'study_first_posted',
                         'study_first_submitted', 'last_update_posted', 'overall_official', 'location',
                         'required_header']
        self.var3 = StringVar()
        self.user_list = []
        """ ---Frame 1-:-Treeview---"""
        self.clinical_option = IntVar()
        self.clinical_option.set(0)
        self.select_frame = LabelFrame(self, text='Data Headers', font=('helvetica', 16, 'bold'), bg='white', padx=25)
        self.select_frame.pack(side=LEFT, fill='y', padx=4, pady=(4, 0))
        self.first_row = LabelFrame(self.select_frame, border=0, bg='white')
        self.first_row.pack(side=LEFT, fill="y")
        self.second_row = LabelFrame(self.select_frame, border=0, bg='white')
        self.second_row.pack(side=LEFT, fill="y")
        self.third_row = LabelFrame(self.select_frame, border=0, bg='white')
        self.third_row.pack(side=LEFT, fill="y")
        first_north_mid_frame = LabelFrame(self.select_frame, text=' Display Clinical Results', relief="ridge",
                                        font=('helvetica', 14, 'bold'), bg='white', pady=5)
        first_north_mid_frame.pack(side=TOP, pady=(0, 20))
        select_option_results = Radiobutton(first_north_mid_frame, text='Show clinical_results',
                                            variable=self.clinical_option, value=1,
                                            command=lambda: self.plot_data_header(3), bg='white')
        select_option_results.pack(side=LEFT)
        select_option_results = Radiobutton(first_north_mid_frame, text='Hide clinical_results',
                                            variable=self.clinical_option, value=0,
                                            command=lambda: self.plot_data_header(3), bg='white')
        select_option_results.pack(side=LEFT)

        """ ---Frame 3-:-intermed button---"""

        self.list_removed_elements = []
        self.item_list_complet = []
        self.frame_inter_button = LabelFrame(self, borderwidth=0, bg='white')
        button_remove = ttk.Button(self.frame_inter_button, text='Remove ->>',
                                   command=lambda: self.remove_elements(itemListComplet), style='C.TButton')
        button_remove.pack(anchor=NE, pady=(100, 5))
        button_add = ttk.Button(self.frame_inter_button, text='<<- Add      ', command=lambda: self.add_elements(),
                                style='C.TButton')
        button_add.pack(anchor=NW, pady=(5, 100))
        button_clear = ttk.Button(self.frame_inter_button, text='Clear All', style='C.TButton',
                                  command=lambda: self.plot_data_header(0))
        button_clear.pack(anchor=CENTER, pady=(0, 5))
        button_select_all = ttk.Button(self.frame_inter_button, text='Select All', command=lambda: self.plot_data_header(1),
                                       style='C.TButton')
        button_select_all.pack(anchor=CENTER, pady=(0, 5))
        button_reset = ttk.Button(self.frame_inter_button, text='Reset Setting', style='C.TButton',
                                  command=lambda: self.plot_data_header(2))
        button_reset.pack(anchor=CENTER, pady=(0, 5))

        """------------Display Frame 4--------------"""

        self.third_frame = LabelFrame(self, text='Elements removed', relief="raise", font=('helvetica', 16, 'bold'),
                                      bg='white')
        self.list_removed_el = Listbox(self.third_frame, height=30, width=25, bg='white')
        self.list_removed_el.bind("<<ListboxSelect>>", lambda x: self.selection_list_box())
        self.list_removed_el.pack(fill=BOTH, expand=True, pady=(10, 0))

        """-------------Initiate display-----------"""
        self.display_frame = LabelFrame(self, text='Tree Structure', relief="raise", font=('helvetica', 16, 'bold'),
                                        width=500, bg='white')
        self.treeview = ttk.Treeview(self.display_frame)
        self.treeview.pack(fill="both", expand=True, side=TOP, anchor=NW)
        if self.pattern != '':
            self.full_list_unchanged = get_major_titles(self.pattern)
            self.full_list = self.full_list_unchanged[:]
            self.model_structural_list = take_name(
                parse_model(self.pattern, self.full_list))
            self.plot_data_header(2)
            self.actualise_treeview()
        self.display_frame.pack(side=LEFT, fill="y", padx=(0, 4), pady=(4, 0))
        self.frame_inter_button.pack(side=LEFT, fill="y", padx=(0, 4), pady=(4, 10))
        self.third_frame.pack(side=LEFT, fill='both', expand=True, padx=(0, 4), pady=(4, 0))

    def on_enter_B_Home(self, event):
        self.menu_home_image.configure(image=self.images.home_magnified)
        self.menu_home_image.pack(pady=(76, 0))
        self.menu_home.configure(font=side_rep_magnified, fg="gold")
        self.menu_home.pack(pady=(0, 0))

    def on_leave_B_Home(self, enter):
        self.menu_home_image.configure(image=self.images.home, bg='white')
        self.menu_home_image.pack(pady=(80, 5))
        self.menu_home.configure(font=side_rep, fg='white')
        self.menu_home.pack(pady=(0, 5))

    def on_enter_B_file(self, event):
        self.menu_file_image.configure(image=self.images.user_setting_magnified)
        self.menu_file_image.pack(padx=0, pady=(5, 0))
        self.menu_file.configure(font=side_rep_magnified, fg="gold")
        self.menu_file.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_file(self, enter):
        self.menu_file_image.configure(image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=5, pady=(10, 5))
        self.menu_file.configure(font=side_rep, fg='white')
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_setting(self, event):
        self.menu_setting_image.configure(image=self.images.data_setting_magnified)
        self.menu_setting_image.pack(padx=0, pady=(5, 0))
        self.menu_setting.configure(font=side_rep_magnified, fg="gold")
        self.menu_setting.pack(pady=(0, 1), padx=(1, 1))

    def on_leave_B_setting(self, enter):
        self.menu_setting_image.configure(image=self.images.data_setting)
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting.configure(font=side_rep, fg='gold')
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_launch(self, event):
        self.menu_launch_image.configure(image=self.images.launch_board_magnified)
        self.menu_launch_image.pack(padx=0, pady=(5, 0))
        self.menu_launch.configure(font=side_rep_magnified, fg="gold")
        self.menu_launch.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_launch(self, enter):
        self.menu_launch_image.configure(image=self.images.launch_board)
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch.configure(font=side_rep, fg='white')
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))

    def clear_all(self):
        """add element selected from treevieew, and move it to the element removed frame and list"""
        for element in self.list_removed_elements:
            if element.item == self.element_selected:
                self.list_removed_el.delete(ACTIVE)
                self.list_removed_elements.remove(element)
                self.treeview.insert(element.parent_name, 'end', element.item, text=element.child_name)
        self.actualise_treeview()

    def plot_data_header(self, entier):
        self.first_row.pack_forget()
        self.first_row = LabelFrame(self.select_frame, border=0, bg='white')
        self.first_row.pack(side=LEFT, fill="y")
        self.second_row.pack_forget()
        self.second_row = LabelFrame(self.select_frame, border=0, bg='white')
        self.second_row.pack(side=LEFT, fill="y")
        self.third_row.pack_forget()
        self.third_row = LabelFrame(self.select_frame, border=0, bg='white')
        self.third_row.pack(side=LEFT, fill="y")
        self.var2 = []
        i = 0
        j = 0
        number_rows = 21
        if self.clinical_option.get() == 1 and not 'clinical_results' in self.full_list and 'clinical_results' in \
                self.full_list_unchanged:
            self.full_list.append('clinical_results')
        elif self.clinical_option.get() == 0 and 'clinical_results' in self.full_list and 'clinical_results' in \
                self.full_list_unchanged:
            self.full_list.remove("clinical_results")
        for member in self.full_list:
            condition = False
            if i > number_rows:
                j += 1
                i = 0
            self.var2.append(IntVar())
            if entier == 2:
                if member in self.main_list:
                    self.var2[j * number_rows + i + j].set(1)
            if entier == 3:
                if member in self.main_list:
                    self.var2[j * number_rows + i + j].set(1)
                if not member in self.user_list:
                    self.var2[j * number_rows + i + j].set(0)
                else:
                    self.var2[j * number_rows + i + j].set(1)
            elif entier == 0:
                self.var2[j * number_rows + i + j].set(0)
                self.treeview.delete()
            elif entier == 1:
                self.var2[j * number_rows + i + j].set(1)
            if j == 0:
                self.check_it = Checkbutton(self.first_row, text=member, font=('Time', 12),
                                            variable=self.var2[j * number_rows + i + j],
                                            command=lambda: self.actualise_treeview(), bg='white')
            elif j == 1:
                self.check_it = Checkbutton(self.second_row, text=member, font=('Time', 12),
                                            variable=self.var2[j * number_rows + i + j],
                                            command=lambda: self.actualise_treeview(), bg='white')
            elif j == 2:
                self.check_it = Checkbutton(self.third_row, text=member, font=('Time', 12),
                                            variable=self.var2[j * number_rows + i + j],
                                            command=lambda: self.actualise_treeview(), bg='white')
            self.check_it.pack(anchor=W)
            i += 1
        self.actualise_treeview()
        """ ---Frame 2-:-Treeview---"""

    def call_back(self, event):
        """get the element selected in the treeview"""
        global itemListComplet
        itemListComplet = []
        for item in self.treeview.selection():
            attribute = WParent(item, self.treeview.item(item, "text"), self.treeview.parent(item))
            itemListComplet.append(attribute)
        return

    def remove_elements(self, item_list_complet):
        """remove element selected from treevieew, and add it to the element removed frame and list"""
        if item_list_complet == []:
            pass
        else:
            for element in item_list_complet:
                if element.item in self.full_list:
                    pass
                elif len(self.treeview.get_children(self.treeview.parent(element.item))) > 1:
                    self.treeview.delete(element.item)
                    self.list_removed_el.insert("end", element.item)
                    self.list_removed_elements.append(element)
        self.actualise_treeview()

    def selection_list_box(self):
        """get the element selected in the Element removed frame"""
        cs = self.list_removed_el.curselection()[0]
        self.element_selected = self.list_removed_el.get(cs)

    def add_elements(self):
        """Command of add button; add element selected from treeview, and remove it to the element removed
         frame and list"""
        for element in self.list_removed_elements:
            if element.item == self.element_selected:
                self.list_removed_el.delete(ACTIVE)
                self.list_removed_elements.remove(element)
                self.treeview.insert(element.parent_name, 'end', element.item, text=element.child_name)
                self.treeview.item(element.item, open=True)
        self.actualise_treeview()

    def removeel(self, UserList):
        """Link between the DataHeader and the Element Removed Section"""
        stock_index_to_remove = []
        for i in range(len(self.list_removed_elements)):
            element = self.list_removed_elements[i]
            parent = element.parent_name
            if not parent in UserList:
                stock_index_to_remove.append(i)
                index = self.list_removed_el.get(0, "end").index(element.item)
                self.list_removed_el.delete(index)
        if len(stock_index_to_remove) > 1:
            stock_index_to_remove.sort(reverse=True)
            for index in stock_index_to_remove:
                self.list_removed_elements.pop(index)
        elif stock_index_to_remove != []:
            self.list_removed_elements.pop()
        return self.list_removed_el, self.list_removed_elements

    def actualise_treeview(self):
        """Actualise the tree structure based on what has been selected in data header and element removed section"""
        self.user_list = []
        self.var4 = StringVar([])
        for i in range(len(self.full_list)):
            if self.var2[i].get() == 1:
                self.user_list.append(self.full_list[i])
        if self.user_list == []:
            self.var3.set('No Element Selected')
        else:
            self.var3.set('Elements Selected')
        self.var4.set(self.user_list)
        self.treeview.pack_forget()
        self.treeview = ttk.Treeview(self.display_frame)
        self.treeview.pack(fill="both", expand=True, side=TOP, anchor=NW)
        self.treeview.tag_configure("SubelementStyle", font=('Calibri', 12))
        self.treeview.tag_configure("Heading", font=('Calibri', 14, 'bold'))
        list_removed_el, list_removed_element = self.removeel(self.user_list)
        for i in range(len(self.user_list)):
            element = self.user_list[i]
            self.treeview.insert('', str(i), str(element), text=element)
            self.treeview.item(str(element), tags=('Heading'), open=True)
            if isinstance(self.model_structural_list[self.model_structural_list.index(element) + 1], list):
                for j in range(len(self.model_structural_list[self.model_structural_list.index(
                        element) + 1])):
                    element_other = self.model_structural_list[self.model_structural_list.index(element) + 1][
                        j]
                    if isinstance(element_other, str):
                        self.list_removed_element_child_name = []
                        for items in list_removed_element:
                            self.list_removed_element_child_name.append(items.parent_name + '-' + items.child_name)
                        if not (str(element) + '-' + str(
                                element_other)) in self.list_removed_element_child_name:
                            self.treeview.insert(str(element), str(j), str(element) + '-' + str(element_other),
                                                 text=element_other)
                            self.treeview.item(str(element) + '-' + str(element_other), tags=('SubelementStyle'),
                                               open=True)
        self.treeview.bind("<<TreeviewSelect>>", self.call_back)
        return (self.user_list)


class PageThree(tk.Frame):
    """Second Page"""

    def __init__(self, parent, controller):
        self.controller = controller
        tk.Frame.__init__(self, parent)
        # calling other classes
        self.page_two = self.controller.get_page(PageTwo)
        self.page_one = self.controller.get_page(PageOne)
        self.images = PicturesPackage()

        # setting Headers and icon
        self.header_frame = LabelFrame(self, borderwidth=0, background='#87AADE')
        self.header_frame.pack(fill='both')
        header_title = Label(self.header_frame, text='ClinicalTrials.gov Data Retriever Tool',
                            font=large_font,
                            background='#87AADE', foreground="white")
        header_title.pack(side=TOP, padx=(0, 0), pady=(5, 5))
        button_frame = LabelFrame(self, relief=None, font=('helvetica', 16, 'bold'), borderwidth=0, background='#87AADE')
        button_frame.pack(side='left', fill='y')
        button_frame.tkraise()

        # Frame Package
        self.menu_home_image = Label(button_frame, image=self.images.home, bg='white')
        self.menu_home_image.pack(pady=(80, 5))
        self.menu_home_image.bind('<Button-1>', self.controller.go_home)
        self.menu_home_image.bind("<Enter>", self.on_enter_B_Home)
        self.menu_home_image.bind("<Leave>", self.on_leave_B_Home)
        self.menu_home = Label(button_frame, text='Home', bg="#87AADE", fg='white', font=side_rep)
        self.menu_home.pack(pady=(0, 5))
        self.menu_home.bind('<Button-1>', self.controller.go_home)
        self.menu_file_image = Label(button_frame, image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=10, pady=(10, 5))
        self.menu_file_image.bind('<Button-1>', self.controller.go_user)
        self.menu_file = Label(button_frame, text='XML Schema', bg="#87AADE", fg='white', font=side_rep)
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))
        self.menu_file.bind('<Button-1>', self.controller.go_user)
        self.menu_file_image.bind("<Enter>", self.on_enter_B_file)
        self.menu_file_image.bind("<Leave>", self.on_leave_B_file)
        self.menu_setting_image = Label(button_frame, image=self.images.data_setting, bg='white')
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting_image.bind('<Button-1>', self.controller.go_setting)
        self.menu_setting_image.bind("<Enter>", self.on_enter_B_setting)
        self.menu_setting_image.bind("<Leave>", self.on_leave_B_setting)
        self.menu_setting = Label(button_frame, text='User Settings', bg="#87AADE", fg='white', font=side_rep)
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))
        self.menu_setting.bind('<Button-1>', self.controller.go_setting)
        self.menu_launch_image = Label(button_frame, image=self.images.launch_board, bg='white')
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch_image.bind('<Button-1>', self.controller.go_launch)
        self.menu_launch = Label(button_frame, text='LaunchBoard', bg="#87AADE", fg='gold', font=side_rep)
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))
        self.menu_launch.bind('<Button-1>', self.controller.go_launch)

        # In tab 3:
        self.folder_name = ""
        self.csv_name = ""
        self.csv_file_path = ''
        self.south_west_frame = LabelFrame(self, text=' Select Name & Directory of the Output File', relief="solid",
                                           font=('helvetica', 16, 'bold'), labelanchor=N, bg='white')
        self.south_west_frame.pack(fill=X, anchor=NW, padx=5, pady=4)
        self.mid_west_frame = LabelFrame(self.south_west_frame, text='CSV file', relief="raised",
                                         font=('helvetica', 14, 'bold'), bg='white', borderwidth=1)
        self.mid_west_frame.pack(fill='x', padx=10, pady=4, anchor=NW)
        self.Frame_two_one = LabelFrame(self.mid_west_frame, borderwidth=0, bg='white')
        self.Frame_two_one.pack(fill=X, anchor=NW)
        self.frame_two_two = LabelFrame(self.mid_west_frame, borderwidth=0, bg='white')
        self.frame_two_two.pack(fill=X, anchor=NW)
        self.csv_label = Label(master=self.Frame_two_one, text='File name (no extension): ', font=('helvetica', 13, 'bold'),
                               bg='white')
        self.csv_label.pack(side=LEFT, padx=10, pady=4, anchor=NW)
        self.csv_name_entry = Entry(self.Frame_two_one, width="20", bg='floral white', fg="brown4")
        self.csv_name_entry.pack(padx=10, pady=4, anchor=NW)
        self.button_get_csv_name = ttk.Button(self.frame_two_two, text='Apply Name',
                                              command=lambda: self.get_csv_name('PageSelf'), style='C.TButton')
        self.button_get_csv_name.pack(ipadx=20, padx=10, pady=4, anchor=NW)
        self.csv_name_label = Label(master=self.frame_two_two, text='CSV file name: ', font=('helvetica', 13, 'bold'),
                                    bg='white')
        self.csv_name_label.pack(padx=10, pady=4, anchor=NW)
        self.sec_south_west_frame = LabelFrame(self.south_west_frame, text='Select Folder', relief="raise",
                                               font=('helvetica', 14, 'bold'), bg='white')
        self.sec_south_west_frame.pack(fill=BOTH, ipadx=20, padx=10, pady=4, anchor=NW)
        self.browse_save_folder = ttk.Button(self.sec_south_west_frame, text="Select Folder",
                                             command=lambda: self.browse_folder(), style='C.TButton')
        self.browse_save_folder.pack(padx=10, pady=4, anchor=NW)
        self.browse_save_folder_label = Label(master=self.sec_south_west_frame, text='CSV folder path: ',
                                              font=('helvetica', 13, 'bold'), bg='white')
        self.browse_save_folder_label.pack(padx=10, pady=4, anchor=NW)

        self.frame_one = LabelFrame(self, text='Enter ClinicalTrials.gov URL', font=('helvetica', 16, 'bold'),
                                    labelanchor=N, relief="solid", bg='white')
        self.frame_one.pack(fill=X, anchor=NW, padx=5, pady=4)
        self.frame_one_tab_three = LabelFrame(self.frame_one, text='Single URL Search', font=('helvetica', 14, 'bold'),
                                              bg='white', labelanchor=NW)
        self.frame_one_tab_three.pack(fill=Y, side=LEFT, anchor=NW, pady=5)
        self.frame_one_tab_four = LabelFrame(self.frame_one, text='Batch URL Search', font=('helvetica', 14, 'bold'),
                                             bg='white', labelanchor=NW)
        self.frame_one_tab_four.pack(fill=BOTH, pady=5, padx=10)
        self.frame_one.pack(fill=X, anchor=NW)
        self.frame_one_one = LabelFrame(self.frame_one_tab_three, borderwidth=0, bg='white')
        self.frame_one_one.pack(fill=X, anchor=NW)
        self.frame_one_two = LabelFrame(self.frame_one_tab_three, borderwidth=0, bg='white')
        self.frame_one_two.pack(fill=X, anchor=NW)
        label_seven = Label(self.frame_one_one, text='Enter your URL:', font=('helvetica', 13, 'bold'), bg='white')
        label_seven.pack(side=LEFT, anchor=NW)
        self.entry_url = Entry(self.frame_one_one, width="35", bg='floral white', fg="brown4")
        self.entry_url.pack()
        self.state_label = Label(self.frame_one_two, text='URL status:', font=('helvetica', 13, 'bold'), bg='white')
        self.state_label.pack(anchor=NW)
        button_launch_one = ttk.Button(self.frame_one_two, text='Launch single search', command=lambda: self.launch_program(1)
                                    , style='C.TButton')
        button_launch_one.pack(anchor=NW, pady=5)
        select_csv_file = ttk.Button(self.frame_one_tab_four, text="Select CSV File",
                                     command=lambda: self.browsep_csv_super_launch(),
                                     style='C.TButton')
        select_csv_file.pack(anchor=NW)
        self.csv_file_path_lb = Label(self.frame_one_tab_four, text='File directory:', font=('helvetica', 13, 'bold'), bg='white')
        self.csv_file_path_lb.pack(anchor=W)
        button_launch_two = ttk.Button(self.frame_one_tab_four, text='Launch in batch', command=lambda: self.launch_program(2),
                                       style='C.TButton')
        button_launch_two.pack(anchor=NW, pady=5)
        # North mid
        self.single_row_opt = IntVar()
        self.single_row_opt.set(1)
        self.disp_sump_up_row_var = IntVar()
        self.disp_sump_up_row_var.set(1)
        self.disp_NCT_col = IntVar()
        self.disp_NCT_col.set(1)

        north_mid_frame = LabelFrame(self, text='Options', relief="solid", font=('helvetica', 16, 'bold'),
                                   labelanchor=N, bg='white')
        north_mid_frame.pack(fill='x', padx=5, pady=4, anchor=NW)
        second_north_mid_frame = LabelFrame(north_mid_frame, text=' Display Options in CSV', relief="raise",
                                         font=('helvetica', 14, 'bold'), bg='white')
        second_north_mid_frame.pack(fill='x', padx=10, pady=4, anchor=NW)
        disp_multiple_row = Radiobutton(second_north_mid_frame,
                                      text='Multiple Rows - Display fields with multiple variables in separate rows',
                                      variable=self.single_row_opt,
                                      value=0, bg='white')
        disp_multiple_row.pack(padx=10, anchor=NW)
        disp_single_row = Radiobutton(second_north_mid_frame,
                                    text='Single Row - Display fields with multiple variables as single cells (separated by "|")',
                                    variable=self.single_row_opt,
                                    value=1, bg='white')
        disp_single_row.pack(padx=10, anchor=NW)
        disp_sump_up_row = Checkbutton(second_north_mid_frame, text='Display a summary header row',
                                    variable=self.disp_sump_up_row_var, bg='white')
        disp_sump_up_row.pack(padx=10, anchor=NW)
        disp_nct_col = Checkbutton(second_north_mid_frame, text='Display NCT Number in the first column',
                                   variable=self.disp_NCT_col, bg='white')
        disp_nct_col.pack(padx=10, anchor=NW)
        self.progress_bar = ttk.Progressbar(self, orient='horizontal', length=286, mode='determinate')
        self.progress_bar.pack(padx=(0, 120))
        self.progress_bar["maximum"] = 100
        self.progress_number = Label(self, text='%', font=side_rep, bg='white')
        self.progress_number.pack(padx=(0, 120))

    def on_enter_B_Home(self, event):
        self.menu_home_image.configure(image=self.images.home_magnified)
        self.menu_home_image.pack(pady=(76, 0))
        self.menu_home.configure(font=side_rep_magnified, fg="gold")
        self.menu_home.pack(pady=(0, 0))

    def on_leave_B_Home(self, enter):
        self.menu_home_image.configure(image=self.images.home, bg='white')
        self.menu_home_image.pack(pady=(80, 5))
        self.menu_home.configure(font=side_rep, fg='white')
        self.menu_home.pack(pady=(0, 5))

    def on_enter_B_file(self, event):
        self.menu_file_image.configure(image=self.images.user_setting_magnified)
        self.menu_file_image.pack(padx=0, pady=(5, 0))
        self.menu_file.configure(font=side_rep_magnified, fg="gold")
        self.menu_file.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_file(self, enter):
        self.menu_file_image.configure(image=self.images.user_setting, bg='white')
        self.menu_file_image.pack(padx=5, pady=(10, 5))
        self.menu_file.configure(font=side_rep, fg='white')
        self.menu_file.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_setting(self, event):
        self.menu_setting_image.configure(image=self.images.data_setting_magnified)
        self.menu_setting_image.pack(padx=0, pady=(5, 0))
        self.menu_setting.configure(font=side_rep_magnified, fg="gold")
        self.menu_setting.pack(pady=(0, 1), padx=(1, 1))

    def on_leave_B_setting(self, enter):
        self.menu_setting_image.configure(image=self.images.data_setting)
        self.menu_setting_image.pack(padx=5, pady=(10, 5))
        self.menu_setting.configure(font=side_rep, fg='white')
        self.menu_setting.pack(pady=(0, 5), padx=(8, 8))

    def on_enter_B_launch(self, event):
        self.menu_launch_image.configure(image=self.images.launch_board_magnified)
        self.menu_launch_image.pack(padx=0, pady=(5, 0))
        self.menu_launch.configure(font=side_rep_magnified, fg="gold")
        self.menu_launch.pack(pady=(0, 1), padx=(0, 0))

    def on_leave_B_launch(self, enter):
        self.menu_launch_image.configure(image=self.images.launch_board)
        self.menu_launch_image.pack(padx=5, pady=(10, 5))
        self.menu_launch.configure(font=side_rep, fg='gold')
        self.menu_launch.pack(pady=(0, 5), padx=(8, 8))

    def browse_folder(self):
        """ Allow user to select a directory and store it in global var called foldername"""
        global browse_save_folder_label_two, folder_name
        self.folder_name = filedialog.askdirectory(title='Select a folder')
        self.browse_save_folder_label.config(text='CSV folder Label: ' + self.folder_name)

    def get_csv_name(self, wind_calling):
        if wind_calling == "PageSelf":
            self.csv_name = self.csv_name_entry.get()
        elif wind_calling == "PageTop":
            self.csv_name = self.CSVTopentry.get()
        if self.csv_name != '':
            self.csv_name = self.csv_name.translate({ord(i): None for i in
                                                   '\"/:*?<>|'})
            if self.csv_name[len(self.csv_name) - 1] == " ":
                self.csv_name = self.csv_name.translate({ord(' '): '_'})
            self.csv_name = self.csv_name + ".csv"
            self.csv_name_label.config(text='CSV file name: ' + self.csv_name)
        else:
            self.csv_name_label.config(text='CSV file name: ' + self.csv_name)

    def get_url(self, url):
        if url == '':
            state = 'Enter URL Before Launching app'
            color = 'gold3'
        else:
            try:
                url = R.urlopen(url)
                state = 'URL Valid'
                color = 'green'
            except error.URLError as e:
                state = "Invalid URL" + str(e.reason)
                color = 'red'
        if state == 'URL Valid':
            if is_zipfile(BytesIO(url.read())) == True:
                state = 'URL Valid'
                color = 'green'
            else:
                state = "Invalid URL ; don't forget : download_studies? in url"
                color = 'red'
        return state, color

    def test_url(self, URL):
        state, color = self.get_url(URL)
        self.state_label.configure(fg=color, font=('Helvetica', 14), text='URL status:' + str(state))
        return state, URL

    def cond_destroy(self, windlevel, entier):
        windlevel.destroy()
        self.launch_program(entier)

    def browsep_csv_super_launch(self):
        self.csv_file_path = filedialog.askopenfilename(filetypes=[("CSV file", ".csv")])
        self.csv_file_path_lb.config(text=self.csv_file_path)

    def launch_program(self, entier):
        global top
        start_time = time.time()
        if self.folder_name == "":
            messagebox.showinfo(title='Folder Info',
                                message='No folder selected \n csv file will be stored in the AppScript folder')
        if self.csv_name == "" and self.csv_name_entry.get() == "":
            top = Toplevel()
            top.title("Enter CSV file name")
            x = self.winfo_x()
            y = self.winfo_y()
            top.geometry("+%d+%d" % (x + 500, y + 200))
            self.CSVTopentry = Entry(top, width="28")
            self.CSVTopentry.pack()
            button_get_csv_top = ttk.Button(top, text='Apply Name', command=lambda: self.get_csv_name("PageTop"),
                                          style='C.TButton')
            button_get_csv_top.pack()
            button = ttk.Button(top, text="Close And Relaunch", command=lambda: self.cond_destroy(top, entier))
            button.pack()
        else:
            if self.csv_name == "":
                if self.csv_name_entry.get() != "":
                    self.csv_name = self.csv_name_entry.get()
                else:
                    print('Error in CSV name, renamed as Serge.csv')
                    self.csv_name = 'Serge.csv'
            if self.folder_name == '':
                complete_csv_name = self.csv_name
            else:
                complete_csv_name = self.folder_name + "/" + self.csv_name
            self.user_list = self.page_two.actualise_treeview()
            self.inter_user_list = self.user_list[:]
            if self.page_one.var_file_pattern.get() == '':
                pass
            else:
                Pattern = self.page_one.var_file_pattern.get()
            """even though those variables have already been set in page two, we have to reparse the model in case we 
            relaunch the program multiple times """
            model_struct_list_watt = parse_model(Pattern,
                                              self.page_two.full_list)
            model_structural_list = take_name(parse_model(Pattern, self.page_two.full_list))
            """Creating a list gathering elements and subelements required by user"""
            for element in self.user_list:
                if element in model_structural_list:
                    if isinstance(model_structural_list[model_structural_list.index(element) + 1], list):
                        list_members = (model_structural_list[model_structural_list.index(
                            element) + 1])
                        list_members_watt = model_struct_list_watt[model_struct_list_watt.index(
                            element) + 1]
                        for items in self.page_two.list_removed_elements:
                            if items.parent_name == model_structural_list[model_structural_list.index(element)] \
                                    and items.child_name in model_structural_list[model_structural_list.index(element) + 1]:
                                if list_members.index(items.child_name) < len(
                                        list_members) - 1:
                                    if isinstance(list_members[list_members.index(items.child_name) + 1],
                                                  list):
                                        index = list_members.index(items.child_name) + 1
                                        list_members.pop(index)
                                        list_members_watt.pop(index)
                                index_sub_element = list_members.index(items.child_name)
                                list_members.pop(index_sub_element)
                                list_members_watt.pop(index_sub_element)
                        self.inter_user_list.insert(self.inter_user_list.index(element) + 1, list_members_watt)
            condition = True

            '''---------------------------Run Single URL---------------------------'''
            if entier == 1:
                self.progress_number.configure(text='Launching single search')
                self.progress_number.update()
                state, URL = self.test_url(self.entry_url.get())
                if state == 'URL Valid':
                    if self.page_two.var3.get() == 'Elements Selected':
                        url = R.urlopen(URL)
                        pass
                    else:
                        condition = False
                        messagebox.showerror(title=None, message='Element not selected')
                else:
                    condition = False
                    messagebox.showerror(message='Invalid URL')
                if condition == True:
                    list_utile_launch = take_name(self.inter_user_list)
                    index_number_lines = number_of_lines(list_utile_launch)
                    headers_var = headers(list_utile_launch, index_number_lines)
                    sumup_lign = realign_all_headers(headers_var)
                    with open(complete_csv_name, 'w') as F:  # open a virgin csv file
                        # dialect_write = csv.Sniffer().sniff(F.readline(), [',', ';'])
                        # F.seek(0)
                        # the_writer_Launch = csv.writer(F, dialect_write)
                        # the_writer_Launch = csv.writer(F, delimiter='@')
                        the_writer_Launch = csv.writer(F, delimiter=',')
                        # first_row_launch = ['SEP=@']  # separate in different columns every @
                        # the_writer_Launch.writerow(first_row_launch)  # Command to excel
                        count_nct = 0

                        # Writting Headers

                        for element_header in headers_var:
                            count_nct += 1
                            if self.disp_NCT_col.get() == 1 and count_nct == 1:
                                the_writer_Launch.writerow(['nct_id'] + element_header)
                            elif self.disp_NCT_col.get() == 0:
                                the_writer_Launch.writerow(element_header)
                            elif self.disp_NCT_col.get() == 1 and count_nct > 1:
                                the_writer_Launch.writerow([''] + element_header)
                        if self.disp_sump_up_row_var.get() == 1:
                            if self.disp_NCT_col.get() == 1:
                                the_writer_Launch.writerow(['nct_id'] + sumup_lign)
                            elif self.disp_NCT_col.get() == 0:
                                the_writer_Launch.writerow(sumup_lign)
                        # if an element as several attribute in an xml file it will display every attribute in a
                        # single row gives a clean csv
                        progression = 0
                        zip_unit_kb = 0
                        self.sum_info = 0
                        self.file_info_list = []
                        count_file_total = 0
                        count_total_percent = 0
                        if self.single_row_opt.get() == 1:
                            with ZipFile(BytesIO(url.read())) as my_zip_file:
                                for z_info in my_zip_file.filelist:
                                    size_z_info = z_info.file_size
                                    self.file_info_list.append(size_z_info)
                                    self.sum_info += size_z_info
                                self.sum_info = self.sum_info / 1000
                                for file_contained in my_zip_file.namelist():
                                    count_file_total += 1
                                    zip_unit_kb += float(self.file_info_list[count_file_total - 1]) / 1000  # kB
                                    if count_file_total == len(self.file_info_list):
                                        progression = 100
                                    else:
                                        progression = int(zip_unit_kb / self.sum_info * 100)
                                    if progression in range(0, 100, 10):
                                        count_total_percent += 1
                                    else:
                                        count_total_percent = 0
                                    tree_launch = ET.parse(my_zip_file.open(file_contained))
                                    root_launch = tree_launch.getroot()
                                    nct_number = retrieve_nct_number(root_launch)
                                    list_el_retrieved = main_search_v01(self.page_two.full_list_unchanged,
                                                                        self.inter_user_list,
                                                                        root_launch)
                                    each_row_displayed = write_all_rows_v01(list_el_retrieved)
                                    gather_each_row = single_row(each_row_displayed)
                                    if self.disp_NCT_col.get() == 1:
                                        if gather_each_row == [[]]:
                                            gather_each_row.remove([])
                                        gather_each_row.insert(0, nct_number)
                                        the_writer_Launch.writerow(gather_each_row)
                                    else:
                                        if gather_each_row == [[]]:
                                            pass
                                        else:
                                            the_writer_Launch.writerow(gather_each_row)
                                    if progression in range(0, 100, 10) and count_total_percent == 1:
                                        self.progress_bar["value"] = progression
                                        self.progress_bar.update()
                                        self.progress_number.configure(text=str(progression) + '%')
                                        self.progress_number.update()

                                    if progression == 100:
                                        self.progress_bar["value"] = progression
                                        self.progress_bar.update()
                                        total_time = "    --- %s seconds ---" % (int(time.time() - start_time))
                                        self.progress_number.configure(text=str(progression) + '%' + total_time)
                                        self.progress_number.update()
                        else:  # multiple row might be convenient for result plots
                            with ZipFile(BytesIO(url.read())) as my_zip_file:
                                for z_info in my_zip_file.filelist:
                                    size_z_info = z_info.file_size
                                    self.file_info_list.append(size_z_info)
                                    self.sum_info += size_z_info
                                self.sum_info = self.sum_info / 1000
                                for file_contained in my_zip_file.namelist():
                                    count_file_total += 1
                                    zip_unit_kb += float(self.file_info_list[count_file_total - 1]) / 1000  # kB
                                    if count_file_total == len(self.file_info_list):
                                        progression = 100
                                    else:
                                        progression = int(zip_unit_kb / self.sum_info * 100)
                                    if progression in range(0, 100, 10):
                                        count_total_percent += 1
                                    else:
                                        count_total_percent = 0
                                    tree_launch = ET.parse(my_zip_file.open(file_contained))
                                    root_launch = tree_launch.getroot()
                                    nct_number = retrieve_nct_number(root_launch)
                                    list_el_retrieved = main_search_v01(self.page_two.full_list_unchanged,
                                                                        self.inter_user_list, root_launch)
                                    each_row_displayed = write_all_rows_v01(list_el_retrieved)
                                    if each_row_displayed == []:
                                        if self.disp_NCT_col.get() == 1:
                                            the_writer_Launch.writerow([str(nct_number)])
                                    else:
                                        if self.disp_NCT_col.get() == 1:
                                            for Line in each_row_displayed:
                                                Line.insert(0, nct_number)
                                                the_writer_Launch.writerow(Line)
                                        elif self.disp_NCT_col.get() == 0:
                                            for Line in each_row_displayed:
                                                the_writer_Launch.writerow(Line)
                                    if progression in range(0, 100, 10) and count_total_percent == 1:
                                        self.progress_bar["value"] = progression
                                        self.progress_bar.update()
                                        self.progress_number.configure(text=str(progression) + '%')
                                        self.progress_number.update()

                                    if progression == 100:
                                        self.progress_bar["value"] = progression
                                        self.progress_bar.update()
                                        total_time = "    --- %s seconds ---" % (int(time.time() - start_time))
                                        self.progress_number.configure(text=str(progression) + '%' + total_time)
                                        self.progress_number.update()
                else:
                    print(condition)

                '''---------------------------Run in Batch---------------------------'''

            elif entier == 2:
                self.progress_number.configure(text='Launching in batch')
                self.progress_number.update()
                if not os.path.isfile(self.csv_file_path):
                    messagebox.showinfo(title=None, message="CSV file doesn't exist or not selected")
                    print("file doesn't exist or not selected")
                else:
                    list_url_red = []
                    list_forbidden_url = []
                    with open(self.csv_file_path, newline='') as csv_file:
                        dialect = csv.Sniffer().sniff(csv_file.readline(), [',', ';'])
                        csv_file.seek(0)
                        csv_reader = csv.reader(csv_file, dialect)
                        number_col_disp = []
                        List_info_red = []
                        line_numb = 0
                        first_line_disp = []  # Headers of csv containing url to run in batch
                        for row in csv_reader:
                            line_numb += 1
                            if line_numb > 1:
                                state, URL = self.test_url(row[0])
                                if state == 'URL Valid':
                                    list_url_red.append(row[0])
                                    List_info_red.append(row)
                                    number_col_disp.append(len(row))
                                else:
                                    list_forbidden_url.append(row[0])
                            else:
                                first_line_disp.append(row)
                        number_max_col_disp = max(number_col_disp)
                    empty = []
                    for i in range(number_max_col_disp):
                        empty.append('')
                    if self.page_two.var3.get() == 'Elements Selected':
                        pass
                    else:
                        condition = False
                        messagebox.showinfo(title=None, message='Element not selected')
                    if condition:
                        list_utile_launch = take_name(self.inter_user_list)
                        index_number_lines = number_of_lines(list_utile_launch)
                        headers_var = headers(list_utile_launch, index_number_lines)
                        sumup_lign = realign_all_headers(headers_var)
                        with open(complete_csv_name, 'w') as F:  # open a virgin csv file
                            # dialect_write = csv.Sniffer().sniff(F.readline(), [',', ';'])
                            # F.seek(0)
                            # the_writer_Launch = csv.writer(F, delimiter='@')
                            # the_writer_Launch = csv.writer(F, dialect_write)
                            the_writer_Launch = csv.writer(F, delimiter=',')
                            # first_row_launch = ['SEP=@']  # separate in different columns every @
                            # the_writer_Launch.writerow(first_row_launch)  # Command to excel
                            for element in list_forbidden_url:
                                print("Warning: Following Url didn't run -> " + element)
                                the_writer_Launch.writerow(['URL not reached: ', str(element)])
                            count_nct = 0
                            for element_header in headers_var:
                                count_nct += 1
                                if self.disp_NCT_col.get() == 1 and count_nct == 1:
                                    the_writer_Launch.writerow(empty + ['nct_id'] + element_header)
                                elif self.disp_NCT_col.get() == 1 and count_nct > 1:
                                    the_writer_Launch.writerow(empty + [''] + element_header)
                                elif self.disp_NCT_col.get() == 0:
                                    the_writer_Launch.writerow(empty + element_header)
                            if self.disp_sump_up_row_var.get() == 1:
                                if self.disp_NCT_col.get() == 1:
                                    the_writer_Launch.writerow(first_line_disp[0] + ['nct_id'] + sumup_lign)
                                elif self.disp_NCT_col.get() == 0:
                                    the_writer_Launch.writerow(first_line_disp[0] + sumup_lign)
                            # if an element as several attribute in an xml file it will display every attribute
                            # in a different row - convenient for results plot
                            self.sum_info = 0
                            self.file_info_list = []
                            for element in list_url_red:
                                url = R.urlopen(element)
                                size_in_list_url_red = 0
                                for z_info in ZipFile(BytesIO(url.read())).filelist:
                                    size_z_info = z_info.file_size
                                    self.file_info_list.append(size_z_info)
                                    size_in_list_url_red += size_z_info
                                zip_kb = float(size_in_list_url_red) / 1000
                                self.sum_info += zip_kb
                            progression = 0
                            zip_unit_kb = 0
                            count_file_total = 0
                            count_total_percent = 0
                            if self.single_row_opt.get() == 1:
                                compteur = 0
                                for element in list_url_red:
                                    count = 0
                                    compteur += 1
                                    url = R.urlopen(element)
                                    with ZipFile(BytesIO(url.read())) as my_zip_file:
                                        for file_contained in my_zip_file.namelist():
                                            count += 1
                                            count_file_total += 1
                                            zip_unit_kb += float(self.file_info_list[count_file_total - 1]) / 1000  # kB
                                            if count_file_total == len(self.file_info_list):
                                                progression = 100
                                            else:
                                                progression = int(zip_unit_kb / self.sum_info * 100)
                                            if progression in range(0, 100, 5):
                                                count_total_percent += 1
                                            else:
                                                count_total_percent = 0
                                            tree_launch = ET.parse(my_zip_file.open(file_contained))
                                            root_launch = tree_launch.getroot()
                                            list_el_retrieved = main_search_v01(self.page_two.full_list_unchanged,
                                                                                self.inter_user_list, root_launch)
                                            each_row_displayed = write_all_rows_v01(list_el_retrieved)
                                            nct_number = retrieve_nct_number(root_launch)
                                            gather_each_row = single_row(each_row_displayed)
                                            if gather_each_row == [[]]:
                                                gather_each_row.remove([])
                                                if self.disp_NCT_col.get() == 1:
                                                    gather_each_row.insert(0, nct_number)
                                                if count == 1:
                                                    the_writer_Launch.writerow(
                                                        List_info_red[compteur - 1] + gather_each_row)
                                                elif count > 1 and self.disp_NCT_col.get() == 1:
                                                    the_writer_Launch.writerow(empty + gather_each_row)
                                            else:
                                                if self.disp_NCT_col.get() == 1:
                                                    gather_each_row.insert(0, nct_number)
                                                if count == 1:
                                                    the_writer_Launch.writerow(
                                                        List_info_red[compteur - 1] + gather_each_row)
                                                elif count > 1:
                                                    the_writer_Launch.writerow(empty + gather_each_row)
                                            if progression in range(0, 100, 5) and count_total_percent == 1:
                                                self.progress_bar["value"] = progression
                                                self.progress_bar.update()
                                                self.progress_number.configure(text=str(progression) + '%')
                                                self.progress_number.update()

                                            if progression == 100:
                                                self.progress_bar["value"] = progression
                                                self.progress_bar.update()
                                                total_time = "    --- %s seconds ---" % (int(time.time() - start_time))
                                                self.progress_number.configure(text=str(progression) + '%' + total_time)
                                                self.progress_number.update()
                            else:  # Multiple rows
                                compteur = 0
                                total_url_numb = len(list_url_red)
                                for element in list_url_red:
                                    count = 0
                                    compteur += 1
                                    progression = compteur / total_url_numb * 100
                                    url = R.urlopen(element)
                                    with ZipFile(BytesIO(url.read())) as my_zip_file:
                                        for file_contained in my_zip_file.namelist():
                                            count += 1
                                            count_file_total += 1
                                            zip_unit_kb += float(self.file_info_list[count_file_total - 1]) / 1000  # kB
                                            if count_file_total == len(self.file_info_list):
                                                progression = 100
                                            else:
                                                progression = int(zip_unit_kb / self.sum_info * 100)
                                            if progression in range(0, 100, 5):
                                                count_total_percent += 1
                                            else:
                                                count_total_percent = 0
                                            tree_launch = ET.parse(my_zip_file.open(file_contained))
                                            root_launch = tree_launch.getroot()
                                            list_el_retrieved = main_search_v01(self.page_two.full_list_unchanged,
                                                                                self.inter_user_list, root_launch)
                                            nct_number = retrieve_nct_number(root_launch)
                                            each_row_displayed = write_all_rows_v01(list_el_retrieved)
                                            if each_row_displayed == []:
                                                if count == 1:
                                                    if self.disp_NCT_col.get() == 1:
                                                        the_writer_Launch.writerow(List_info_red[compteur - 1] +
                                                                                   [str(nct_number)])
                                                    elif self.disp_NCT_col.get() == 0:
                                                        the_writer_Launch.writerow(List_info_red[compteur - 1])
                                                elif count > 1:
                                                    if self.disp_NCT_col.get() == 1:
                                                        the_writer_Launch.writerow(empty + [str(nct_number)])
                                            else:
                                                num_line = 0
                                                for Line in each_row_displayed:
                                                    num_line += 1
                                                    if self.disp_NCT_col.get() == 1:
                                                        Line.insert(0, nct_number)
                                                    if count == 1 and num_line == 1:
                                                        the_writer_Launch.writerow(List_info_red[compteur - 1] + Line)
                                                    else:
                                                        the_writer_Launch.writerow(empty + Line)
                                            if progression in range(0, 100, 5) and count_total_percent == 1:
                                                self.progress_bar["value"] = progression
                                                self.progress_bar.update()
                                                self.progress_number.configure(text=str(progression) + '%')
                                                self.progress_number.update()

                                            if progression == 100:
                                                self.progress_bar["value"] = progression
                                                self.progress_bar.update()
                                                total_time = "    --- %s seconds ---" % (int(time.time() - start_time))
                                                self.progress_number.configure(text=str(progression) + '%' + total_time)
                                                self.progress_number.update()

            else:
                print('Error : run stop before fully complete is duty')
        if condition:
            print('CSV File ready, running time = ' + "--- %s seconds ---" % (int(time.time() - start_time)))
        return


if __name__ == "__main__":
    app = Interface()
    app.configure(background='white')
    app.mainloop()
