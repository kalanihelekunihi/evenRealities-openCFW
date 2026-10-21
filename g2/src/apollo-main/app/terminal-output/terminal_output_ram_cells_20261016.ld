SECTIONS {
  .bss.opencfw.terminal.output_payload 0x20074a94 (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.output_payload))
  }
  .bss.opencfw.terminal.output_active 0x2007502c (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.output_active))
  }
  .bss.opencfw.terminal.output_mode 0x2007502d (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.output_mode))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.bss.opencfw.terminal.output_payload) == 4, "output payload cell size")
ASSERT(SIZEOF(.bss.opencfw.terminal.output_active) == 1, "output active cell size")
ASSERT(SIZEOF(.bss.opencfw.terminal.output_mode) == 1, "output mode cell size")
