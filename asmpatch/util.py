import tempfile
import os

class tempory_folder:
    def __init__(self):
        self.folder = tempfile.mkdtemp()
        self.files = []

    def register_file(self, file_name):
        """indicate that a file is added to the tempory folder file (either just now or later). Return the path of the file."""
        if file_name in self.files:
            raise BaseException("the file name {} has already been registered for the tempory folder {}.".format(file_name, self.folder))
        self.files.append(file_name)
        return os.path.join(self.folder, file_name)

    def clean(self):
        for file in self.files:
            os.remove(os.path.join(self.folder, file))
        os.rmdir(self.folder)
        self.folder = "this tempory folder was removed (cleaned) by the program"

def write_file(file_path, content):
    f = open(file_path,"w")
    f.write(content)
    f.close()

def read_file(file_path):
    f = open(file_path, "r")
    c = f.read()
    f.close()
    return c
