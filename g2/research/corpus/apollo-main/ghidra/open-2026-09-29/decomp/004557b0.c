
undefined8 FUN_004557b0(int param_1,int *param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = 0;
  if (*param_2 != 0) {
    param_2[1] = *(int *)(param_2[1] + 4);
    if ((int *)param_2[1] == param_2 + 2) {
      param_2[1] = *(int *)(param_2[1] + 4);
    }
    iVar2 = *(int *)(param_2[1] + 0xc);
    do {
      param_2[1] = *(int *)(param_2[1] + 4);
      if ((int *)param_2[1] == param_2 + 2) {
        param_2[1] = *(int *)(param_2[1] + 4);
      }
      iVar3 = *(int *)(param_2[1] + 0xc);
      FUN_00455728(iVar3,param_1 + iVar1 * 0x24,1,param_3);
      iVar1 = iVar1 + 1;
    } while (iVar3 != iVar2);
  }
  return CONCAT44(param_4,iVar1);
}

