
undefined4 FUN_00550d3c(byte param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  int iVar5;
  
  iVar1 = DAT_00550ff4;
  if (*(int *)(DAT_00550ff4 + 0xc) != 0) {
    for (bVar4 = 0; bVar4 < 10; bVar4 = bVar4 + 1) {
      if (*(int *)(iVar1 + (uint)bVar4 * 4 + 0x10) != 0) {
        FUN_0043ded4(*(undefined4 *)(iVar1 + (uint)bVar4 * 4 + 0x10),1);
      }
    }
    if (10 < param_1) {
      param_1 = 10;
    }
    if (param_1 == 0) {
      iVar2 = 0;
    }
    else {
      iVar2 = (param_1 - 1) * 8 + (uint)param_1 * 4;
    }
    iVar5 = 0;
    if (((param_1 != 0) && (param_1 < 3)) && (iVar5 = (0x1c - iVar2) / 2, iVar5 < 0)) {
      iVar5 = 0;
    }
    for (bVar4 = 0; bVar4 < param_1; bVar4 = bVar4 + 1) {
      iVar2 = *(int *)(iVar1 + (uint)bVar4 * 4 + 0x10);
      if (iVar2 != 0) {
        FUN_0043dfa4(iVar2,1);
        uVar3 = FUN_0044104c(DAT_00551810);
        FUN_0044127e(iVar2,uVar3,0);
        FUN_0043f6b8(iVar2,0xd,0,(uint)bVar4 * 0xc + iVar5);
        FUN_00441488(iVar2,0xff,0);
      }
    }
    FUN_0044ea04(*(undefined4 *)(iVar1 + 0xc),0,0);
  }
  return param_4;
}

