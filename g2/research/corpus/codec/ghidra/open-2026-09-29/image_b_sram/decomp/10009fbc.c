
undefined4 FUN_10009fbc(int *param_1,undefined1 *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = param_1[1];
  if (iVar2 != *param_1) {
    iVar3 = param_1[4];
    if (0 < iVar3) {
      iVar1 = 0;
      do {
        iVar2 = iVar2 + iVar1;
        iVar1 = iVar1 + 1;
        *param_2 = *(undefined1 *)(param_1[2] + (iVar2 - param_1[3] * (iVar2 / param_1[3])));
        param_2 = param_2 + 1;
        iVar3 = param_1[4];
        iVar2 = param_1[1];
      } while (iVar1 < iVar3);
    }
    param_1[1] = (iVar2 + iVar3) - param_1[3] * ((iVar2 + iVar3) / param_1[3]);
    return 1;
  }
  return 0;
}

