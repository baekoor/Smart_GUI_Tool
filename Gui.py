import os
import sys
import subprocess
import yaml
import time
from PyQt5 import QtWidgets as qtw
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDragMoveEvent, QDropEvent, QFont

OUTPUTFILENAME = ""
BINLOCS = []
INSTALLLOC = []
IVY = ""
VERSION = ""
SIGMA3 = "SIGMA3=P0,P1"
VERBOSE = False
FILETYPE = "UPDATE"
key = '' #key for encryption

#Validates the resource and project hex addresses
def check_hex_format(string):
    valid_chars = set('abcdefABCDEF')
    if all(char in valid_chars for char in string):
        return True
    else:
        return False

#Function that handles cleanup of extra files if Keepfiles is not checked
def cleanup():
    for filename in BINLOCS:
        if os.path.isfile("{}.xz".format(filename)):
            os.remove("{}.xz".format(filename))
        if os.path.isfile("{}.xz.aes-128".format(filename)):
            os.remove("{}.xz.aes-128".format(filename))

    if os.path.isfile("payload.bin"):
        os.remove("payload.bin")
    if os.path.isfile("metadata.txt"):
        os.remove("metadata.txt")
    if os.path.isfile("outMetadata.txt"):
        os.remove("outMetadata.txt")
    if os.path.isfile("outMetadata.txt.aes-128"):
        os.remove("outMetadata.txt.aes-128")

def hw_id(self): #Used to compile HW checkbox info for console command
        HW = "-"
        if self.c1.isChecked():
            HW = 0
        elif self.c2.isChecked():
            HW = 1
        elif self.c3.isChecked():
            HW = 2
        elif self.c4.isChecked():
            HW = 3

        return HW

def refreshIV(): #returns 32 char list as string from shared library of c file
    if os.name == "posix":
        res = subprocess.run(['resources/IV'], capture_output=True, text=True)
        IVY = res.stdout.strip()
    elif os.name == "nt":
        res = subprocess.run([r"resources/IV.exe"], capture_output=True, text=True)
        IVY = res.stdout.strip()
    return IVY

class Button(qtw.QPushButton): #Button class for .bin files, drag and drop as well as browse
    def __init__(self, text):
        super().__init__(text)
        self.setAcceptDrops(True)
        self.clicked.connect(self.browse_files)

    def dragEnterEvent(self, event: QDragEnterEvent): #Called when drag is in progress and cursor enters the box
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event: QDragMoveEvent): #Identifies if the button is being interacted with by the user
        event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent): #Allows for files to be dropped into the button saving the file path
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.setText(file_path)

    def browse_files(self): #Allows for user to browse files
        file_dialog = qtw.QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Browse Files')
        if file_path:
            self.setText(file_path) #Sets file path to open from if available on button


class LineEditMem(qtw.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orig_text = self.text()
        self.setPlaceholderText("8 Digit hexadecimal address") #Establish Placeholder string
        self.setFocusPolicy(Qt.ClickFocus)
       
    def focusOutEvent(self, event): #Focus out call from QLineEditMem box, prevents more than 8 char returns
        super().focusOutEvent(event)
        if self.text().strip() == "": #If box is left empty, set back to original text
            self.setText(self.orig_text)
        else:
            return
                   
    def focusInEvent(self, event): #Focus in call for QLineEditMem box, deletes text in box and sets to placeholder
        super().focusInEvent(event)
        if self.text() == self.orig_text:
            self.clear()
        else:
            return


class LineEdit(qtw.QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.orig_text = self.text()
        if self.orig_text == "File Name":
            self.setPlaceholderText("Enter File Name") #Sets placeholer to "Enter File Name"
        else:
            self.setPlaceholderText("Version # 0.0.X") #Sets placeholder to "Enter Vesion Number"
       
    def focusOutEvent(self, event): #QLineedit focus out event which resets empty boxes to their original type
        super().focusOutEvent(event)
        if self.text().strip() == "":
            self.setText(self.orig_text)
        else:
            return
                   
    def focusInEvent(self, event): #QLineedit focus in event which changes the box to placeholder
        super().focusInEvent(event)
        if self.text() == self.orig_text:
            self.clear()
        else:
            return


class Window(qtw.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Smart 3 Update File Creation Tool") #Name of Window
        self.initUI()

    def initUI(self):
        layout = qtw.QGridLayout(self) #Creates the primary layout in the form of grid, everything is inside here

        self.iv = qtw.QLabel(refreshIV()) #Creates the IV object that will be later updated on refresh
        self.iv.setFont(QFont('Courier New', 11)) #Sets IV font to monospace type font to prevent size from changing on refresh

        self.rF = qtw.QPushButton(self)
        self.rF.setStyleSheet("QPushButton { border-image: url(resources/refresh.jpeg); }") #Applies refresh icon image to button as background
        self.rF.setMaximumSize(280, 24)
        self.rF.clicked.connect(self.rF_clicked) #Connect refresh on click to rF_clicked function

        self.fn = LineEdit("File Name") #File Name LineEdit
        self.v = LineEdit("Version #") #Version Number LineEdit
        self.pB = Button("Project .bin") #Project .bin path Button
        self.pB.setMaximumSize(350, 24)
        self.pBA = LineEditMem("P.bin Address") # Project .bin address, hexidecimal address of LineEditMem type
        self.rB = Button("Resources .bin") #Resources .bin path Button
        self.rBA = LineEditMem("R.bin Address") #Resources .bin address, hexidecimal address of LineEditMem type
        self.rB.setMaximumSize(350, 24)

        B = qtw.QPushButton("BUILD")
        B.clicked.connect(self.B_clicked) #Links Build button to B_clicked function
        C = qtw.QPushButton("CLOSE")
        C.clicked.connect(self.C_clicked) #Link Close button to C_clicked function

        layout.addWidget(self.iv, 0, 0) #Assigning the top 8 widgets
        layout.addWidget(self.rF, 0, 1)
        layout.addWidget(self.fn, 1, 0)
        layout.addWidget(self.v, 1, 1)
        layout.addWidget(self.pB, 2, 0)
        layout.addWidget(self.pBA, 2, 1)
        layout.addWidget(self.rB, 3, 0)
        layout.addWidget(self.rBA, 3, 1)
        
        self.c1 = qtw.QCheckBox("4.2\"")
        self.c2 = qtw.QCheckBox("7\"")
        self.c3 = qtw.QCheckBox("8\"")
        self.c4 = qtw.QCheckBox("10.6\"")
        self.c1.stateChanged.connect(self.checkbox_change)
        self.c2.stateChanged.connect(self.checkbox_change)
        self.c3.stateChanged.connect(self.checkbox_change)
        self.c4.stateChanged.connect(self.checkbox_change)

        self.c_l = qtw.QHBoxLayout() #Horizontal Layout for HW specification checkboxes
        self.c_l.addWidget(self.c1)
        self.c_l.addWidget(self.c2)
        self.c_l.addWidget(self.c3)
        self.c_l.addWidget(self.c4)

        vbl = qtw.QHBoxLayout() #Horizontal Layout for verbose option
        self.verb = qtw.QCheckBox("Verbose")
        self.keep = qtw.QCheckBox("Keep Files")
        self.keep.stateChanged.connect(self.keep_click)
        self.verb.stateChanged.connect(self.verbose)

        vbl.addWidget(self.verb)
        vbl.addWidget(self.keep)

        layout.addLayout(self.c_l, 4, 0, 1, 2) #Adds HW spec horizontal layout
        layout.addLayout(vbl, 5, 0, 1, 2) #Adds verbose option layout
        layout.addWidget(B, 6, 0)
        layout.addWidget(C, 6, 1)

        self.setLayout(layout)
        self.setGeometry(600, 500, 500, 225) #Sets screen location for opening, as well as width and height of window
        with open('config.yaml', 'r') as file:
            config = yaml.safe_load(file)
            
        if config['metadata']['file_name'] != None:
            self.fn.setText(config['metadata']['file_name'])
        if config['cryptography']['IV'] != None:
            global IVY
            self.iv.setText(config['cryptography']['IV'])
        if config['cryptography']['key'] != None:
            global key
            key = config['cryptography']['key']
        if config['metadata']['version'] != None:
            self.v.setText(config['metadata']['version'])
        if config['metadata']['Proj_bin_addr'] != None:
            self.pBA.setText(config['metadata']['Proj_bin_addr'])
        if config['metadata']['Resources_bin_addr'] != None:
            self.rBA.setText(config['metadata']['Resources_bin_addr'])
        if config['filepaths']['Proj_bin'] != None:
            self.pB.setText(config['filepaths']['Proj_bin'])
        if config['filepaths']['Resources_bin'] != None:   
            self.rB.setText(config['filepaths']['Proj_bin'])
    
    def rF_clicked(self): #called when refresh button is clicked, returns updated IV to label
        self.iv.setText(refreshIV())

    def B_clicked(self): #Build button, compiles relevent information and returns the appropriate command based on the data
        if self.fn.text() == "File Name" or self.fn.text() == "Enter File Name": #Ensures valid file name before compilation
            raise ValueError("Must enter a valid file name")
        if check_hex_format(self.pBA.text()) or check_hex_format(self.rBA.text()):
            raise ValueError("Must enter valid HEX address")
        OUTPUTFILENAME = self.fn.text()
        BINLOCS.append(self.pB.text())
        BINLOCS.append(self.rB.text())

        INSTALLLOC.append(self.pBA.text())
        INSTALLLOC.append(self.rBA.text())
        
        IVY = self.iv.text() #Initialization Vector(IV) - Randomly generated from execs\IV.exe
        VERSION = self.formatV()
        hw_id(self)
        md5 = []
        partitions = [""] * 5
        partitionFile = [""] * 2  # Initialize partitionFile array with empty strings
        pSize = [0] * 5
        pCRC32 = [0] * 5
        pProcSize = [0] * 5
        pProcCRC32 = [0] * 5
        pOffset = [0] * 5


        if os.name == "posix":
            CRC32PROG = 'crc32'
        elif os.name == "nt":
            CRC32PROG = r"resources\crc32.exe"
        else:
            print("Unknown operating system")

        for i, filename in enumerate(BINLOCS):
            if os.path.isfile(filename):
                if self.verb.isChecked():
                    print("process", filename)
            else:
                continue
            
            if not INSTALLLOC[i]:
                print("Partition needs an install location")
                cleanup()
                exit(2)
            
            if os.path.isfile(filename + ".xz"):
                os.remove(filename + ".xz")
            if os.path.isfile(filename + ".xz.aes-128"):
                os.remove(filename + ".xz.aes-128")
            
            if os.name == "posix":
                pCRC32[i] = subprocess.check_output([CRC32PROG, filename]).decode().strip()
            elif os.name == "nt":
                pCRC32[i] = subprocess.check_output([CRC32PROG, filename]).decode().strip()
            
            temp = os.stat(filename)
            pSize[i] = temp.st_size
            
            if os.name == "posix":
                subprocess.run(["xz", "-z", "-0", "-k", filename])
                subprocess.run(["openssl", "enc", "-nopad", "-aes-128-ofb", "-nosalt", "-d", "-in", filename + ".xz", "-K", key, "-iv", IVY, "-out", filename + ".xz.aes-128"])
            elif os.name == "nt":
                subprocess.run([r"resources\xz.exe", "-z", "-0", "-k", filename])
                subprocess.run(["resources\AES-128-OFB.exe", IVY, key, filename + ".xz", filename + ".xz.aes-128"])
            else:
                print("Unknown OS")
                cleanup()
                exit(2)
            
            partitionFile[i] = filename + ".xz.aes-128"
            if os.name == "posix":
                pProcCRC32[i] = subprocess.check_output([CRC32PROG, partitionFile[i]]).decode().strip()

            elif os.name == "nt":
                pProcCRC32[i] = subprocess.check_output([CRC32PROG, partitionFile[i]]).decode().strip()
            
            temp = os.stat(partitionFile[i])
            pProcSize[i] = temp.st_size
            
            OFFSET = 0
            for j in range(i):
                OFFSET += pProcSize[j]
            pOffset[i] = OFFSET
            
            partitions[i] = "P{}={},{},{},{},{},{}".format(i, pOffset[i], pProcSize[i], pProcCRC32[i], INSTALLLOC[i], pSize[i], pCRC32[i])
            md5.append(partitions[i])
            if self.verb.isChecked():
                print("{} = {}".format(partitionFile[i], partitions[i]))

        # Check if "payload.bin" file exists and remove it if it does
        if os.path.isfile("payload.bin"):
            os.remove("payload.bin")

        # Concatenates contents of partition files into "payload.bin"
        for p in partitionFile:
            with open(p, "rb") as file:
                data = file.read()
            with open("payload.bin", "ab+") as file:
                file.write(data)

        if os.name == "posix":
            crc32_process = subprocess.Popen([CRC32PROG, "payload.bin"], stdout=subprocess.PIPE)
        elif os.name == "nt":
            crc32_process = subprocess.Popen([CRC32PROG, "payload.bin"], stdout=subprocess.PIPE)
        payloadCRC32 = crc32_process.communicate()[0].decode().strip()
        payloadSize = os.stat("payload.bin").st_size
        
        metadata_content = f"TYPE={FILETYPE};VERSION={VERSION};HW={hw_id(self)};{SIGMA3}"
        with open("metadata.txt", 'w') as metadata_file:
            metadata_file.write(metadata_content + ";")
            metadata_file.write(md5[0] + ";" + md5[1])
            metadata_file.write(f";CRC32={payloadCRC32};SIZE={payloadSize}")

        if os.name == "posix":
            subprocess.run(['resources/MT', "metadata.txt", "outMetadata.txt"])
            subprocess.run(["openssl", "enc", "-nopad", "-aes-128-ofb", "-nosalt", "-d", "-in", "outMetadata.txt", "-K", "cec8f5edfd7feef15f4e55652dc213ca", "-iv", IVY, "-out", "outMetadata.txt.aes-128"])
        elif os.name == "nt":
            subprocess.run([r"resources\MT.exe", "metadata.txt", "outMetadata.txt"])
            subprocess.run([r"resources\AES-128-OFB.exe", IVY, "cec8f5edfd7feef15f4e55652dc213ca", "outMetadata.txt", "outMetadata.txt.aes-128"])
        
        #Creates final output file with .xz.aes-128 type
        with open(OUTPUTFILENAME + ".bin", "ab") as update_file:
            byte = bytes.fromhex(IVY)
            update_file.write(byte)
            #Writes compressed encrypted metadata to output file
            with open("outMetadata.txt.aes-128", "rb") as metadata_file:
                update_file.write(metadata_file.read())
            #Writes compressed and encrypted partition data to output file
            with open("payload.bin", "rb") as payload_file:
                update_file.write(payload_file.read())
        print("IV USED: " + IVY)
        
        if not self.keep.isChecked():
            cleanup()
    
    def C_clicked(self): #Action on "CLOSE" button press, exits application
        app.exit()
    
    def check_checked(self):
        if self.c1.isChecked() or self.c2.isChecked() or self.c3.isChecked() or self.c4.isChecked():
            if not self.c1.isChecked():
                self.c1.setEnabled(False)
            if not self.c2.isChecked():
                self.c2.setEnabled(False)
            if not self.c3.isChecked():
                self.c3.setEnabled(False)
            if not self.c4.isChecked():
                self.c4.setEnabled(False)
        else:
            if not self.c1.isEnabled():
                self.c1.setEnabled(True)
            if not self.c2.isEnabled():
                self.c2.setEnabled(True)
            if not self.c3.isEnabled():
                self.c3.setEnabled(True)
            if not self.c4.isEnabled():
                self.c4.setEnabled(True)
        

    def checkbox_change(self, state): #Change Hardware checkbox's on/off
        cb = self.sender()
        cb_n = cb.text()
        checked = state == Qt.Checked
        self.check_checked()

    def verbose(self, state): #Changes verbose textbox on/off
        cb = self.sender()
        cb_n = cb.text()
        checked = state == Qt.Checked

    def keep_click(self, state): #Changes verbose textbox on/off
        cb = self.sender()
        cb_n = cb.text()
        checked = state == Qt.Checked

    def formatV(self): #Function that adds .0.0 in the case of a single number input
        if self.v.text().isalpha():
            raise ValueError("Version number cannot contain characters")
        if len(self.v.text()) == 1:
            ot = self.v.text()
            form = ot + ".0.0"
            return form
        return self.v.text()
        
if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec_() 