import tempfile
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

    splited = []
    print("reading/splitting the different function")
    for file_name in input_name:
        file_path = input_prefix + file_name + input_suffix
        content = read_file(file_path)
        dir_path = os.path.dirname(file_path)
        parsed = parse_asm(content, dir_path, gpp_path)
        splited.append(split_part(parsed))

    # generate object file
    print("generating the object file")
    objects = []
    for patch in splited:
        actual_object = []
        for section in patch:
            dir = tempfile.mkdtemp()
            actual_object.append({
                "dir": dir,
                "objpath": generate_object(section, gas_path, dir),
                "data": section
            })
        objects.append(actual_object)

    actual_end_offset = end_offset

    # generate and read map file. Embed true offset position, and global
    #TODO: check and merge overwrite
    print("generating map file (metadata) (undefined reference can be ignored)")
    objects_pass_two = []
    globals = {}
    for patch in objects:
        tmp_pass_two = []
        for section in patch:
            old_start = section["data"]["start"]
            if old_start == "end":
                old_start = actual_end_offset
            meta = get_metadata_object(section["data"], section["objpath"], gld_path, actual_end_offset, section["dir"])
            actual_end_offset = meta["new_end"]
            actual_section_data = {}
            actual_section_data["dir"] = section["dir"]
            actual_section_data["objpath"] = section["objpath"]
            actual_section_data["start"] = old_start
            tmp_pass_two.append(actual_section_data)
            for g in meta["offsets"]:
                globals[g] = meta["offsets"][g]
        objects_pass_two.append(tmp_pass_two)

    # generate patches files
    print("generating patches (undefined reference *should* not be ignored)")
    for file_nb in range(len(input_name)):
        file_name = input_name[file_nb]
        print("  for {}".format(file_name))
        datas = objects_pass_two[file_nb]
        diffs = {}
        for data in datas:
            patch_bin = generate_binary_patch(data["objpath"], globals, data["start"], gld_path, data["dir"])
            diffs[int(data["start"], 16)] = list(struct.unpack("B"*len(patch_bin), patch_bin))
        out_file_path = out_prefix + file_name + out_suffix
        with open(out_file_path, "w") as f:
            f.write(yaml.dump({"sys/main.dol": diffs}, Dumper=yaml.CDumper))
