.org end

; For crash testing
;.space 0x10000, 0xFF

.global set_charge_speed
set_charge_speed:
stwu sp, -0x10 (sp)
mflr r18
stw r18, 0x14 (sp)

lis r18, custom_charge_speed@ha
addi r18, r18, custom_charge_speed@l
lfs f1,0(r18)

lwz r18, 0x14 (sp)
mtlr r18
addi sp, sp, 0x10
blr

.global custom_charge_speed
custom_charge_speed:
.long 0x42700000
.long 0x00000000
