# This script converts a binary file containing 16-bit color values (RGB565) that is generated when taking a screenshot
# into a binary file with 24-bit RGB values. This binary file is then converted into a bmp image using the microbmp library.

import ttkbootstrap as ttk
import ttkbootstrap.toast as popup
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip

from typing import Literal

from tkinter.filedialog import askdirectory

from PIL import Image, ImageTk

import os


class main_menu(ttk.Window):
    def __init__(self):
        # Initialize the main window and set the title, theme and minimal size
        super().__init__("Screenshot export", "darkly")
        self.minsize(550, 300)

        # Set up the default theme and style font
        self.defaultFont = "Consolas"
        self.style.configure(".", font=f"{self.defaultFont} 9")

        self.sourceDirectory = ""
        self.loadedFiles = []

        self.selectedFile = ""
        self.selectedFileNumber = ttk.StringVar()

        self.supportedFormats = ("png", "bmp", "gif")
        self.exportModes = {"selected":"Just the selected image", "all":"All"}

        self.init_GUI()


    def init_GUI(self):
        self.init_top_menu()
        self.init_shortcuts()
        self.init_main_GUI()

        Messagebox.ok(
            parent=self,
            title="First step",
            message="Please select a folder with .bin files from the PICO to start exporting them.",
            alert=True
        )

        self.select_directory()


    def init_main_GUI(self):
        # These frames will only be shown once a directory is selected
        self.leftFrame = ttk.Frame(self, padding=10)
        self.rightFrame = ttk.Frame(self, padding=10)

        self.operationFrame = ttk.LabelFrame(self.leftFrame, text="Select an operation to perform:", padding = 10)
        self.operationFrame.pack(fill=BOTH, side=LEFT, expand=False)

        self.previewFrame = ttk.LabelFrame(self.rightFrame, text="Select a file to preview:", padding=10)
        self.previewFrame.pack(fill=BOTH, side=LEFT, expand=False)

        self.exportFormatLabelFrame = ttk.LabelFrame(self.operationFrame, text="Select how should the file be exported", padding=10)
        self.exportFormatLabelFrame.pack(fill=X, side=TOP, expand=False)

        self.formatFrame = ttk.Frame(self.exportFormatLabelFrame)
        self.formatFrame.pack(fill=X, side=TOP, expand=False)
        self.formatLabel = ttk.Label(self.formatFrame, text="Format: ")
        self.formatLabel.pack(fill=X, side=LEFT, expand=True)
        self.formatBox = ttk.Combobox(self.formatFrame, values=self.supportedFormats, state="readonly")
        self.formatBox.pack(fill=X, side=RIGHT, expand=True)
        self.formatBox.set(self.supportedFormats[0])
        self.formatBox.bind("<<ComboboxSelected>>", self.validate_format_selection)


        self.modeFrame = ttk.Frame(self.exportFormatLabelFrame)
        self.modeFrame.pack(fill=X, side=TOP, expand=False)
        self.modeLabel = ttk.Label(self.modeFrame, text="Export mode: ")
        self.modeLabel.pack(fill=X, side=LEFT, expand=True)
        self.modeBox = ttk.Combobox(self.modeFrame, values=list(self.exportModes.values()), state="readonly")
        self.modeBox.pack(fill=X, side=RIGHT, expand=True)
        self.modeBox.set(self.exportModes["selected"])


        self.exportButton = ttk.Button(
            self.operationFrame, 
            text="Export",
            style="primary.TButton",
            command=self.export
            )
        self.exportButton.pack(fill=X, side=BOTTOM, expand=False, pady=10)


        self.selectedFileFrame = ttk.LabelFrame(self.previewFrame, text="Selected image:", padding = 10)
        self.selectedFileFrame.pack(fill=BOTH, side=TOP, expand=False)

        self.pathLabel = ttk.Label(self.selectedFileFrame, text="None", wraplength=500, bootstyle=(SUCCESS, INVERSE))
        self.pathLabel.pack(fill=NONE, side=TOP, expand=False, pady=10)

        self.imageLabel = ttk.Label(self.selectedFileFrame)
        self.imageLabel.pack(anchor=CENTER, fill=None, side=TOP, expand=True, pady=10)

        self.fileSelectionFrame = ttk.Frame(self.previewFrame)
        self.fileSelectionFrame.pack(fill=X, side=TOP, expand=False, pady=10)

        self.previousFileButton = ttk.Button(
            self.fileSelectionFrame, 
            text="<",
            style="primary.TButton", 
            command=self.previous_file
        )
        self.nextFileButton = ttk.Button(
            self.fileSelectionFrame, 
            text=">",
            style="primary.TButton" ,
            command=self.next_file
        )
        self.previousFileButton.pack(fill=NONE, side=LEFT, expand=False, pady=10)
        self.nextFileButton.pack(fill=NONE, side=RIGHT, expand=False, pady=10)


        self.currentFileNumberBox = ttk.Entry(
            self.fileSelectionFrame,
            textvariable=self.selectedFileNumber,
            validate="all",
            validatecommand=(self.register(self.validate_file_number), '%P'),
            invalidcommand=self.reset_file_number_box,
            width=6
        )
        self.currentFileNumberBox.bind("<KeyRelease>", self.number_entry_changed)
        self.currentFileNumberBox.pack(fill=NONE, side=LEFT, expand=True, pady=10)
        
        self.totalFilesNumber = ttk.Entry(
            self.fileSelectionFrame,
            state=DISABLED,
            width=6
        )
        self.totalFilesNumber.pack(fill=NONE, side=RIGHT, expand=True, pady=10)

        self.separatorLabel = ttk.Label(self.fileSelectionFrame, text="/")
        self.separatorLabel.pack(anchor=CENTER, fill=NONE, side=LEFT, expand=True, pady=10)


    def show_GUI(self):
        self.leftFrame.pack(anchor=NE, fill=NONE, side=LEFT, expand=False)
        self.rightFrame.pack(anchor=NW, fill=NONE, side=RIGHT, expand=False)

    def hide_GUI(self):
        self.leftFrame.pack_forget()
        self.rightFrame.pack_forget()


    def select_file(self, index:int):
        if index >= len(self.loadedFiles):
            index = 0
        elif index < 0:
            index = len(self.loadedFiles) - 1

        if not self.selectedFileNumber.get() == "":
            self.selectedFileNumber.set(str(index))

        self.selectedFile = self.loadedFiles[index]

        self.pathLabel.configure(text=self.selectedFile)
        self.update_image_preview()

    
    def next_file(self, *_):
        self.select_file(self.loadedFiles.index(self.selectedFile)+1)
        self.selectedFileNumber.set(self.loadedFiles.index(self.selectedFile))

    def previous_file(self, *_):
        self.select_file(self.loadedFiles.index(self.selectedFile)-1)
        self.selectedFileNumber.set(self.loadedFiles.index(self.selectedFile))


    def number_entry_changed(self, *_):
        if self.selectedFileNumber.get() == "":
            self.select_file(0)
        else:
            self.select_file(int(self.selectedFileNumber.get()))

    
    def validate_format_selection(self, *_):
        if self.formatBox.get() == "gif":
            self.modeBox.set(self.exportModes["all"])
            self.modeBox.configure(state="disabled")
        else:
            self.modeBox.configure(state="readonly")


    def validate_file_number(self, value):
        try:
            value = int(value)
        except:
            if value == "":
                return True
                
            popup.ToastNotification(
                title=f"Invalid value",
                message=f"This must be a number between {0} (inclusive) and {len(self.loadedFiles)} (exclusive).",
                duration=5000,
                icon="❌",
                bootstyle=WARNING
            ).show_toast()

            return False
        
        if 0 <= value < len(self.loadedFiles):
            return True
        else:
            popup.ToastNotification(
                title=f"Invalid value",
                message=f"This must be a number between {0} (inclusive) and {len(self.loadedFiles)} (exclusive).",
                duration=5000,
                icon="❌",
                bootstyle=WARNING
            ).show_toast()
            return False
        
    def reset_file_number_box(self):
        self.selectedFileNumber.set(str(self.loadedFiles.index(self.selectedFile)))
        

    def init_top_menu(self):
        self.topMenu = ttk.Menu(self)

        self.fileMenu = ttk.Menu(self.topMenu)
        self.fileMenu.add_command(
            label="Select input folder", 
            command=self.select_directory, 
            accelerator="Ctrl+O"
        )

        self.topMenu.add_cascade(label="File", menu=self.fileMenu)
        self.configure(menu=self.topMenu)


    def init_shortcuts(self):
        self.bind("<Control-o>", self.select_directory)


    def select_directory(self):
        self.loadedFiles = []

        self.sourceDirectory = askdirectory(
            parent=self, 
            mustexist=True, 
            title="Please select the input directory"
        )

        
        if not self.sourceDirectory == "":
            Messagebox.ok("The program will load all .bin files from the selected folder.",
                          "Info",
                          True,
                          self)
            self.load_directory()
        else:
            popup.ToastNotification(
                    title=f"Operation cancelled",
                    message=f"No directory was selected",
                    duration=5000,
                    icon="❌",
                    bootstyle=WARNING
            ).show_toast()

    
    def update_image_preview(self):
        newImage = self.convert_image(self.selectedFile)
        self.previewImage = ImageTk.PhotoImage(newImage)
        self.imageLabel.configure(image=self.previewImage)


    def load_directory(self):
        for file in os.listdir(self.sourceDirectory):
            if os.path.isfile(self.sourceDirectory + "/" + file) and str(file).endswith(".bin"):
                self.loadedFiles.append(self.sourceDirectory + "/" + file)

        if len(self.loadedFiles) > 0:
            self.loadedFiles.sort()
            
            popup.ToastNotification(
                title=f"Success",
                message=f"Successfully found {len(self.loadedFiles)} supported files.",
                duration=5000,
                icon="✅",
                bootstyle=SUCCESS
            ).show_toast()

            self.select_file(0)
            self.selectedFileNumber.set(self.loadedFiles.index(self.selectedFile))
            self.show_GUI()
        else:
            popup.ToastNotification(
                    title=f"Operation cancelled",
                    message=f"There were no supported files in the selected directory.",
                    duration=5000,
                    icon="❌",
                    bootstyle=WARNING
            ).show_toast()
            self.hide_GUI()
       

    @staticmethod
    def color(value565):
        """ 
        Converts the 16-bit color format to the 24-bit RGB format.
        """
        r5 = (value565 >> 11) & 0x1F
        g6 = (value565 >> 5) & 0x3F
        b5 = value565 & 0x1F

        # Convert to 8-bit (0–255) by scaling:
        r8 = (r5 * 255) // 31
        g8 = (g6 * 255) // 63
        b8 = (b5 * 255) // 31

        return (r8, g8, b8)
    

    def convert_image(self, path, size:tuple=(240, 240), scaleTo:tuple=(240,240)): 

        outputImage = Image.new("RGB", size)

        with open(path, 'rb') as tmp:
            for i in range(0, len(tmp.read()), 2):
                tmp.seek(i) 
                value = tmp.read(2)
                color888 = self.color(int.from_bytes(value, 'big'))
                outputImage.putpixel((int((i/2)%size[0]), int((i/2)//size[1])), color888)
            
            if not size == scaleTo:
                outputImage = outputImage.resize(scaleTo, Image.Resampling.NEAREST)
            tmp.close()

        return outputImage
    

    def save_image(self, inputPath, savePath):
        outputImage = self.convert_image(inputPath)
        outputImage.save(savePath)

    def export_selected(self, *_):
        self.export(self.selectedFile)
    

    def export(self, *_):
        format = self.formatBox.get()

        if self.modeBox.get() == self.exportModes["selected"]:
            filesToExport = [self.selectedFile]
        elif self.modeBox.get() == self.exportModes["all"]:
            filesToExport = self.loadedFiles
        else:
            raise ValueError("Unknown export mode")
        
        outputDirectory = askdirectory(title="Select a directory to export to")
        if outputDirectory == "":
            popup.ToastNotification(
                title="Operation cancelled",
                message="You did not select any directory.",
                duration=5000,
                icon="📁",
                alert=True,
                bootstyle=INFO
            ).show_toast()
            return
        
        if format in ["png", "bmp"]:
            for file in filesToExport:
                exportPath = outputDirectory + "/" + str(file).split("/")[-1][:-3] + format
                self.save_image(file, exportPath)
        elif format == "gif":
            exportPath = outputDirectory + "/" + (str(self.loadedFiles[0]).split("/")[-1][:-3]) + format

            frames = []
            
            for file in filesToExport:
                frames.append(self.convert_image(file))

            firstFrame = frames[0]
            firstFrame.save(
                exportPath,
                format="GIF",
                append_images=frames[1:],
                save_all=True,
                duration=50,
                loop=0
            )

        
if __name__ == "__main__":
    mainWindow = main_menu()
    mainWindow.mainloop()      