ENTRY(__aeabi_uidiv)
SECTIONS {
 .division 0xA6C0 : { *uidiv.o(.text) }
 .zero 0xA9A8 : { *zero.o(.text) }
 /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
