# This script converts a binary file containing 16-bit color values (RGB565) that is generated when taking a screenshot
# into a binary file with 24-bit RGB values. This binary file is then converted into a bmp image using the microbmp library.

import ttkbootstrap as ttk
import ttkbootstrap.toast as popup
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.tooltip import ToolTip

from tkinter.filedialog import askdirectory

from microbmp import MicroBMP
from PIL import Image

import os


class main_menu(ttk.Window):
    def __init__(self):
        # Initialize the main window and set the title, theme and minimal size
        super().__init__("Screenshot export", "darkly")
        self.minsize(300, 200)

        # Set up the default theme and style font
        self.defaultFont = "Consolas"
        self.style.configure(".", font=f"{self.defaultFont} 9")

        self.sourceDirectory = ""
        self.foundFiles = []

        self.init_GUI()


    def init_GUI(self):
        self.init_top_menu()
        self.init_shortcuts()
        self.init_main_GUI()


    def init_main_GUI(self):
        # These frames will only be shown once a directory is selected
        self.leftFrame = ttk.Frame(self, padding=10)
        self.leftFrame.pack(anchor=NE, fill=NONE, side=LEFT, expand=False)
        self.rightFrame = ttk.Frame(self, padding=10)

        self.operationFrame = ttk.LabelFrame(self.leftFrame, text="Select an operation to perform:", padding = 10)
        self.operationFrame.pack(fill=BOTH, side=LEFT, expand=False)

        self.exportSelectedButton = ttk.Button(
            self.operationFrame, 
            text="Export just the selected image",
            style="primary.TButton" 
            """ command=pass """
            )
        self.exportSelectedButton.pack(fill=NONE, side=TOP, expand=False, pady=10)

        self.exportAllButton = ttk.Button(
            self.operationFrame, 
            text="Export all images from\nthe selected directory",
            style="primary.TButton" 
            """ command=pass """
            )
        self.exportAllButton.pack(fill=NONE, side=TOP, expand=False, pady=10)

        self.createGIFButton = ttk.Button(
            self.operationFrame, 
            text="Export all images from the\nselected directory as a GIF",
            style="primary.TButton" 
            """ command=pass """
        )
        self.createGIFButton.pack(fill=NONE, side=TOP, expand=False, pady=10)
        

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
        self.foundFiles = []

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


    def load_directory(self):
        for file in os.listdir(self.sourceDirectory):
            if os.path.isfile(self.sourceDirectory + "/" + file) and str(file).endswith(".bin"):
                self.foundFiles.append(self.sourceDirectory + "/" + file)

        if len(self.foundFiles) > 0:
            popup.ToastNotification(
                title=f"Success",
                message=f"Successfully found {len(self.foundFiles)} supported files.",
                duration=5000,
                icon="✅",
                bootstyle=SUCCESS
            ).show_toast()
        else:
            popup.ToastNotification(
                    title=f"Operation cancelled",
                    message=f"There were no supported files in the selected directory.",
                    duration=5000,
                    icon="❌",
                    bootstyle=WARNING
            ).show_toast()
       

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
    

if __name__ == "__main__":
    mainWindow = main_menu()
    mainWindow.mainloop()


# outputImage = MicroBMP(240, 240, 24)

# with open(inputFile, 'rb') as tmp:
#     for i in range(0, len(tmp.read()), 2):
#         tmp.seek(i) 
#         value = tmp.read(2)
#         color888 = color(int.from_bytes(value, 'big'))
#         outputImage[int((i/2)%240), int((i/2)//240)] = color888
#     tmp.close()

# outputImage.save(outputFile)          