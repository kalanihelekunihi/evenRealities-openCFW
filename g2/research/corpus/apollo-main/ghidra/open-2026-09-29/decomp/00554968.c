
undefined8 FUN_00554968(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  iVar1 = DAT_005553c4;
  if (param_1 == 0) {
    iVar2 = 0;
  }
  else if (*(int *)(DAT_005553c4 + 0xc) == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = FUN_0043fdda();
    uVar3 = param_2 + 3;
    if (*(uint *)(iVar1 + 0xc) <= uVar3) {
      uVar3 = *(int *)(iVar1 + 0xc) - 1;
    }
    iVar4 = 0;
    for (; param_2 <= uVar3; param_2 = param_2 + 1) {
      if ((param_2 == *(int *)(iVar1 + 0xc) - 1U) && (*(uint *)(iVar1 + 0x10) % 10 != 0)) {
        iVar4 = *(uint *)(iVar1 + 0x10) + iVar4 + (*(uint *)(iVar1 + 0x10) / 10) * -10;
      }
      else {
        iVar4 = iVar4 + 10;
      }
    }
    if (iVar2 < iVar4 * 0x1c) {
      iVar2 = iVar4 * 0x1c - iVar2;
    }
    else {
      iVar2 = 0;
    }
  }
  return CONCAT44(param_4,iVar2);
}

