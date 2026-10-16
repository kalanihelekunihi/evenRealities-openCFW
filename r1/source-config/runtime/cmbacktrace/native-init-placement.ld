/* Authenticated private-state placement; linker range symbols are supplied
   by the native configuration/verification driver, not invented image bounds. */
SECTIONS {
 .cmb_init_flag 0x20007a1c (NOLOAD) : { *(.bss.init_ok) }
 .cmb_stack_start 0x20007a24 (NOLOAD) : { *(.bss.main_stack_start_addr) }
 .cmb_stack_size 0x20007a28 (NOLOAD) : { *(.bss.main_stack_size) }
 .cmb_code_start 0x20007a2c (NOLOAD) : { *(.bss.code_start_addr) }
 .cmb_code_size 0x20007a30 (NOLOAD) : { *(.bss.code_size) }
 .cmb_fw_name 0x2002e8e4 (NOLOAD) : { *(.bss.fw_name) }
 .cmb_hw_ver 0x2002e8f9 (NOLOAD) : { *(.bss.hw_ver) }
 .cmb_sw_ver 0x2002e90e (NOLOAD) : { *(.bss.sw_ver) }
 . = 0x01000000; .text : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
