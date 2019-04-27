import sys,platform
from cx_Freeze import setup, Executable
import os

def getTargetName():
    myOS = platform.system()
    if myOS == 'Linux':
        return "3DP"
    elif myOS == 'Windows':
        return "3DP.exe"
    else:   
        return "3DP.dmg"


base = "Console"
if sys.platform == "win32":
    base = "Win32GUI"

if sys.platform == 'win64':
    base = "Win64GUI"
	
	# "includes":["Image_Converter.py","Serial_test.py","Ui_MainWindow.py","visualization.py"],
os.environ['TCL_LIBRARY'] = "C:\\Users\\Jimmy\\Anaconda3\\tcl\\tcl8.6"
os.environ['TK_LIBRARY'] = "C:\\Users\\Jimmy\\Anaconda3\\tcl\\tk8.6"
exe = Executable(script = "Main_PROGRAM.py", base=base, targetName = getTargetName())

build_exe_options = {"packages": ["re","time","win32com.client","os","PyQt5", "sys","matplotlib","numpy","subprocess","xml","serial","time","functools"],
                      "namespace_packages":["mpl_toolkits.mplot3d"],
					  "includes": ["matplotlib.backends.backend_qt5agg"],
					 "include_files":[os.path.join(r"C:\Users\Jimmy\Anaconda3", "DLLs", "tk86t.dll"),
						os.path.join(r"C:\Users\Jimmy\Anaconda3", "DLLs", "tcl86t.dll"),
						os.path.join(r"C:\Users\Jimmy\Anaconda3\Library\plugins","platforms"), "Serial_test.py","Image_Converter.py","visualization.py","Ui_MainWindow.py","mjp-multijet-printing.jpg"]
                     }

setup(  name = "3DP",
        version = "1.0",
        description = "3DP GUI Application!",
        options = {"build_exe": build_exe_options},
        executables = [exe])