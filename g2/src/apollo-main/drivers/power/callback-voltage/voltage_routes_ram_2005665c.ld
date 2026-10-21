SECTIONS
{
  .bss.opencfw.audio.voltage_routes 0x2005665c (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.audio.voltage_routes))
  }
}
ASSERT(SIZEOF(.bss.opencfw.audio.voltage_routes) == 108, "voltage route table must be 108 bytes")
