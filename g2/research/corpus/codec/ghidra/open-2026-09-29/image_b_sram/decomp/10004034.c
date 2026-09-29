
void gx8002_uart_transmit_complete(undefined4 *param_1)

{
  gx8002_dma_release(param_1[0x1f]);
  param_1[0x1f] = 0xffffffff;
  FUN_10004584(*param_1);
  (*(code *)(param_1[0x1b] & 0xfffffffe))(*param_1,param_1[0x1c]);
  return;
}

