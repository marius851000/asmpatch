from .util import read_file, split_line

def read_linker_files(file_list):
    globals = {}

    if len(file_list) != 0:
        print("reading linker file(s)")
        for ld_file_path in file_list:
            file_content = read_file(ld_file_path)
            for line in file_content.split("\n"):
                splited = split_line(line)
                if len(splited) == 0:
                    continue
                name = splited[0]
                offset = int(splited[2], 16)
                globals[name] = offset

    return globals
