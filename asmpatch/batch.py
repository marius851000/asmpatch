import struct
import yaml
import os
from .parser import parse_asm
from .patch import split_part, generate_object, get_metadata_object, generate_binary_patch
from .util import read_file
from .linker import read_linker_files

#TODO: use and abuse of map reduce
def batchpatch(
    gas_path,
    gld_path,
    gpp_path,
    end_offset,
    input_name,
    linker_files = [],
    out_prefix = "",
    out_suffix = "_diff.txt",
    input_prefix = "",
    input_suffix = ".asm"
):

    globals = read_linker_files(linker_files)

    input_path = []
    for name in input_name:
        input_path.append(input_prefix + name + input_suffix)

    splited = []
    print("reading/splitting the different function")
    for file_path in input_path:
        content = read_file(file_path)
        dir_path = os.path.dirname(file_path)
        parsed = parse_asm(content, dir_path, gpp_path)
        splited.append(split_part(parsed))

    # generate object file
    print("generating the object file")
    objects = []
    for (patch, name) in zip(splited, input_name):
        actual_object = []
        loop_counter = 0
        for section in patch:
            actual_object.append({
                "object_bin": generate_object(section, gas_path, name, loop_counter),
                "data": section
            })
            start = actual_object[-1]["data"]["start"]
            if start in globals:
                actual_object[-1]["data"]["start"] = globals[start]
            elif isinstance(start, str) and start != "end":
                if len(start) >= 2:
                    if start[0:1] == "0x":
                        start = start[2:]
                actual_object[-1]["data"]["start"] = int(start, 16)

            loop_counter += 1
        objects.append(actual_object)

    actual_end_offset = end_offset

    # generate and read map file. Embed true offset position, and global
    # TODO: check and merge overwrite
    print("generating map file (metadata) (undefined reference can be ignored)")
    objects_pass_two = []
    for (patch, name) in zip(objects, input_name):
        objects_pass_two.append([])
        loop_nb = 0
        for section in patch:
            meta = get_metadata_object(section["data"], section["object_bin"], name, loop_nb, gld_path, actual_end_offset)
            actual_section_data = {
                "object_bin": section["object_bin"],
                "start": meta["correct_start"],
            }
            actual_end_offset = meta["new_end"]
            objects_pass_two[-1].append(actual_section_data)
            for g in meta["offsets"]:
                globals[g] = meta["offsets"][g]
            loop_nb += 1

    # generate patches files
    print("generating patches (undefined reference should *not* be ignored)")
    for (file_name, datas) in zip(input_name, objects_pass_two):
        print("  for {}".format(file_name))
        diffs = {}
        loop_nb = 0
        for data in datas:
            patch_bin = generate_binary_patch(data["object_bin"], globals, data["start"], file_name, loop_nb, gld_path)
            diffs[data["start"]] = list(struct.unpack("B"*len(patch_bin), patch_bin))
            loop_nb += 1
        out_file_path = out_prefix + file_name + out_suffix
        with open(out_file_path, "w") as f:
            f.write(yaml.dump({"sys/main.dol": diffs}, Dumper=yaml.CDumper))
