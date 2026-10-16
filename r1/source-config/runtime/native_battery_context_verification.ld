SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .device 0x20016b84 : { *(.r1.battery.device) }
 .runtime 0x20006890 : { *(.r1.battery.runtime) }
 .thread 0x20006638 : { *(.r1.battery.thread) }
 .lowthread 0x20006548 : { *(.r1.battery.low.thread) }
 .power 0x20006878 : { *(.r1.battery.power.clients) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
