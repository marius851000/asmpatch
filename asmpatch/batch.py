import struct
import yaml
import os
from .parser import parse_asm
from .patch import split_part, generate_object, get_metadata_object, generate_binary_patch
from .util import read_file

#TODO: use and abuse of map reduce
def batchpatch(
    gas_path,
    gld_path,
    gpp_path,
    end_offset,
    input_name,
    out_prefix = "",
    out_suffix = "_diff.txt",
    input_prefix = "",
    input_suffix = ".asm"
):

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
            loop_counter += 1
        objects.append(actual_object)

    actual_end_offset = end_offset

    # generate and read map file. Embed true offset position, and global
    # TODO: check and merge overwrite
    print("generating map file (metadata) (undefined reference can be ignored)")
    objects_pass_two = []
    globals = {}
    for (patch, name) in zip(objects, input_name):
        tmp_pass_two = []
        loop_nb = 0
        for section in patch:
            old_start = section["data"]["start"]
            if old_start == "end":
                old_start = actual_end_offset
            meta = get_metadata_object(section["data"], section["object_bin"], name, loop_nb, gld_path, actual_end_offset)
            actual_end_offset = meta["new_end"]
            actual_section_data = {}
            actual_section_data["object_bin"] = section["object_bin"]
            actual_section_data["start"] = old_start
            tmp_pass_two.append(actual_section_data)
            for g in meta["offsets"]:
                globals[g] = meta["offsets"][g]
            loop_nb += 1
        objects_pass_two.append(tmp_pass_two)

    # generate patches files
    print("generating patches (undefined reference should *not* be ignored)")
    for (file_name, datas) in zip(input_name, objects_pass_two):
        print("  for {}".format(file_name))
        diffs = {}
        loop_nb = 0
        for data in datas:
            patch_bin = generate_binary_patch(data["object_bin"], globals, data["start"], file_name, loop_nb, gld_path)
            diffs[int(data["start"], 16)] = list(struct.unpack("B"*len(patch_bin), patch_bin))
            loop_nb += 1
        out_file_path = out_prefix + file_name + out_suffix
        with open(out_file_path, "w") as f:
            f.write(yaml.dump({"sys/main.dol": diffs}, Dumper=yaml.CDumper))
