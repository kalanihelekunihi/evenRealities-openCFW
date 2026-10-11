ENTRY(case_binary_06_41_candidate)
case_binary_ack0641 = 0x0010f001;
case_binary_legacy0641 = case_legacy_ff_prefix;
case_legacy_logger = 0x0010f101;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
