SECTIONS {
 .r1.output_gpio.configuration 0x20007228 : { *(.r1.output_gpio.configuration) }
 .r1.output_gpio.name0 0xc0754 : { *(.r1.output_gpio.name0) }
 .r1.output_gpio.name1 0xc0770 : { *(.r1.output_gpio.name1) }
 .r1.output_gpio.name2 0xc0780 : { *(.r1.output_gpio.name2) }
 .r1.output_gpio.name3 0xc0760 : { *(.r1.output_gpio.name3) }
 .r1.output_gpio.name4 0xc0790 : { *(.r1.output_gpio.name4) }
 .text 0x1000000 : { *(.text*) *(.rodata*) }
 .data 0x20010000 : { *(.data*) *(.bss*) *(COMMON) *(.r1.*) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) *(.note*) }
}
