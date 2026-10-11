ENTRY(opencfw_provider_415fae)
SECTIONS { . = 0x10000; .text : { *(.text*) } .rodata : { *(.rodata*) } .data : { *(.data*) } .bss : { *(.bss*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
__aeabi_d2f = 0x08001001;
__aeabi_fcmpeq = 0x08001011;
