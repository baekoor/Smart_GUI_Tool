Smart 3 Update File Creation Tool GUI - python 3.7+

OS independent GUI tool for version control on dash clusters for boats.
The program uses two binary data files, defines specific memory addresses for metadata, 
compresses using XZ and encrypts with AES-128-OFB to create a concatenated data file that can be uploaded to dash clusters

This can be run from terminal on linux with (python3.7 Gui.py), on windows with cmd (python Gui.py)
or via double clicking the file.

#########################################  NOTE FOR USE ON LINUX #######################################
# On linux based OS's be sure to run the commands from the main/resources/linux-xxx folders README's
# and place the output files in the resources folder(if asked in pop-up click replace). These need to be
# re-compiled on a new system and failing to do so will prevent the program from functioning properly.

**** REQUIRED PYTHON LIBRARIES ARE ****
PyQt5 - pip install pyqt5
Yaml - pip install pyyaml

Note: If you are having issues running this code, ensure that you are executing using python3.7 or higher
