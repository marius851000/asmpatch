import yaml

output_file = "merged_diff.txt"

patch_to_merge = [ "custom_funcs", "apply_changes" ]

patched_bytes = {} # offset: value (1 byte)

for patch_name in patch_to_merge:
    patch_path = patch_name + "_diff.txt"
    f = open(patch_path)
    parsed_file = yaml.load(f)
    f.close()
    main_dol = parsed_file["sys/main.dol"]
    for patch_offset in main_dol:
        for byte_nb in range(len(main_dol[patch_offset])):
            byte_offset = patch_offset + byte_nb
            patched_bytes[byte_offset] = main_dol[patch_offset][byte_nb]

list_of_keys = []
for key in patched_bytes:
    list_of_keys.append(key)

list_of_keys.sort()

actual_key_id = -1
start_of_patch = -1
patches = {}
for key in list_of_keys:
    if key != actual_key_id + 1:
        print("new patch start at {}.".format(key))
        start_of_patch = key
        patches[start_of_patch] = []
    patches[start_of_patch].append(patched_bytes[key])
    actual_key_id = key

f = open(output_file, "w")
f.write(yaml.dump({"sys/main.dol": patches}, Dumper=yaml.CDumper))
f.close()
