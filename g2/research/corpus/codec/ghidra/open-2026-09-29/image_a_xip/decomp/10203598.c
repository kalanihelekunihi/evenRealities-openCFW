
void gx8002_uart_flush(int param_1)

{
  do {
  } while ((*(uint *)(*(int *)(param_1 * 0x80 + DAT_102035b0 + 4) + 0x14) & 0x40) == 0);
  return;
}

