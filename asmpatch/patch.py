import os
import subprocess
from .parser import recreate_asm
from .map import parse_map
from .util import tempory_folder, read_file, write_file

def split_part(parsed):
    splited = []
    actual_initial_position = None
    actual_section = []

    for part in parsed:
        category = part["category"]
        if category == "comment":
            continue
        # check for a new part
        if category == "command":
            if part["name"] == ".org":
                if len(part["parameter"]) != 1:
                    raise Exception("ASM: .org should have exactly one operand")
                if actual_section != []:
                    splited.append({
                        "start": actual_initial_position,
                        "section": actual_section
                    })
                actual_initial_position = part["parameter"][0]
                actual_section = []
                continue

        if actual_initial_position == None:
            raise Exception("ASM: the line {} appear before any .org argument".format(part))

        actual_section.append(part)

    if actual_section != []:
        splited.append({
            "start": actual_initial_position,
            "section": actual_section
        })
    return splited

def enumerate_global(parsed):
    globals = []
    for part in parsed:
        if part["category"] == "command":
            if part["name"] == ".global" or part["name"] == ".globl":
                if len(part["parameter"]) != 1:
                    raise Exception("ASM: .global should have exactly one operand")
                globals.append(part["parameter"][0])
    return globals

def generate_object(splited, executable_as, name, loop_number):
    dir = tempory_folder(("build_object", os.path.join(name, str(loop_number))))
    # create tempory file
    # .asm
    assembly = recreate_asm(splited["section"], with_comment=False)
    tempory_assembly_path = dir.register_file("assembly.asm")
    write_file(tempory_assembly_path, assembly)

    # .o
    tempory_object_path = dir.register_file("object.o")
    subprocess.run([executable_as, "-mregnames", "-m750cl", tempory_assembly_path, "-o", tempory_object_path])
    if not os.path.isfile(tempory_object_path):
        raise BaseException("failed to create the object file from {}".format(tempory_assembly_path))

    object_file = open(tempory_object_path, "rb")
    object_bin = object_file.read()
    object_file.close()
    dir.clean()
    return object_bin

def get_metadata_object(splited, object_bin, name, loop_nb, executable_ld, end_offset):
    start = splited["start"]
    start_at_end = start == "end"
    if start_at_end:
        start = end_offset

    dir = tempory_folder(("map_file", os.path.join(name, str(loop_nb))))
    # create empty .ld file
    empty_ld_path = dir.register_file("empty.ld")
    write_file(empty_ld_path, "")

    # create object.o file
    object_path = dir.register_file("object.o")
    object_file = open(object_path, "wb")
    object_file.write(object_bin)
    object_file.close()

    # create .map file
    tempory_map_path = dir.register_file("map.map")
    subprocess.run([
        executable_ld,
        "-Ttext", hex(start),
        "--no-demangle",
        "--oformat=binary",
        "-T", empty_ld_path,
        "-Map=" + tempory_map_path,
        object_path])
    # read .map file
    map_content = read_file(tempory_map_path)

    map_data = parse_map(map_content)
    map_data["correct_start"] = start
    if start_at_end:
        map_data["new_end"] = end_offset + map_data["lenght"]
    else:
        map_data["new_end"] = end_offset
    dir.clean()
    return map_data

def generate_binary_patch(object_bin, globals, offset, name, loop_nb, executable_ld):
    dir = tempory_folder(("binary_patch", os.path.join(name, str(loop_nb))))
    # create linker.ld file
    ld_path = dir.register_file("linker.ld")
    ld_file = open(ld_path, "w")
    for g in globals:
        ld_file.write("{} = {};\n".format(g, globals[g]))
    ld_file.close()

    # create the object.o file
    object_path = dir.register_file("object.o")
    object_file = open(object_path, "wb")
    object_file.write(object_bin)
    object_file.close()

    # generate the .bin file
    bin_path = dir.register_file("bin.bin")
    subprocess.run([
        executable_ld,
        "-Ttext", hex(offset),
        "--oformat=binary",
        "-T", ld_path,
        object_path,
        "-o", bin_path,
        "--no-demangle"])

    # read the .bin file
    bin_file = open(bin_path, "rb")
    patch_bin = bin_file.read()
    bin_file.close()
    dir.clean()
    return patch_bin
