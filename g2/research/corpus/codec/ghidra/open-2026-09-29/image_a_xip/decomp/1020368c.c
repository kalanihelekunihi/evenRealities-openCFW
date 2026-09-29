
undefined4 gx8002_uart_receive_start(int param_1,int param_2,undefined4 param_3)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = param_1 * 0x80 + DAT_102036bc;
  if (param_2 == 0) {
    uVar1 = 0xffffffff;
  }
  else {
    *(undefined4 *)(iVar2 + 0x40) = 1;
    *(int *)(iVar2 + 0x50) = param_2;
    *(undefined4 *)(iVar2 + 0x54) = param_3;
    func_0x10025560();
    *(uint *)(*(int *)(iVar2 + 4) + 4) = *(uint *)(*(int *)(iVar2 + 4) + 4) | 1;
    func_0x1002556c();
    uVar1 = 0;
  }
  return uVar1;
}

