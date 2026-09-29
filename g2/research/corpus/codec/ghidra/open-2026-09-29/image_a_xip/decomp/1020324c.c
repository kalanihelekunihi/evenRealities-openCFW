
void dw_uart_putc(int param_1,undefined4 param_2)

{
  do {
  } while (((*(undefined4 **)(param_1 + 4))[5] & 0x20) == 0);
  **(undefined4 **)(param_1 + 4) = param_2;
  return;
}

