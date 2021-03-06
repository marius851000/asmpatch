import subprocess
import os
from .util import read_file, write_file

def cpp_to_assembly(cpp_code, source_file, gpp, tmp_builder):
    '''
    tranform the cpp code contained in the str in sourec_file to a String that contain the generated assembly code
    '''
    tmp_dir = tmp_builder.build_tempory_folder(("cpp_to_asm", source_file))

    gpp_flags = [
        "-S",
        "-fno-asynchronous-unwind-tables",
        "-fno-dwarf2-cfi-asm",
        "-O3",
        "-fverbose-asm",
        "-I" + os.path.dirname(source_file)
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
