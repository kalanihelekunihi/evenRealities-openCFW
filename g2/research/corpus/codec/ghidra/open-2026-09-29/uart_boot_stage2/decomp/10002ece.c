
uint dw_uart_getc(int param_1)

{
  do {
  } while (((*(uint **)(param_1 + 4))[5] & 1) == 0);
  return **(uint **)(param_1 + 4) & 0xff;
}

