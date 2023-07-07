import sys
from cx_Freeze import setup, Executable
build_exe_options = {"packages": ["os"], "excludes": [], "includes":[]}

bdist_msi_options = {
    'upgrade_code': '{LawyerAssistant}',
    'add_to_path': False,
    'initial_target_dir': r'[ProgramFilesFolder]\%s\%s' % ("Eclipse","sol"),
    }
base = None
if sys.platform == "win32":
    base = "Win32GUI"
setup(  name = "Eclipse",
      version = "0.1.0",
      description = "Ecplise",
      author = "Jesus Daniel Lopez Jimenez",
      options = {"build_exe": build_exe_options,'bdist_msi': bdist_msi_options,"build_exe": {"include_files":["Interfaz","Config","Correo.pyw"]}},
      executables = [Executable("Main.pyw",shortcutName = "Eclipse" , shortcutDir="DesktopFolder",base=base)])
