
uint gx8002_dma_bus_address(uint param_1)

{
  if (param_1 < 0x20000000) {
    param_1 = param_1 & 0x7ffffff;
  }
  return param_1;
}

