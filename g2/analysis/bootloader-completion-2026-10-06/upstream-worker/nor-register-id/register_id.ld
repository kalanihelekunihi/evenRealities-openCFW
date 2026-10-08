/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_read_mspi_register_id)
SECTIONS {
  . = 0x432000;
  .text : { *(.text*) *(.rodata*) }
  .ARM.exidx : { *(.ARM.exidx*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
