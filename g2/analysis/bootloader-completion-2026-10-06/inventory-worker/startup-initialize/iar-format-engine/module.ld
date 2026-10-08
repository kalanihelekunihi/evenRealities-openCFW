ENTRY(opencfw_iar_format_engine)
SECTIONS{. = 0x70000;.text : {*(.text*) *(.rodata*)}.ARM.exidx : {*(.ARM.exidx*)}}
