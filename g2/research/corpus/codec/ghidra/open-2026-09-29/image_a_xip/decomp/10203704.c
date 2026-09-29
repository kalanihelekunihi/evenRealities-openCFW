
undefined4 gx8002_uart_receive_abort(int param_1)

{
  if (*(int *)(param_1 * 0x80 + DAT_1020371c + 0x2c) != 0) {
    gx8002_uart_receive_abort_dma();
  }
  return 0;
}

