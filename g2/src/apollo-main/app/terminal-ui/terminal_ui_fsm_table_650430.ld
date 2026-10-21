SECTIONS {
  .rodata.opencfw.terminal.ui_fsm 0x650430 : {
    KEEP(*(.rodata.opencfw.terminal.ui_fsm))
  }
}
INSERT AFTER .rodata;
ASSERT(SIZEOF(.rodata.opencfw.terminal.ui_fsm) == 4160,
       "stock Terminal UI FSM table extent")
