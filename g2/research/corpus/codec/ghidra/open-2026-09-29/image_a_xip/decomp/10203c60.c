
uint virt_to_dma(uint param_1)

{
  if (param_1 + 0xf0000000 < 0x20000000) {
    param_1 = param_1 & 0x7ffffff;
  }
  return param_1;
}

