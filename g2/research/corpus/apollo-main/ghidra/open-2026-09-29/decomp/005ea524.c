
undefined4 FUN_005ea524(undefined2 param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  
  bVar1 = *(byte *)(param_2 + 1);
  if (bVar1 == 0) {
    iVar2 = FUN_005ea4f0(param_1,param_2);
    uVar3 = DAT_005eadd0;
    if ((iVar2 == 0) && (iVar2 = FUN_005ea2f2(param_2), uVar3 = DAT_005eadd0, iVar2 == 0)) {
      uVar3 = 0;
    }
  }
  else {
    uVar3 = DAT_005eadcc;
    if ((bVar1 != 2) && (uVar3 = DAT_005eadc4, 1 < bVar1)) {
      uVar3 = 0;
    }
  }
  return uVar3;
}

