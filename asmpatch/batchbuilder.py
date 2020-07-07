import os
from .batch import batchpatch
from .util import TemporyFolderBuilder

class BatchBuilder: # a rust like builder for a batch
    def __init__(self):
        self.end_offset = None
        self.gld = None
        self.gas = None
        self.gpp = None
        self.input_output_files = []
        self.linker_files = []
        self.tmp_builder = TemporyFolderBuilder()

    def set_end_offset(self, end_offset):
        assert isinstance(end_offset, int)
        self.end_offset = end_offset

    def with_gcc_path(self, gcc_path):
        gcc_bin_path = os.path.join(gcc_path, "bin")
        gcc_executables = os.listdir(gcc_bin_path)

        suffix_to_look_for = [ "as", "ld", "g++" ]
        executables = {}
        for executable in gcc_executables:
            if executable.endswith(".exe"):
                normalized_executable = executable[0:-4]
            else:
                normalized_executable = executable
            for suffix in suffix_to_look_for:
                if normalized_executable.endswith(suffix):
                    if normalized_executable.endswith("ld.gold") or normalized_executable.endswith("ld.bfd"): #endswith sometime allow those two with endswith("ld")
                        continue
                    executables[suffix] = os.path.join(gcc_bin_path, executable)

        if executables["as"] == None:
            print("can't find gnu as in the folder {}".format(gcc_bin_path))
        else:
            self.gas_path = executables["as"]

        if executables["ld"] == None:
            print("can't find gnu ld in the folder {}".format(gcc_bin_path))
        else:
            self.gld_path = executables["ld"]

        if executables["g++"] == None:
            print("can't find g++ in the folder {}".format(gcc_bin_path))
        else:
            self.gpp_path = executables["g++"]

    def with_linker_file(self, linker_path):
        self.linker_files.append(linker_path)

    def with_patch(self, input_path, output_path):
        self.input_output_files.append((input_path, output_path))

    def with_tmp_builder(self, tmp_builder):
        self.tmp_builder = tmp_builder

    def execute(self):
        errors = []
        if self.gas_path == None:
            errors.append("the gnu assembler binary is not defined when trying to execute a patch batch.")
        if self.gld_path == None:
            errors.append("the gnu ld binary is not defined when trying to execute a patch batch.")
        if self.gld_path == None:
            errors.append("the g++ binary is not defined when trying to execute a patch batch.")
        if self.end_offset == None:
            errors.append("the end offset of the patched binary is not indicated while trying to execute a batch patch.")
        if self.input_output_files == []:
            errors.append("No input (and output) files are defined in the batch builder while trying to execute a batch patch.")
        if len(errors) != 0:
            for error_message in errors[:-1]:
                print(error_message)
            raise BaseException(error_message[-1])
        batchpatch(
            gas_path = self.gas_path,
            gld_path = self.gld_path,
            gpp_path = self.gpp_path,
            end_offset = self.end_offset,
            tmp_builder = self.tmp_builder,
            input_output_files = self.input_output_files,
            linker_files = self.linker_files,
        )
