
void gx8002_uart_stage1_put(undefined4 param_1)

{
  do {
  } while ((((undefined4 *)*puRam1000059c)[5] & 0x40) == 0);
  *(undefined4 *)*puRam1000059c = param_1;
  return;
}

