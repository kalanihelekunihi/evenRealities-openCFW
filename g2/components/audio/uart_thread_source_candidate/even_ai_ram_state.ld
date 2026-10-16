/* Observed EvenAI RAM extents; reserve without startup image bytes. */
SECTIONS {
  .opencfw.evenai.service 0x2006ed10 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.service))
  }
  .opencfw.evenai.heartbeat 0x20074014 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.heartbeat))
  }
  .opencfw.evenai.mutex 0x20074580 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.mutex))
  }
  .opencfw.evenai.config 0x20074974 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.config))
  }
  .opencfw.evenai.last 0x20074f36 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.last))
  }
  .opencfw.evenai.proto 0x200f5884 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.proto))
  }
  .opencfw.evenai.tx 0x2037c4a0 (NOLOAD) : {
    KEEP(*(.bss.opencfw.evenai.tx))
  }
}
INSERT AFTER .bss;
