SECTIONS {
  .opencfw.evenai.ready.state 0x2006f138 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.ready.state))
  }
  .opencfw.evenai.text.handle 0x20074c04 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.text.handle))
  }
  .opencfw.evenai.text.pending 0x200f39b4 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.text.pending))
  }
  .opencfw.evenai.text.merged 0x200f3db4 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.text.merged))
  }
} INSERT AFTER .bss;
