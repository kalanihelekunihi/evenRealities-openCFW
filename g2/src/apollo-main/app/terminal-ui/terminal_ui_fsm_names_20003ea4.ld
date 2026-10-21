SECTIONS {
  .bss.opencfw.terminal.ui_state_names 0x20003ea4 (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.ui_state_names))
  }
  .bss.opencfw.terminal.ui_event_names 0x20003edc (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.ui_event_names))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.bss.opencfw.terminal.ui_state_names) == 52,
       "stock Terminal state-name pointer extent")
ASSERT(SIZEOF(.bss.opencfw.terminal.ui_event_names) == 160,
       "stock Terminal event-name pointer extent")
