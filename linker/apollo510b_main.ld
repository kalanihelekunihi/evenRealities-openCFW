/* ============================================================================
 * apollo510b_main.ld — Linker script for G2 main application firmware
 *
 * Target: Ambiq Apollo510b (ARM Cortex-M55)
 * Load address: 0x00438000 (after bootloader region)
 * SRAM: 512 KB (0x20000000 – 0x2007FFFF)
 * Stack pointer: 0x2007FB00
 *
 * Derived from:
 *   - docs/firmware/firmware-files.md § 4.1 (preamble + ARM vector table)
 *   - docs/firmware/firmware-files.md § 6.1 (flash memory map)
 *   - Reference firmware v2.0.7.16 ARM vector table analysis
 * ============================================================================ */

MEMORY
{
    /* Main application flash region (after bootloader) */
    FLASH (rx)  : ORIGIN = 0x00438000, LENGTH = 3136K

    /* SRAM — shared between all tasks (FreeRTOS) */
    SRAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 512K

    /* Extended SRAM (if available on Apollo510b) */
    /* ESRAM (rwx) : ORIGIN = 0x20080000, LENGTH = 512K */
}

/* Stack pointer initial value — top of usable SRAM */
_stack_top = 0x2007FB00;

/* Entry point — Reset_Handler from vector table */
ENTRY(Reset_Handler)

SECTIONS
{
    /* ── Vector table + code ── */
    .text :
    {
        . = ALIGN(4);
        KEEP(*(.isr_vector))     /* ARM Cortex-M55 vector table */
        *(.text*)                /* Code */
        *(.rodata*)              /* Read-only data */
        . = ALIGN(4);
        _etext = .;
    } > FLASH

    /* ── Initialized data (copied from flash to SRAM at startup) ── */
    .data : AT(_etext)
    {
        . = ALIGN(4);
        _sdata = .;
        *(.data*)
        . = ALIGN(4);
        _edata = .;
    } > SRAM

    /* ── Zero-initialized data ── */
    .bss :
    {
        . = ALIGN(4);
        _sbss = .;
        *(.bss*)
        *(COMMON)
        . = ALIGN(4);
        _ebss = .;
    } > SRAM

    /* ── Heap (grows up from end of BSS) ── */
    .heap :
    {
        . = ALIGN(8);
        _heap_start = .;
        /* FreeRTOS manages its own heap via pvPortMalloc/TLSF */
        . = . + 128K;
        _heap_end = .;
    } > SRAM

    /* ── Stack (at top of SRAM) ── */
    .stack :
    {
        . = ALIGN(8);
        _stack_bottom = .;
        . = . + 4K;
        _stack_top_check = .;
    } > SRAM
}

/* Symbols for startup code (C runtime init) */
_sidata = LOADADDR(.data);  /* Flash address of .data initializers */
