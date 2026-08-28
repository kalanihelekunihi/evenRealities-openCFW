/* SPDX-License-Identifier: MIT */
ENTRY(Reset_Handler)

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 64K
    SRAM  (rwx) : ORIGIN = 0x20000000, LENGTH = 8K
}

__stack_top = ORIGIN(SRAM) + LENGTH(SRAM);

SECTIONS
{
    .vectors ORIGIN(FLASH) : ALIGN(4)
    {
        KEEP(*(.vectors))
    } > FLASH

    .text : ALIGN(4)
    {
        *(.text .text.*)
        *(.rodata .rodata.*)
        KEEP(*(.open_cfw.exports))
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

    __heap_start = __bss_end;
    __heap_end = __stack_top;
    __flash_load_end = LOADADDR(.data) + SIZEOF(.data);

    ASSERT(__flash_load_end <= ORIGIN(FLASH) + LENGTH(FLASH) - 4,
           "Touch flash image exceeds 64 KiB before checksum")
    ASSERT(__bss_end <= __stack_top, "Touch SRAM image exceeds 8 KiB")

    /DISCARD/ :
    {
        *(.comment)
        *(.note*)
        *(.ARM.attributes)
    }
}
