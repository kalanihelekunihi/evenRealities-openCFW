SECTIONS
{
  .bss.opencfw.pdm.handle_rows 0x200718c8 (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.pdm.handle_rows))
  }
}
ASSERT(SIZEOF(.bss.opencfw.pdm.handle_rows) == 128, "PDM handle rows must be 128 bytes")
