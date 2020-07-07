from asmpatch.batchbuilder import BatchBuilder
from asmpatch.util import TemporyFolderBuilder

import os
os.makedirs("./build", exist_ok=True)

import subprocess
#TODO: cache, autofind, config file



batch = BatchBuilder()
batch.set_end_offset(int("805954bc", 16)) #TODO: auto find end offset via elf file. Also auto add the linker file
gcc_path = subprocess.check_output(["nix-build", "<nixpkgs>", "-A", "pkgs.pkgsCross.ppc-embedded.buildPackages.gcc", "--no-out-link"], encoding="ascii").split("\n")[0]
# something like /nix/store/ps6pvl36wzsdcibxkyxm8wiy5qxkx87p-powerpc-none-eabi-stage-final-gcc-debug-wrapper-9.3.0, contain bin/powerpc-none-eabi-* files
batch.with_gcc_path(gcc_path)
batch.with_linker_file("patches/spyro06_ntsc.ld")
tmp_folder = TemporyFolderBuilder()
tmp_folder.set_keep_folder(True)
batch.with_tmp_builder(tmp_folder)
for name in ["custom_funcs", "remove_optimization_for_freecam_ntsc", "apply_changes", "include_cpp"]:
    batch.with_patch("./patches/{}.asm".format(name), "./build/{}_diff.txt".format(name))

print("generating ...")
batch.execute()
print("done !")
