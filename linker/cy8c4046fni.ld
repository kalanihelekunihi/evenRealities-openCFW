/* ============================================================================
 * cy8c4046fni.ld — Linker script for G2 touch controller
 *
 * Target: Cypress CY8C4046FNI (ARM Cortex-M0, PSoC4)
 * Flash: 0x00000000 (32 KB typical for CY8C4046)
 * SRAM:  0x20000000 (4 KB, SP=0x20002000 suggests 8KB variant)
 *
 * Derived from docs/firmware/firmware-files.md § 4.3
 * Touch firmware is wrapped in FWPK format with CRC32C checksum.
 * ============================================================================ */

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 32K
    SRAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 8K
}

_stack_top = 0x20002000;
ENTRY(Reset_Handler)

SECTIONS
{
    .text :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))
        *(.text*)
        *(.rodata*)
        . = ALIGN(4);
        _etext = .;
    } > FLASH

    .data : AT(_etext)
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > SRAM

    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > SRAM
}

_sidata = LOADADDR(.data);
