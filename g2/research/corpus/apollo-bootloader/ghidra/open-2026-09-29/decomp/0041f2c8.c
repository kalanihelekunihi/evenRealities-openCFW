
longlong FUN_0041f2c8(code *param_1,int param_2,undefined1 *param_3,uint param_4)

{
  int iVar1;
  uint uVar2;
  
  uVar2 = param_4;
  while( true ) {
    if (uVar2 == 0) {
      return (ulonglong)param_4 << 0x20;
    }
    iVar1 = (*param_1)(*(undefined4 *)(param_2 + 8),*param_3);
    *(int *)(param_2 + 8) = iVar1;
    if (iVar1 == 0) break;
    *(int *)(param_2 + 0x2c) = *(int *)(param_2 + 0x2c) + 1;
    uVar2 = uVar2 - 1;
    param_3 = param_3 + 1;
  }
  return CONCAT44(param_4,0xffffffff);
}

