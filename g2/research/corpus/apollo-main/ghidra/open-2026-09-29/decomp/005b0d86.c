
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005b0d86(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  byte bVar5;
  undefined4 uStack_10;
  
  piVar2 = _DAT_005b1a0c;
  iVar1 = DAT_005b15d8;
  uStack_10 = in_r3;
  if ((*_DAT_005b1a0c != 0) && (*(int *)(DAT_005b15d8 + 100) != 0)) {
    if ((*(int *)(DAT_005b15d8 + 0x68) != 0) &&
       (iVar3 = FUN_0043e2ea(*(undefined4 *)(DAT_005b15d8 + 0x68)), iVar3 != 0)) {
      FUN_0044d7b8(*(undefined4 *)(iVar1 + 0x68));
    }
    uVar4 = FUN_0043de82(*piVar2);
    *(undefined4 *)(iVar1 + 0x68) = uVar4;
    FUN_0043c0e4(iVar1 + 0x6c,0x10,0);
    FUN_0044129e(*(undefined4 *)(iVar1 + 0x68),0,0);
    FUN_0044131c(*(undefined4 *)(iVar1 + 0x68),0,0);
    FUN_0044146a(*(undefined4 *)(iVar1 + 0x68),0,0);
    func_0x005b0ac4(*(undefined4 *)(iVar1 + 0x68),0,0);
    FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x68),0x12);
    for (bVar5 = 0; bVar5 < 4; bVar5 = bVar5 + 1) {
      uVar4 = FUN_0043de82(*(undefined4 *)(iVar1 + 0x68));
      *(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c) = uVar4;
      FUN_0043f09a(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0,(uint)bVar5 * 0x28);
      FUN_0043f4c0(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0x1b8,0x28);
      uVar4 = FUN_0044104c(0);
      FUN_0044127e(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),uVar4,0);
      FUN_0044129e(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0xff,0);
      FUN_0044131c(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0,0);
      FUN_0044146a(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0,0);
      func_0x005b0ac4(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0,0);
      FUN_0043dfa4(*(undefined4 *)(iVar1 + (uint)bVar5 * 4 + 0x6c),0x12);
    }
    FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x68),0x1b8,0xa0);
    uStack_10 = 0;
    FUN_0043f6d6(*(undefined4 *)(iVar1 + 0x68),*(undefined4 *)(iVar1 + 100),1,0);
    FUN_005b0d24(iVar1,*(undefined1 *)(iVar1 + 0x97));
  }
  return uStack_10;
}

