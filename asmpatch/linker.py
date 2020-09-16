from .util import read_file, split_line

def read_linker_files(file_list):
    '''read a *.ld file from the list of file_list, that is a list of path to ld file, in the form of a dict with key = offset (offset is an integer). key contained in later file/after the line overwrite the previous one.'''
    globals = {}

    if len(file_list) != 0:
        print("reading linker file(s)")
        for ld_file_path in file_list:
            file_content = read_file(ld_file_path)
            for line in file_content.split("\n"):
                splited = split_line(line)
                if len(splited) == 0:
                    continue
                if splited[1] != "=":
                    print("in the *.ld file, for the line \"{}\", the middle character is expected to be an \"=\"".format(line))
                name = splited[0]
                offset = int(splited[2], 16)
                globals[name] = offset

    return globals
