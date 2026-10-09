SECTIONS {
 .text.deregister 0x33C0 : { *(.text.deregister_tm_clones) }
 .text.register 0x33E0 : { *(.text.register_tm_clones) }
 .text.dtors 0x3408 : { *(.text.__do_global_dtors_aux) }
 .text.frame 0x3434 : { *(.text.frame_dummy) }
 .eh_frame 0xB56C : { *(.eh_frame) }
 .init_array 0x2000087C : { *(.init_array) }
 .fini_array 0x20000880 : { *(.fini_array) }
 .tm_clone_table 0x20000884 : { *(.tm_clone_table) }
 .completed 0x200008A8 (NOLOAD) : { *(.bss.completed.1) }
 .object 0x200008AC (NOLOAD) : { *(.bss.object.0) }
 /DISCARD/ : { *(.rodata.all_implied_fbits) *(.data.__dso_handle) *(.ARM.attributes) }
}
__TMC_END__ = 0x20000884;
