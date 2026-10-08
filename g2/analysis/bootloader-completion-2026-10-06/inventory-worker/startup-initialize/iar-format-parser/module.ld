ENTRY(opencfw_format_parse)
SECTIONS{. = 0x70000;.text : {*(.text*) *(.rodata*)}.ARM.exidx : {*(.ARM.exidx*)}}
