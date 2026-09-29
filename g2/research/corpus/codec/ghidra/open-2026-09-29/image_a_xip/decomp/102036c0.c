
undefined4 gx8002_uart_receive_stop(int param_1)

{
  int iVar1;
  
  iVar1 = param_1 * 0x80 + DAT_102036e4;
  *(undefined4 *)(iVar1 + 0x50) = 0;
  *(undefined4 *)(iVar1 + 0x54) = 0;
  func_0x10025560();
  *(uint *)(*(int *)(iVar1 + 4) + 4) = *(uint *)(*(int *)(iVar1 + 4) + 4) & 0xfffffffe;
  func_0x1002556c();
  return 0;
}

