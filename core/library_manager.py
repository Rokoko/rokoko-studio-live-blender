
import os
import bpy
import sys
import json
import shutil
import pkgutil
import pathlib
import platform
import ensurepip
import subprocess


class LibraryManager:
    os_name = platform.system()
    system_info = {
        "operating_system": os_name,
    }
    pip_is_updated = False

    def __init__(self, libs_main_dir: pathlib.Path):
        self.libs_main_dir = libs_main_dir
        self.libs_info_file = self.libs_main_dir / ".lib_info"

        python_ver_str = "".join([str(ver) for ver in sys.version_info[:2]])
        self.libs_dir = os.path.join(self.libs_main_dir, "python" + python_ver_str)

        # Set python path on older Blender versions
        try:
            self.python = bpy.app.binary_path_python
        except AttributeError:
            self.python = sys.executable

        self.check_libs_info()
        self._prepare_libraries()

    def _prepare_libraries(self):
        # Create main library directory
        if not os.path.isdir(self.libs_main_dir):
            os.mkdir(self.libs_main_dir)
        # Create python specific library directory
        if not os.path.isdir(self.libs_dir):
            os.mkdir(self.libs_dir)

        # Add the library path to the modules, so they can be loaded from the plugin
        if self.libs_dir not in sys.path:
            sys.path.append(self.libs_dir)

    def install_libraries(self, required):
        missing_after_install = []

        # Install missing libraries
        missing = [mod for mod in required if not pkgutil.find_loader(mod)]
        if missing:
            # Ensure and update pip
            self._update_pip()

            # Install the missing libraries into the library path
            print("Installing missing libraries:", missing)
            try:
                # command = [self.python, '-m', 'pip', 'install', f"--target={str(self.libs_dir)}", "--index-url=http://pypi.python.org/simple/", "--trusted-host=pypi.python.org", *missing]
                command = [self.python, '-m', 'pip', 'install', f"--target={str(self.libs_dir)}", *missing]
                subprocess.check_call(command, stdout=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                print("PIP Error:", e)
                print("Installing libraries failed.")
                if self.os_name != "Windows":
                    print("Retrying with sudo..")
                    # command = ["sudo", self.python, '-m', 'pip', 'install', f"--target={str(self.libs_dir)}", "--index-url=http://pypi.python.org/simple/", "--trusted-host=pypi.python.org", *missing]
                    command = ["sudo", self.python, '-m', 'pip', 'install', f"--target={str(self.libs_dir)}", *missing]
                    subprocess.call(command, stdout=subprocess.DEVNULL)
            finally:
                # Reset console color, because it could still be colored after running pip
                print('\033[39m')

            # Check if all library installations were successful
            missing_after_install = [mod for mod in required if not pkgutil.find_loader(mod)]
            installed_libs = [lib for lib in missing if lib not in missing_after_install]
            if missing_after_install:
                print("WARNING: Could not install the following libraries:", missing_after_install)
            if installed_libs:
                print("Successfully installed missing libraries:", installed_libs)

        # Create library info file after all libraries are installed to ensure everything is installed correctly
        self.create_libs_info()

        return missing_after_install

    def check_libs_info(self):
        if not os.path.isdir(self.libs_dir):
            return

        # If the library info file doesn't exist, delete the libs folder
        if not os.path.isfile(self.libs_info_file):
            print("Library info is missing, deleting library folder.")
            shutil.rmtree(self.libs_main_dir)
            return

        # Read data from info file
        current_data = self.system_info
        with open(self.libs_info_file, 'r', encoding="utf8") as file:
            loaded_data = json.load(file)

        # Compare info and delete libs folder if it doesn't match
        for key, val_current in current_data.items():
            val_loaded = loaded_data.get(key)
            if not val_loaded == val_current:
                print("Current info:", current_data)
                print("Loaded info: ", loaded_data)
                print("Library info is not matching, deleting library folder.")
                shutil.rmtree(self.libs_main_dir)
                return

    def create_libs_info(self):
        # If the path doesn't exist or the info file already exists, don't create it
        if not os.path.isdir(self.libs_dir) or os.path.isfile(self.libs_info_file):
            return

        # Write the current data to the info file
        with open(self.libs_info_file, 'w', encoding="utf8") as file:
            json.dump(self.system_info, file)

    def _update_pip(self):
        if self.pip_is_updated:
            return

        print("Ensuring pip")
        ensurepip.bootstrap()

        print("Updating pip")
        try:
            # subprocess.check_call([self.python, "-m", "pip", "install", "--upgrade", "--index-url=http://pypi.python.org/simple/", "--trusted-host=pypi.python.org", "pip"])
            subprocess.check_call([self.python, "-m", "pip", "install", "--upgrade", "pip"])
        except subprocess.CalledProcessError as e:
            print("PIP Error:", e)
            print("Updating pip failed.")
            if self.os_name != "Windows":
                print("Retrying with sudo..")
                # subprocess.call(["sudo", self.python, "-m", "pip", "install", "--upgrade", "--index-url=http://pypi.python.org/simple/", "--trusted-host=pypi.python.org", "pip"])
                subprocess.call(["sudo", self.python, "-m", "pip", "install", "--upgrade", "pip"])
        finally:
            # Reset console color, because it could still be colored after running pip
            print('\033[39m')

        self.pip_is_updated = True


# Setup library path in the Blender addons directory and start library manager
main_dir = pathlib.Path(os.path.dirname(__file__)).parent.parent
libs_dir = main_dir / "Rokoko Libraries"
lib_manager = LibraryManager(libs_dir)
