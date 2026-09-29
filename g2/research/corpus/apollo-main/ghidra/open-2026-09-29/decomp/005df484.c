
undefined4 FUN_005df484(int param_1,int param_2,int param_3,undefined4 param_4,int *param_5)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_2 == 0) {
    iVar1 = *(int *)(*(int *)(param_1 + 0x68) + 4);
  }
  else {
    iVar1 = FUN_005df158(param_1);
    if (iVar1 == 0) {
      return 0x8e;
    }
    param_3 = *(int *)(iVar1 + 8) + param_3;
    iVar1 = *(int *)(iVar1 + 0xc);
  }
  if ((param_5 == (int *)0x0) || (*param_5 != 0)) {
    if (param_5 != (int *)0x0) {
      iVar1 = *param_5;
    }
    uVar2 = FT_Stream_ReadAt(*(undefined4 *)(param_1 + 0x68),param_3,param_4,iVar1);
  }
  else {
    *param_5 = iVar1;
    uVar2 = 0;
  }
  return uVar2;
}

