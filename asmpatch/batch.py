import struct
import yaml
import os
from .parser import parse_asm
from .patch import split_part, generate_object, get_metadata_object, generate_binary_patch
from .util import read_file, parse_hex_to_int
from .linker import read_linker_files

#TODO: use and abuse of map reduce
def batchpatch(
    gas_path,
    gld_path,
    gpp_path,
    end_offset,
    tmp_builder,
    input_output_files,
    linker_files = [],
):

    input_files = []
    output_files = []

    for (input, output) in input_output_files:
        input_files.append(input)
        output_files.append(output)

    globals = read_linker_files(linker_files)

    splited = []
    print("reading/splitting the different function")
    for input_path in input_files:
        content = read_file(input_path)
        dir_path = os.path.dirname(input_path)
        parsed = parse_asm(content, dir_path, gpp_path, tmp_builder)
        splited.append(split_part(parsed))

    # generate object file
    print("generating the object file")
    objects = []
    for (patch, input_path) in zip(splited, input_files):
        actual_object = []
        loop_counter = 0
        for section in patch:
            actual_object.append({
                "object_bin": generate_object(section, gas_path, input_path, loop_counter, tmp_builder),
                "data": section
            })
            start = actual_object[-1]["data"]["start"]

            splited_by = {
                "+": start.split("+"),
                "-": start.split("-")
            }

            diff = 0
            for splited_char in splited_by:
                if len(splited_by[splited_char]) > 2:
                    raise BaseException("no more than one {} can be present on a line, to indicate a difference in the offset.".format(splited_char))
                if len(splited_by[splited_char]) == 2:
                    if diff != 0:
                        raise BaseException("there can't be a + and - in the same line (to indicate a difference in the offset).")
                    diff_string = splited_by[splited_char][1]
                    diff = parse_hex_to_int(diff_string)
                    if splited_char == "-":
                        diff = -diff
                    start = splited_by[splited_char][0]

            if start in globals:
                actual_object[-1]["data"]["start"] = globals[start]+diff

            elif isinstance(start, str) and start != "end":
                if diff != 0:
                    raise BaseException("no diff can be accepted when there is just an offset (the offset is {}).".format(start))
                actual_object[-1]["data"]["start"] = parse_hex_to_int(start)

            loop_counter += 1
        objects.append(actual_object)

    actual_end_offset = end_offset

    # generate and read map file. Embed true offset position, and global
    # TODO: check and merge overwrite
    print("generating map file (metadata) (undefined reference can be ignored)")
    objects_pass_two = []
    for (patch, input_path) in zip(objects, input_files):
        objects_pass_two.append([])
        loop_nb = 0
        for section in patch:
            meta = get_metadata_object(section["data"], section["object_bin"], input_path, loop_nb, gld_path, actual_end_offset, tmp_builder)
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
    for (input_path, output_path, datas) in zip(input_files, output_files, objects_pass_two):
        print("  from {} to {}".format(input_path, output_path))
        diffs = {}
        loop_nb = 0
        for data in datas:
            patch_bin = generate_binary_patch(data["object_bin"], globals, data["start"], input_path, loop_nb, gld_path, tmp_builder)
            diffs[data["start"]] = list(struct.unpack("B"*len(patch_bin), patch_bin))
            loop_nb += 1
        with open(output_path, "w") as f:
            f.write(yaml.dump({"sys/main.dol": diffs}, Dumper=yaml.CDumper))
