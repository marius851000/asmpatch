A (WIP) tool to generate patch for binary program. This tool doesn't apply them, but list the offset of bytes that should be changed in a yaml format (generated from assembly).

note: the various exemple embedded here are for the US gamcube version of the legend of spyro: a new beggining

It support having multiple .asm input (one patch is generated by asm).
A .asm patch can also patch multiple section of a file (with the .org instruction).
.org end can also be used. The program will select a free space at the end of the file, removing the potential conflict when adding information to the file.

.asm format:
this patcher use the gnu assembler. It should support most of its function. In addition to the standard GNU AS feature, it have those special handling:
.org are handled by this prorgram. The possible value are: either an hex address (with 0x...) or end. end write at a free space at the of the file
.global can accessed/defined by/from all the .asm file. I recommend you add a prefix to the patch, to prevent compatibility issue.

TODO:
- documentation
- use the g++ flag to have only one section
- use a logging library, transform all warning into true warning.
- a proper command line
- a method that permit to check that the difference with/without a rewritten function is the same (idea: load a savestate just before the function start, save one when it finish. Do this with/without the custom function (the difference is just the b that doesn't replace the original function) and compare the memory !)
