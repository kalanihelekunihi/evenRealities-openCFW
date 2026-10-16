/* Verification-only terminal symbol. No application body or executable
   fallback is supplied; the verifier stops before this boundary executes. */
PROVIDE(r1_native_application_entry = 0x20000201);
SECTIONS {
 . = 0x000c43ec;
 .r1.scatter.regions : { *(.r1.scatter.regions) }
 . = 0x01000000;
 .text : { *(.text*) *(.rodata*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
