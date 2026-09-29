
int FUN_00590e6c(undefined4 param_1,undefined4 param_2,undefined4 param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  
  iVar1 = FUN_00590d3c(param_2,param_1);
  iVar2 = FUN_00590d74(param_3,param_1);
  bVar6 = SBORROW4(iVar1,4);
  iVar3 = iVar1 + -4;
  if (iVar1 < 4) {
    bVar6 = SBORROW4(iVar2,7);
    iVar3 = iVar2 + -7;
  }
  if (((iVar3 < 0 == bVar6) || (7 < param_4 - 1U)) || (param_5 < 0)) {
    return -1;
  }
  if (param_5 < 1) {
    param_5 = 0;
  }
  else if (DAT_005915ac <= param_5) {
    param_5 = DAT_005915ac;
  }
  if (iVar2 < 5) {
    iVar3 = 0x14;
  }
  else {
    iVar3 = *(int *)(DAT_005915b0 + iVar1 * 0x10 + iVar2 * 8 + -0x28);
  }
  iVar5 = (int)((ulonglong)((longlong)((iVar1 + 1) * param_5) * (longlong)DAT_005915b4) >> 0x20);
  iVar5 = (iVar5 >> 10) - (iVar5 >> 0x1f);
  if (param_4 * iVar3 < iVar5) {
    iVar3 = iVar5;
    if (iVar2 < 5) {
LAB_00590f12:
      iVar4 = 400;
      goto LAB_00590efa;
    }
  }
  else {
    if (iVar2 < 5) {
      iVar3 = param_4 * 0x14;
      goto LAB_00590f12;
    }
    iVar3 = param_4 * *(int *)(DAT_005915b0 + iVar1 * 0x10 + iVar2 * 8 + -0x28);
  }
  iVar4 = *(int *)(DAT_005915b0 + iVar1 * 0x10 + iVar2 * 8 + -0x24);
LAB_00590efa:
  if (iVar3 < param_4 * iVar4) {
    if (iVar2 < 5) {
      iVar1 = 0x14;
    }
    else {
      iVar1 = *(int *)(DAT_005915b0 + iVar1 * 0x10 + iVar2 * 8 + -0x28);
    }
    iVar3 = iVar1 * param_4;
    if (iVar1 * param_4 < iVar5) {
      iVar3 = iVar5;
    }
  }
  else {
    if (iVar2 < 5) {
      iVar3 = 400;
    }
    else {
      iVar3 = *(int *)(DAT_005915b0 + iVar1 * 0x10 + iVar2 * 8 + -0x24);
    }
    iVar3 = iVar3 * param_4;
  }
  return iVar3;
}

