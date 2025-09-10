# This is an experimental tool to livestream the display from a GamePico

import ttkbootstrap as ttk
import ttkbootstrap.toast as popup
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox

import numpy as np

import time

from typing import TypedDict

from tkinter.filedialog import askdirectory

from PIL import Image, ImageTk

import sys
import glob
import serial

class HeaderData(TypedDict):
    version: int
    headerLength: int
    width: int
    height: int
    id: int
    frameTime: int
    gzip: bool
    gzip_wbits: int


class main_window(ttk.Window):
    def __init__(self):
        # Initialize the main window and set the title, theme and minimal size
        super().__init__("Live screen stream", "darkly")
        self.minsize(600, 500)

        # Set up the default theme and style font
        self.defaultFont = "Consolas"
        self.style.configure(".", font=f"{self.defaultFont} 9")


        self.init_GUI()

        self.after(10, self.check_data_available)


    def init_GUI(self):
        self.init_top_menu()
        self.init_main_GUI()
        self.show_GUI()


    def init_main_GUI(self):
        # These frames will only be shown once a directory is selected
        self.leftFrame = ttk.Frame(self, padding=10)
        self.rightFrame = ttk.Frame(self, padding=10)

        self.operationFrame = ttk.LabelFrame(self.leftFrame, text="Select an operation to perform:", padding = 10)
        self.operationFrame.pack(fill=BOTH, side=LEFT, expand=False)

        self.displayFrame = ttk.LabelFrame(self.rightFrame, text="Received stream:", padding=10)
        self.displayFrame.pack(fill=BOTH, side=LEFT, expand=False)


        self.portFrame = ttk.Frame(self.operationFrame)
        self.portFrame.pack(fill=X, side=TOP, expand=False)
        self.portLabel = ttk.Label(self.portFrame, text="Pico port: ")
        self.portLabel.pack(fill=X, side=LEFT, expand=True)

        self.availablePorts = self.list_serial_ports()

        self.portBox = ttk.Combobox(self.portFrame, values=self.availablePorts, state=READONLY)
        self.portBox.pack(fill=X, side=RIGHT, expand=True)
        try:
            self.portBox.set(self.availablePorts[0])
            self.init_serial_port()
        except IndexError:
            pass

        self.portBox.bind("<<ComboboxSelected>>", self.init_serial_port)

        self.imageLabel = ttk.Label(self.displayFrame)
        self.imageLabel.pack(anchor=CENTER, fill=None, side=TOP, expand=True, pady=10)


    def init_serial_port(self, *_):
        if not self.portBox.get() == "":
            self.serialPort = serial.Serial(self.portBox.get(), 115200, timeout=0.5)


    def show_GUI(self):
        self.leftFrame.pack(anchor=NE, fill=NONE, side=LEFT, expand=False)
        self.rightFrame.pack(anchor=NW, fill=NONE, side=RIGHT, expand=False)

    def hide_GUI(self):
        self.leftFrame.pack_forget()
        self.rightFrame.pack_forget()
        

    def init_top_menu(self):
        pass

    
    def update_image_frame(self):
        self.currentFrame = ImageTk.PhotoImage(self.convertedImage)
        self.imageLabel.configure(image=self.currentFrame)
        self.update()

    
    def check_data_available(self):
        try:
            self.serialPort.writelines(["ready\n".encode("utf-8")])
            if self.serialPort.in_waiting > 0:
                self.serialPort.read(2)
                self.receive_image()
            self.after(40, self.check_data_available)
        except AttributeError:
            self.availablePorts = self.list_serial_ports()
            self.portBox.configure(values=self.availablePorts)

            self.init_serial_port()

            try:
                self.portBox.set(self.availablePorts[0])
            except IndexError:
                pass
        
            self.after(2000, self.check_data_available)
        except serial.SerialException:
            self.serialPort = 0
            self.availablePorts = self.list_serial_ports()
            self.portBox.configure(values=self.availablePorts)

            try:
                self.portBox.set(self.availablePorts[0])
            except IndexError:
                self.portBox.set("")
        
            self.after(2000, self.check_data_available)


    @staticmethod
    def list_serial_ports():
        # Source of this code: https://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python
        """ Lists serial port names

            :raises EnvironmentError:
                On unsupported or unknown platforms
            :returns:
                A list of the serial ports available on the system
        """
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError):
                pass
        return result
       

    @staticmethod
    def color_array_convert(values565:np.ndarray) -> np.ndarray:
        """ 
        Converts the 16-bit color format to the 24-bit RGB format.
        Arguments:
            values565 (ndarray): ndarray of shape (H, W) or flat, dtype=uint16
        
        Returns:
            ndarray: of shape (H, W, 3), dtype=uint8
        """
        r5 = (values565 >> 11) & 0x1F
        g6 = (values565 >> 5) & 0x3F
        b5 = values565 & 0x1F

        # Convert to 8-bit (0–255) by scaling:
        r8 = ((r5 * 255) // 31).astype(np.uint8)
        g8 = ((g6 * 255) // 63).astype(np.uint8)
        b8 = ((b5 * 255) // 31).astype(np.uint8)

        return np.stack((r8, g8, b8), axis=-1)


    def receive_image(self, scaleFactor:int = 3):
        width = 240
        height = 240
        packetCount = 16
        timeoutMs = 500

        outputImage = Image.new("RGB", (width, height))

        print("Receiving data... ", end="")
        startTime = time.time_ns()

        rawData = bytearray()

        self.serialPort.writelines(["continue\n".encode("utf-8")])

        while len(rawData) != width*height*2:
            packet = self.serialPort.read(width*height*2//packetCount)
            if len(packet) == width*height*2//packetCount:
                rawData += packet
                self.serialPort.writelines(["continue\n".encode("utf-8")])
            else:
                self.serialPort.writelines(["retry\n".encode("utf-8")])

            if (time.time_ns() - startTime)//10000000 > timeoutMs:
                print("Request timeout!")
                return
    
        self.serialPort.writelines(["end\n".encode("utf-8")])

        print(f"elapsed {(time.time_ns() - startTime)//1000/1000} ms")

        print(f"Converting image, ", end="")
        startTime = time.time_ns()
        outputImage = self.convert_image(rawData, width, height)
        print(f"elapsed {(time.time_ns() - startTime)//1000/1000} ms")

        self.convertedImage = outputImage.resize((width*scaleFactor, height*scaleFactor), Image.Resampling.NEAREST)

        self.update_image_frame()

    
    def convert_image(self, raw_data, width, height):
        # Convert raw RGB565 data from a bytearray to a NumPy array
        image_data_565 = np.frombuffer(raw_data, dtype='>u2').reshape((height, width))

        # Convert the RGB565 array to RGB888 array
        rgb888_data = self.color_array_convert(image_data_565)

        # Create the image using Pillow
        img = Image.fromarray(rgb888_data, 'RGB')

        return img

        
if __name__ == "__main__":
    mainWindow = main_window()
    mainWindow.mainloop()      