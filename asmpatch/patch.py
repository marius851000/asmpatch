import os
import subprocess
from .parser import recreate_asm
from .map import parse_map

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

def generate_object(splited, executable_as, dir):
    # create tempory file
    # .asm
    assembly = recreate_asm(splited["section"], with_comment=False)
    tempory_assembly_path = os.path.join(dir, "assembly.asm")
    tempory_assembly_file = open(tempory_assembly_path, "w")
    tempory_assembly_file.write(assembly)
    tempory_assembly_file.close()

    # .o
    tempory_object_path = os.path.join(dir, "object.o")
    subprocess.run([executable_as, "-mregnames", "-m750cl", tempory_assembly_path, "-o", tempory_object_path])
    if not os.path.isfile(tempory_object_path):
        raise BaseException("failed to create the object file from {}".format(tempory_assembly_path))
    return tempory_object_path

def get_metadata_object(splited, object_path, executable_ld, end_offset, dir):
    start = splited["start"]
    start_at_end = start == "end"
    if start_at_end:
        start = end_offset

    # create empty .ld file
    empty_ld_path = os.path.join(dir, "empty.ld")
    empty_ld_file = open(empty_ld_path, "w")
    empty_ld_file.close()

    # create .map file
    tempory_map_path = os.path.join(dir, "map.map")
    subprocess.run([executable_ld, "-Ttext", start, "--no-demangle", "--oformat=binary", "-T", empty_ld_path, "-Map="+tempory_map_path, object_path])
    # read .map file
    tempory_map_file = open(tempory_map_path)
    map_content = tempory_map_file.read()
    tempory_map_file.close()

    map_data = parse_map(map_content)
    if start_at_end:
        map_data["new_end"] = hex(int(start, 16) + map_data["lenght"])
    else:
        map_data["new_end"] = start
    return map_data

def generate_binary_patch(object_path, globals, offset, executable_ld, dir):
    # create linker.ld file
    ld_path = os.path.join(dir, "linker.ld")
    ld_file = open(ld_path, "w")
    for g in globals:
        ld_file.write("{} = {};\n".format(g, globals[g]))
    ld_file.close()

    # generate the .bin file
    bin_path = os.path.join(dir, "bin.bin")
    subprocess.run([executable_ld, "-Ttext", offset, "--oformat=binary", "-T", ld_path, object_path, "-o", bin_path])

    # read the .bin file
    bin_file = open(bin_path, "rb")
    patch_bin = bin_file.read()
    bin_file.close()
    return patch_bin
