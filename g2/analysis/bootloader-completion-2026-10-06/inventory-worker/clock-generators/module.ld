SECTIONS {
 . = 0x08010000;
 .text : { *(.text*) *(.rodata*) }
 .ARM.exidx : { *(.ARM.exidx*) }
}
/* Explicit test cuts, not recovered implementations. */
opencfw_boot_pll_gcd = 0x08002001;
opencfw_boot_pll_vco_generate = 0x08002011;
