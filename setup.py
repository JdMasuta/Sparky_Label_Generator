# setup.py
import PyInstaller.__main__
import os

# Get the directory containing this script
base_path = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    'generate_tag_gui.py',  # your main script
    '--onefile',  # create a single executable
    '--windowed',  # prevent console window from appearing
    '--name=Label Generator',  # name of your executable
    '--icon=icon.ico',  # path to your icon file
    '--add-data=pdf_generator.py;.',  # include additional Python modules
    # '--noconsole',  # hide the console window
    '--clean',  # clean PyInstaller cache
    '--noconfirm',  # replace output directory without asking
])