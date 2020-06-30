from asmpatch.batch import batchpatch

gas = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-as"
gld = "/nix/store/wqdf40jb3787wvi004rm1k6m2i1fsgyv-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0/bin/powerpc-none-eabi-ld"

print("generating ...")
batchpatch(
    gas,
    gld,
    "0x805960BC", #offset of the end of the file
    [ "custom_funcs", "remove_optimization_for_freecam_ntsc", "apply_changes" ]
)
print("done !")
