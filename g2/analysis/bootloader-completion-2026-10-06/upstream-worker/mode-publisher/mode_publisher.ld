/* SPDX-License-Identifier: MIT */
ENTRY(opencfw_publish_mspi_mode)
SECTIONS {
  . = 0x432000;
  .text : { *(.text*) *(.rodata*) }
  .ARM.exidx : { *(.ARM.exidx*) }
  .data : { *(.data*) }
  .bss : { *(.bss*) *(COMMON) }
}
