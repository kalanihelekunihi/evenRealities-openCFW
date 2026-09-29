
undefined4 FUN_005ca934(int param_1,int *param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  
  iVar1 = FUN_005c9dca(param_1,0);
  iVar2 = FUN_005c9dd4(param_1,0);
  iVar3 = FUN_005c9db6(param_1,0);
  iVar4 = FUN_005c9dc0(param_1,0);
  iVar5 = FUN_0043fd9e(param_1);
  iVar6 = FUN_0043fdda(param_1);
  if ((iVar5 - iVar1) - iVar2 < (iVar6 - iVar3) - iVar4) {
    iVar4 = FUN_0043fd9e(param_1);
    iVar2 = (iVar4 - iVar1) - iVar2;
  }
  else {
    iVar5 = FUN_0043fdda(param_1);
    iVar2 = (iVar5 - iVar3) - iVar4;
  }
  iVar2 = iVar2 / 2;
  *param_2 = iVar1 + iVar2 + *(int *)(param_1 + 0x14);
  param_2[1] = iVar3 + iVar2 + *(int *)(param_1 + 0x18);
  if (param_3 != (int *)0x0) {
    *param_3 = iVar2;
  }
  return param_4;
}

