
void gx8002_uart_stage1_put_sync(undefined4 param_1)

{
  uint *puVar1;
  
  puVar1 = (undefined4 *)*puRam100005c0 + 5;
  do {
  } while ((*puVar1 & 0x40) == 0);
  *(undefined4 *)*puRam100005c0 = param_1;
  do {
  } while ((*puVar1 & 0x40) == 0);
  return;
}

