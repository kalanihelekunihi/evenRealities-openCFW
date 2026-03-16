/* ============================================================================
 * apollo510b_bootloader.ld — Linker script for G2 bootloader
 *
 * Target: Ambiq Apollo510b (ARM Cortex-M55)
 * Flash region: 0x00410000 – 0x00438000 (~160 KB)
 * Hands off to main application at 0x00438000 via VTOR relocation
 *
 * Derived from docs/firmware/firmware-files.md § 4.2, § 6.1
 * ============================================================================ */

MEMORY
{
    FLASH (rx)  : ORIGIN = 0x00410000, LENGTH = 160K
    SRAM (rwx)  : ORIGIN = 0x20000000, LENGTH = 512K
}

_stack_top = 0x2007FB00;
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

/* Application handoff address — bootloader jumps here after validation */
_app_entry = 0x00438000;
