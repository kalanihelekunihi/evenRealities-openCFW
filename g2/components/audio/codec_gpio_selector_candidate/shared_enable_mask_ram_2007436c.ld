SECTIONS
{
  .bss.opencfw.codec.shared_enable_mask 0x2007436c (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.codec.shared_enable_mask))
  }
}
ASSERT(SIZEOF(.bss.opencfw.codec.shared_enable_mask) == 4, "codec enable mask must be four bytes")
