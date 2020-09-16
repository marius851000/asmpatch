import tempfile
import os

class TemporyFolderBuilder:
    def __init__(self):
        self.keep_folder = False
        self.general_tempory_folder_path = None

    def set_keep_folder(self, keep_folder):
        assert isinstance(keep_folder, bool)
        self.keep_folder = keep_folder
        if keep_folder:
            if self.general_tempory_folder_path == None:
                self.general_tempory_folder_path = tempfile.mkdtemp()
            print("using the temporary folder {}".format(self.general_tempory_folder_path))

    def build_tempory_folder(self, debug_path):
        return TemporyFolder(
            debug_path,
            self.keep_folder,
            self.general_tempory_folder_path
        )

class TemporyFolder:
    def __init__(self, debug_path, keep_folder = False, general_tempory_folder_path = None):
        if type(debug_path) == tuple:
            absolute_path_of_parameter = os.path.abspath(debug_path[1])
            if absolute_path_of_parameter[1] == ":": # windows like, start with {letter}:/... , we just want {letter}/...
                debug_path = os.path.join(debug_path[0], absolute_path_of_parameter[0]+absolute_path_of_parameter[2:])
            else:
                debug_path = os.path.join(debug_path[0], absolute_path_of_parameter[1:])

        if general_tempory_folder_path != None:
            self.folder = os.path.join(general_tempory_folder_path, debug_path)
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
        self.keep_folder = keep_folder

    def register_file(self, file_name):
        """indicate that a file is added to the tempory folder file (either just now or later). Return the path of the file."""
        if file_name in self.files:
            raise BaseException("WARNING: the file name {} has already been registered for the tempory folder {}.".format(file_name, self.folder))
        self.files.append(file_name)
        return os.path.join(self.folder, file_name)

    def get_folder(self):
        return self.folder

    def clean(self):
        if self.keep_folder:
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


def parse_hex_to_int(nb_str):
    if len(nb_str) >= 2:
        if nb_str[0:1] == "0x":
            nb_str = nb_str[2:]
    return int(nb_str, 16)
