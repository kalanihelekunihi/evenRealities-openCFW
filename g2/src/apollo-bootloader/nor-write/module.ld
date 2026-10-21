/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_provider_420b0c)
PHDRS { text PT_LOAD FLAGS(5); }

/* Exact stock entry aliases around this recovered source module. */
opencfw_provider_42069e = 0x0042069f;
opencfw_provider_420f10 = 0x00420f11;
opencfw_bl_nor_read_before = 0x0041ff09;
opencfw_bl_nor_read_configure = 0x00420e8d;
opencfw_bl_nor_read_delay = 0x004207f5;
opencfw_bl_nor_read_after = 0x0041ff1f;
opencfw_bl_nor_wait = 0x004207a3;
opencfw_bl_printf = 0x00415faf;
opencfw_bl_log = 0x004176cf;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  .data : { *(.data*) } :text
  .bss : { *(.bss*) } :text
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
