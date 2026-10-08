ENTRY(opencfw_format_integer_render)
SECTIONS{. = 0x70000;.text : {*(.text*) *(.rodata*)}.ARM.exidx : {*(.ARM.exidx*)}}
