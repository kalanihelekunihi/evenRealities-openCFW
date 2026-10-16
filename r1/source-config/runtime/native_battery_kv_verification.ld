SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .power 0x20006abc : { *(.r1.battery.kv.power) }
 .devinfo 0x200069a8 : { *(.r1.battery.kv.devinfo) }
 .powerhandle 0x20007df8 : { *(.r1.battery.kv.power.handle) }
 .devinfohandle 0x20007de8 : { *(.r1.battery.kv.devinfo.handle) }
 .port 0x20006974 : { *(.r1.kv.port_slot) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
