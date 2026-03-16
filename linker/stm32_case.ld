/* ============================================================================
 * stm32_case.ld — Linker script for G2 charging case MCU
 *
 * Target: STM32L0xx-class ARM Cortex-M0+ (inferred from vector table)
 * Flash base: 0x08000000 (STM32 convention, Reset=0x08000145)
 * SRAM: ~11 KB (SP=0x20002C88)
 *
 * Derived from docs/firmware/firmware-files.md § 4.4, § 6.3
 * The exact STM32 part is unknown — L053C8 (64KB flash, 8KB RAM) is a
 * reasonable guess based on SP address and feature set.
 * ============================================================================ */

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x08000000, LENGTH = 64K
    SRAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 8K
}

_stack_top = 0x20002C88;
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
