.text
ld.as r0,[0x802878,r0]
cmp_s r0,0
jeq_s [blink]
j_s [r0]
nop_s
