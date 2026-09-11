/* SPDX-License-Identifier: MIT */
/*
 * Board-routing literals here mirror the documented defaults in
 * board_config.h (OPEN_CFW_CASE_FLASH_BASE, _BANK1_BASE, _SRAM_BASE/BYTES,
 * _STACK_TOP, _BANK1_IDENTITY_LIMIT); a linker script cannot #include a C
 * header, so keep the two in sync by hand -- test_g2_case_source_manifest
 * checks they agree.
 */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 256K /* OPEN_CFW_CASE_FLASH_BASE / _FLASH_BANK_BYTES */
    SRAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 144K  /* OPEN_CFW_CASE_SRAM_BASE / _SRAM_BYTES */
}

__stack_top = 0x20002C88; /* OPEN_CFW_CASE_STACK_TOP */

SECTIONS
{
    .vectors ORIGIN(FLASH) : ALIGN(4) { KEEP(*(.vectors)) } > FLASH
    .text : ALIGN(4)
    {
        *(.text .text.*)
        *(.rodata .rodata.*)
        . = ALIGN(4);
        __text_end = .;
    } > FLASH
    .data : ALIGN(4)
    {
        __data_start = .;
        *(.data .data.*)
        . = ALIGN(4);
        __data_end = .;
    } > SRAM AT > FLASH
    __data_load = LOADADDR(.data);
    .bss (NOLOAD) : ALIGN(4)
    {
        __bss_start = .;
        *(.bss .bss.* COMMON)
        . = ALIGN(4);
        __bss_end = .;
    } > SRAM
    __flash_load_end = LOADADDR(.data) + SIZEOF(.data);
    ASSERT(__flash_load_end <= 0x0803F000, /* OPEN_CFW_CASE_BANK1_IDENTITY_LIMIT */
           "Case source image overlaps preserved bank-1 identity window")
    ASSERT(__bss_end <= ORIGIN(SRAM) + LENGTH(SRAM),
           "Case source image exceeds STM32G0B1 SRAM")
    /DISCARD/ : { *(.comment) *(.note*) *(.ARM.attributes) }
}
