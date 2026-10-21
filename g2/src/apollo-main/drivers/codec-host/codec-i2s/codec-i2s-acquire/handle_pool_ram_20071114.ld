SECTIONS
{
  .bss.opencfw.codec.i2s_handle_pool 0x20071114 (NOLOAD) :
  {
    KEEP(*(.bss.opencfw.codec.i2s_handle_pool))
  }
}
ASSERT(SIZEOF(.bss.opencfw.codec.i2s_handle_pool) == 200, "I2S handle pool must be 200 bytes")
