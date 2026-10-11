/* Isolated, non-production link for current selected Bootloader source. */
ENTRY(opencfw_boot_startup_power_initialize)
SECTIONS {
  . = 0x08000000;
  .text : { *(.text .text.*) }
  .rodata : { *(.rodata .rodata.*) }
  .ARM.exidx : { *(.ARM.exidx .ARM.exidx.*) }
  .data : { *(.data .data.*) }
  .bss : { *(.bss .bss.* COMMON) }
}
__aeabi_d2f = 0x080f0001;
opencfw_bl_generic_log = 0x080f0011;
opencfw_bl_post_configure = 0x080f0021;
opencfw_boot_fs_error = 0x080f0031;
opencfw_boot_rom48 = 0x080f0041;
opencfw_boot_rom_delay_cycles = 0x080f0051;
opencfw_boot_rom_mram_program = 0x080f0061;
printf = 0x080f0071;
resume_scheduler = 0x080f0081;
