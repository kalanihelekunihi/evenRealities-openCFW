
undefined4 gx8002_uart_transmit_abort(int param_1)

{
  if (*(int *)(param_1 * 0x80 + DAT_10203700 + 0x2c) != 0) {
    gx8002_uart_transmit_abort_dma();
  }
  return 0;
}

