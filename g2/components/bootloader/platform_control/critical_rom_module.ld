ENTRY(opencfw_boot_mram_dispatch)
SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
/* critical-save executes source assembly */
opencfw_boot_control_guard_begin = 0x41bd93;
opencfw_boot_control_guard_end = 0x41bde5;
opencfw_boot_control_log = 0x08002131;
opencfw_boot_control_mode_one = 0x41f8bb;
opencfw_boot_control_mode_two = 0x41ba81;
opencfw_boot_control_cleanup = 0x41c991;
opencfw_boot_rom_mram_program = 0x0200ff21;
