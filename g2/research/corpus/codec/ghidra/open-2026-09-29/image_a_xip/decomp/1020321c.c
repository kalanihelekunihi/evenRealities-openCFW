
undefined4 gx8002_uart_transmit_abort_dma(int param_1)

{
  if (-1 < *(int *)(param_1 + 0x7c)) {
    gx8002_dma_abort();
    *(undefined4 *)(param_1 + 0x7c) = 0xffffffff;
  }
  return 0;
}

