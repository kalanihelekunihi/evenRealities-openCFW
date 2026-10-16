SECTIONS {
 .text 0x01000000 : { *(.text*) }
 .name 0x50f20 : { *(.r1.gxt.bus.name) }
 .state 0x200076f8 (NOLOAD) : { *(.r1.gxt.bus.state) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_stock_registry_find = 0x20000201;
r1_stock_dispatch_08 = 0x20000211;
r1_stock_dispatch_0c = 0x20000221;
r1_stock_dispatch_10 = 0x20000231;
r1_stock_dispatch_14 = 0x20000241;
