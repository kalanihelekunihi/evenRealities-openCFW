PROVIDE(r1_dfu_bootloader_prepare_boundary = 0x20000201);
PROVIDE(r1_dfu_control_point_write_boundary = 0x20000205);
SECTIONS {
 .r1.dfu.context 0x2002c110 : { *(.r1.dfu.context) }
 .r1.dfu.value_seed 0x9c65c : { *(.r1.dfu.value_seed) }
 .r1.connection.field10 0x200064bc : { *(.r1.connection.field10) }
 .text 0x1000000 : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
