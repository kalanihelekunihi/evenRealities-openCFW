ENTRY(ft_open_face_native)
SECTIONS { .native 0x438000 : {*(.native)} /DISCARD/ : {*(.ARM.exidx*) *(.comment*)} }
