from asmpatch.batch import batchpatch
import os
os.makedirs("./build", exist_ok=True)

gas = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-as"
gld = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-ld"
gpp = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-g++"

print("generating ...")
batchpatch(
    gas,
    gld,
    gpp,
    "0x805954bc", #offset of the end of the file
    [ "custom_funcs", "remove_optimization_for_freecam_ntsc", "apply_changes" ],
    input_prefix = "./patches/",
    out_prefix = "./build/"
)
print("done !")
