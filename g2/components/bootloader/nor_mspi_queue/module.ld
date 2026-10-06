/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_bl_mspi_clockgen_control)
PHDRS { text PT_LOAD FLAGS(5); resources PT_LOAD FLAGS(4); }

/* Reviewed private dependencies: architectural critical section, clock API,
 * and delay routine. Queue operations below are implemented in this module. */
opencfw_bl_critical_save = 0x0041b8ed;
opencfw_bl_clock_request = 0x004222f1;
opencfw_bl_delay_us = 0x0041d1c1;

SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) } :text
  .data : { *(.data*) } :text
  .bss : { *(.bss*) } :text
  .cmdq_resources 0x00430880 : { KEEP(*(.cmdq_resources)) } :resources
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
