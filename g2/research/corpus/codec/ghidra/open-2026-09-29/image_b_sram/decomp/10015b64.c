
undefined4 FUN_10015b64(int *param_1,undefined4 *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  iVar2 = *param_1;
  iVar3 = param_1[3];
  iVar1 = iVar2 + param_1[4];
  iVar1 = iVar1 - iVar3 * (iVar1 / iVar3);
  if (iVar1 != param_1[1]) {
    if (0 < param_1[4]) {
      iVar1 = 0;
      while( true ) {
        uVar4 = *param_2;
        param_2 = (undefined4 *)((int)param_2 + 1);
        *(char *)(param_1[2] + ((iVar2 + iVar1) - iVar3 * ((iVar2 + iVar1) / iVar3))) = (char)uVar4;
        iVar1 = iVar1 + 1;
        if (param_1[4] <= iVar1) break;
        iVar2 = *param_1;
        iVar3 = param_1[3];
      }
      iVar1 = param_1[4] + *param_1;
      iVar1 = iVar1 - param_1[3] * (iVar1 / param_1[3]);
    }
    *param_1 = iVar1;
    return 1;
  }
  return 0;
}

