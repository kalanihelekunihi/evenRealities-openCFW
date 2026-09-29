
undefined4 FUN_1000a7f0(int *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int iVar4;
  
  iVar1 = DAT_1000a858;
  iVar4 = 0;
  iVar2 = 8;
  piVar3 = DAT_1000a854;
  do {
    if (*piVar3 == *param_1) {
      FUN_10011344(DAT_1000a854 + iVar4 * 2,param_1,8);
      return 0;
    }
    iVar4 = iVar4 + 1;
    piVar3 = piVar3 + 2;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  if ((*(uint *)(DAT_1000a858 + 0xc) < 8) && (*param_1 != 0)) {
    FUN_10011344(DAT_1000a858 + (*(uint *)(DAT_1000a858 + 0xc) + 10) * 8,param_1,8);
    *(int *)(iVar1 + 0xc) = *(int *)(iVar1 + 0xc) + 1;
    return 0;
  }
  return 0xffffffff;
}

