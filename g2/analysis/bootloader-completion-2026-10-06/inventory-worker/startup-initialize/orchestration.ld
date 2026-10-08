child_42252e = 0x8000201;
child_41c17a = 0x8000211;
child_41c2d8 = 0x8000221;
child_41bf84 = 0x8000231;
child_41b918 = 0x8000241;
child_41c320 = 0x8000251;
child_421548 = 0x8000261;
child_41ce52 = 0x8000271;
child_41bbd0 = 0x8000281;
child_41be36 = 0x8000291;
child_41b8ec = 0x80002a1;
child_41acb2 = 0x80002b1;
ENTRY(reconstructed_initialize)
SECTIONS { . = 0x10000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
