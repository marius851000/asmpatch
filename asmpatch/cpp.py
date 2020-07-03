import subprocess
import os
from .util import tempory_folder, read_file, write_file

def cpp_to_assembly(cpp_code, gpp):
    tmp_dir = tempory_folder()

    gpp_flags = [
        "-S",
        "-fno-asynchronous-unwind-tables",
        "-fno-dwarf2-cfi-asm",
        "-O3"
    ]
    # generate code.cpp
    code_cpp_path = tmp_dir.register_file("code.cpp")
    write_file(code_cpp_path, cpp_code)

    # generate code.asm
    code_asm_path = tmp_dir.register_file("code.asm")

    # build the arguments
    parameter = [gpp]
    parameter.extend(gpp_flags)
    parameter.append(code_cpp_path)
    parameter.extend(["-o", code_asm_path])

    subprocess.check_call(parameter)
    result_asm = read_file(code_asm_path)

    tmp_dir.clean()

    return result_asm
