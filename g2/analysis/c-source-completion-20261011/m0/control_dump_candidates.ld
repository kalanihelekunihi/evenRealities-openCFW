case_legacy_logger = 0x0010f001;
case_legacy_aa_read = 0x0010f101;
case_legacy_ee_first = 0x0010f201;
case_binary_5e_hex = 0x0010f301;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.comment*) } }
