SECTIONS {
 .rodata 0x3357b4 : { *(.rodata) }
 .context_802a60 0x802a60 (NOLOAD) : { *(.bss.opencfw_scan_context_802a60) }
 .context_8035dc 0x8035dc (NOLOAD) : { *(.bss.opencfw_scan_context_8035dc) }
 .context_80389c 0x80389c (NOLOAD) : { *(.bss.opencfw_scan_context_80389c) }
 /DISCARD/ : { *(.comment) *(.note*) *(.ARC.attributes) }
}
ASSERT(SIZEOF(.rodata) == 12, "table extent")
ASSERT(SIZEOF(.context_802a60) == 704, "context extent")
ASSERT(SIZEOF(.context_8035dc) == 704, "context extent")
ASSERT(SIZEOF(.context_80389c) == 704, "context extent")
