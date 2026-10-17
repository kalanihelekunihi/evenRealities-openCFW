SECTIONS
{
  .bss.opencfw.codec.i2s_handle 0x2007450c (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.codec.i2s_handle))
  }
}
ASSERT(SIZEOF(.bss.opencfw.codec.i2s_handle) == 4, "codec I2S handle must be four bytes")
