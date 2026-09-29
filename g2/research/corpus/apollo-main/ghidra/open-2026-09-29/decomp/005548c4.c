
int FUN_005548c4(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  iVar2 = FUN_005546be(param_1,param_2,param_3,0x1c);
  iVar6 = DAT_005553c4;
  iVar3 = FUN_0043fdda(param_1);
  iVar4 = *(int *)(iVar6 + 0x10) * 0x1c;
  if (iVar3 < iVar4) {
    iVar4 = iVar4 - iVar3;
  }
  else {
    iVar4 = 0;
  }
  if ((*(uint *)(iVar6 + 0xc) < 4) || (*(int *)(DAT_00554d28 + 0x2c) + 4U < *(uint *)(iVar6 + 0xc)))
  {
    bVar1 = false;
  }
  else {
    bVar1 = true;
  }
  if (bVar1) {
    uVar5 = *(uint *)(iVar6 + 0x10) % 10;
    if (uVar5 != 0) {
      iVar6 = (uVar5 + 0x1e) * 0x1c;
      if (iVar3 < iVar6) {
        iVar6 = iVar6 - iVar3;
      }
      else {
        iVar6 = 0;
      }
      if (iVar6 < iVar4) {
        iVar4 = iVar6;
      }
    }
  }
  else if (((*(char *)(iVar6 + 0x28) == '\x01') && (*(int *)(iVar6 + 0x24) != 0)) &&
          (*(int *)(iVar6 + 0x10) != 0)) {
    iVar4 = *(int *)(iVar6 + 0x24) * ((*(int *)(iVar6 + 0x10) - 1U) / *(uint *)(iVar6 + 0x24)) *
            0x1c;
  }
  if (iVar2 <= iVar4) {
    iVar4 = iVar2;
  }
  return iVar4;
}

