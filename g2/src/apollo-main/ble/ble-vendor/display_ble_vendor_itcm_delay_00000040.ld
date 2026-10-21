SECTIONS
{
  .text.opencfw.itcm.delay_00000040 0x40 :
  {
    KEEP(*(.text.opencfw.itcm.delay_00000040))
  }
}
ASSERT(SIZEOF(.text.opencfw.itcm.delay_00000040) == 6, "ITCM delay must be six bytes")
