SECTIONS
{
  .bss.opencfw.codec.power_state 0x20074fb6 (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.codec.power_state))
  }
}
ASSERT(SIZEOF(.bss.opencfw.codec.power_state) == 1, "codec power state must be one byte")
