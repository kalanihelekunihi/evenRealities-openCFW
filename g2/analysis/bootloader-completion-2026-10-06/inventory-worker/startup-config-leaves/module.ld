ENTRY(config_copy)
configure_4 = 0x08001001;
configure_5 = 0x08001011;
configure_6 = 0x08001021;
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } }
