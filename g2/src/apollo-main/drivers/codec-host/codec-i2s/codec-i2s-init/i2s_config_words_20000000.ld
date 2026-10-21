SECTIONS
{
  .data.opencfw.codec.i2s_config_base 0x20000000 :
  {
    KEEP(*(.data.opencfw.codec.i2s_config_base))
  }
  .data.opencfw.codec.i2s_dma_descriptor 0x20000740 :
  {
    KEEP(*(.data.opencfw.codec.i2s_dma_descriptor))
  }
}
ASSERT(SIZEOF(.data.opencfw.codec.i2s_config_base) == 40, "I2S config size")
ASSERT(SIZEOF(.data.opencfw.codec.i2s_dma_descriptor) == 24, "I2S DMA descriptor size")
