from asmpatch.batch import batchpatch
import os
os.makedirs("./build", exist_ok=True)

gas = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-as"
gld = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-ld"
gpp = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-g++"

def transform_to_entry(name):
    return ("./patches/"+name+".asm", "./build/"+name+"_diff.txt")

print("generating ...")
batchpatch(
    gas,
    gld,
    gpp,
    int("805954bc", 16), #offset of the end of the file
    #[ "custom_funcs", "remove_optimization_for_freecam_ntsc", "apply_changes", "include_cpp" ],
    #[ "include_cpp" ],
    map(transform_to_entry, ["custom_funcs", "remove_optimization_for_freecam_ntsc", "apply_changes", "include_cpp"]),
    linker_files = [ "patches/spyro06_ntsc.ld" ],
)
print("done !")
