/* SPDX-License-Identifier: MIT
 * Isolated emulator address space; not the stock Apollo firmware link map.
 */
ENTRY(ambiq_sim_status)
MEMORY {
    CODE (rx) : ORIGIN = 0x00010000, LENGTH = 64K
    RAM (rw) : ORIGIN = 0x20000000, LENGTH = 64K
}
SECTIONS {
    .text : { *(.text*) *(.rodata*) } > CODE
    .ARM.exidx : { *(.ARM.exidx*) } > CODE
    .data : { *(.data*) } > RAM
    .bss (NOLOAD) : { *(.bss*) *(COMMON) } > RAM
    /DISCARD/ : { *(.comment) *(.note*) }
}
