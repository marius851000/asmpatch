import tempfile
import os

KEEP_TEMPORARY_FOLDER = True
TEMPORARY_FOLDER_PATH = None

class tempory_folder:
    def __init__(self, debug_path):
        global TEMPORARY_FOLDER_PATH
        if KEEP_TEMPORARY_FOLDER and TEMPORARY_FOLDER_PATH == None:
            TEMPORARY_FOLDER_PATH = tempfile.mkdtemp()
            print("using the temporary folder {} .".format(TEMPORARY_FOLDER_PATH))

        if type(debug_path) == tuple:
            debug_path = os.path.join(debug_path[0], debug_path[1])

        if TEMPORARY_FOLDER_PATH != None:
            self.folder = os.path.join(TEMPORARY_FOLDER_PATH, debug_path)
            if os.path.isdir(self.folder):
                added_number = 0
                while True:
                    new_folder = os.path.join(self.folder, str(added_number))
                    if os.path.isdir(new_folder):
                        added_number += 1
                    else:
                        break
                print("WARNING: The temporary folder {} is already used elsewhere in the program. This is a bug. Will use {} instead.".format(self.folder, new_folder))
                self.folder = new_folder
            os.makedirs(self.folder, exist_ok = False)
        else:
            self.folder = tempfile.mkdtemp()
        self.files = []

    def register_file(self, file_name):
        """indicate that a file is added to the tempory folder file (either just now or later). Return the path of the file."""
        if file_name in self.files:
            raise BaseException("WARNING: the file name {} has already been registered for the tempory folder {}.".format(file_name, self.folder))
        self.files.append(file_name)
        return os.path.join(self.folder, file_name)

    def get_folder(self):
        return self.folder

    def clean(self):
        if KEEP_TEMPORARY_FOLDER:
            existing_file = os.listdir(self.folder)
            for file in self.files:
                if file in existing_file:
                    existing_file.remove(file)
                else:
                    print("WARNING: the file {} was registered for the temporary folder {}, but isn't in the list of existing files ({}).".format(file, self.folder, existing_file))
            if len(existing_file) != 0:
                print("WARNING: those files are not registered as temporary file: {} .".format(existing_file))
            return
        for file in self.files:
            os.remove(os.path.join(self.folder, file))
        os.rmdir(self.folder)
        self.folder = None

def write_file(file_path, content):
    f = open(file_path,"w")
    f.write(content)
    f.close()

def read_file(file_path):
    f = open(file_path, "r")
    c = f.read()
    f.close()
    return c

def split_line(line):
    splited = []
    new_part = True
    for chara in line:
        if chara == " " or chara == "\t":
            new_part = True
        else:
            if new_part:
                splited.append(chara)
                new_part = False
            else:
                splited[-1] += chara
    return splited
