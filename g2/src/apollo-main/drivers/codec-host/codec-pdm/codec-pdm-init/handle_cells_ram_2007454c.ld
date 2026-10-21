SECTIONS
{
  .bss.opencfw.pdm.alternate_handle 0x2007454c (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.pdm.alternate_handle))
  }
  .bss.opencfw.pdm.production_handle 0x20074550 (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.pdm.production_handle))
  }
}
ASSERT(SIZEOF(.bss.opencfw.pdm.alternate_handle) == 4, "alternate PDM handle must be four bytes")
ASSERT(SIZEOF(.bss.opencfw.pdm.production_handle) == 4, "production PDM handle must be four bytes")
