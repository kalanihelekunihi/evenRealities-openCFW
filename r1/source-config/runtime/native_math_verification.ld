/* Verification placement only. This is not a final firmware linker script. */
SECTIONS
{
    .errno 0x20007dbc (NOLOAD) : { KEEP(*(.r1.runtime.errno)) }
    .round_one 0x28330 : { KEEP(*(.r1.float.round_one)) }
    .decimal_zero 0x3f6a8 : { KEEP(*(.r1.format.decimal_zero)) }
    .text 0x1000000 : { *(.text*) *(.rodata*) }
    /DISCARD/ : { *(.ARM.exidx*) *(.comment*) }
}
