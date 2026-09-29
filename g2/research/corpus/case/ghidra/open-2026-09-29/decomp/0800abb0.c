
void FUN_0800abb0(int param_1,int param_2)

{
  int *piVar1;
  uint uVar2;
  uint uVar3;
  
  piVar1 = DAT_0800ac00;
  uVar3 = DAT_0800ac00[3];
  uxListRemove(*DAT_0800ac00 + 4);
  if ((param_1 == -1) && (param_2 != 0)) {
    FUN_0800bfe2(DAT_0800ac04,*piVar1 + 4);
    return;
  }
  uVar2 = uVar3 + param_1;
  *(uint *)(*piVar1 + 4) = uVar2;
  if (uVar2 < uVar3) {
    FUN_0800bfb0(piVar1[0xe],*piVar1 + 4);
  }
  else {
    FUN_0800bfb0(piVar1[0xd],*piVar1 + 4);
    if (uVar2 < (uint)piVar1[10]) {
      piVar1[10] = uVar2;
      return;
    }
  }
  return;
}

