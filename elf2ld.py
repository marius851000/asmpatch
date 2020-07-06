import subprocess

input_elf = "/home/marius/ANBHack/spyro06US.elf"
output_ld = "./patches/spyro06_ntsc.ld"

print("tranforming {} to {}".format(input_elf, output_ld))

out = subprocess.check_output([
    "objdump",
    "--syms",
    input_elf
], encoding="ascii")

symbols = {}
used_multiple_time = [] #TODO: understand why that

for line in str(out).split("\n")[2:]:
    splited = []
    new_part = True
    for chara in line:
        if chara == " " or chara == "\t":
            new_part = True
        else:
            if new_part:
                splited.append(chara)
                new_part = False
            else:
                splited[-1] += chara
    if len(splited) == 0:
        continue
    if splited[0] == "SYMBOL":
        continue
    name = splited[-1]
    if "@" in name:
        continue
    if "<" in name:
        continue
    if ">" in name:
        continue
    offset = "0x" + splited[0]
    if name[0] == ".":
        continue
    if name in symbols:
        used_multiple_time.append(name)
        del symbols[name]
    symbols[name] = offset

print("those symbol are reference multiple time, and are not included to prevent problem:")
print(used_multiple_time)
linker_file = open(output_ld, "w")
for name in symbols:
    offset = symbols[name]
    linker_file.write(name + " = " + offset + "\n")
linker_file.close()

print("done")
