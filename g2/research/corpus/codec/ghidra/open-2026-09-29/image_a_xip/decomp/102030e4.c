
void gx8002_uart_receive_complete(undefined4 *param_1)

{
  gx8002_dma_release(param_1[0x1a]);
  param_1[0x1a] = 0xffffffff;
  func_0x100256c0(param_1[0x18],param_1[0x19]);
  (*(code *)(param_1[0x16] & 0xfffffffe))(*param_1,param_1[0x17]);
  return;
}

