.org end

; For crash testing
;.space 0x10000, 0xFF

.global set_charge_speed
set_charge_speed:
stwu sp, -0x10 (sp)
mflr r18
stw r18, 0x14 (sp)

bl setspyrorotspeedtor18
lfs f1,0(r18)

lwz r18, 0x14 (sp)
mtlr r18
addi sp, sp, 0x10
blr

.org end
.include_cpp ./setr18value.cpp
