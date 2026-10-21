SECTIONS {
  .opencfw.terminal.list_anim_state 0x20070ea8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.terminal.list_anim_state))
  }
}
INSERT AFTER .bss;
