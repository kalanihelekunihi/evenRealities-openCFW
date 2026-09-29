
undefined4 FUN_005b6b58(void)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 in_r3;
  int iVar8;
  uint uVar9;
  
  iVar1 = DAT_005b7604;
  if (*(int *)(DAT_005b7604 + 0x28) != 0) {
    iVar2 = FUN_005b6a3a();
    uVar3 = FUN_005b4770();
    uVar9 = 0;
    if (0xc < (uVar3 & 0xffff)) {
      if ((iVar2 / 0x1c & 0xffffU) < 3) {
        uVar9 = 0;
      }
      else {
        uVar9 = iVar2 / 0x1c - 2;
      }
      if ((uVar3 - 0xc & 0xffff) < (uVar9 & 0xffff)) {
        uVar9 = uVar3 - 0xc;
      }
    }
    if ((uVar9 & 0xffff) != (uint)*(ushort *)(iVar1 + 0x60)) {
      FUN_005b6ac0(uVar9 & 0xffff);
    }
    if ((*(int *)(iVar1 + 0x24) != 0) && (*(int *)(iVar1 + 0x2c) != 0)) {
      iVar8 = (uVar3 & 0xffff) * 0x1c;
      iVar4 = FUN_0043fdda(*(undefined4 *)(iVar1 + 0x24));
      iVar5 = FUN_005b6a06();
      if ((iVar4 < iVar8) && (0 < iVar5)) {
        iVar8 = (iVar4 * iVar4) / iVar8;
        if (iVar8 < 0x1c) {
          iVar8 = 0x1c;
        }
        if (iVar4 < iVar8) {
          iVar8 = iVar4;
        }
        iVar6 = FUN_0043fe16(*(undefined4 *)(iVar1 + 0x1c));
        iVar7 = FUN_0043fce0(*(undefined4 *)(iVar1 + 0x24));
        FUN_0043f4c0(*(undefined4 *)(iVar1 + 0x2c),2,iVar8);
        FUN_0043f09a(*(undefined4 *)(iVar1 + 0x2c),iVar6 + -10,
                     ((iVar4 - iVar8) * iVar2) / iVar5 + iVar7);
        FUN_0043dfa4(*(undefined4 *)(iVar1 + 0x2c),1);
      }
      else {
        FUN_0043ded4(*(undefined4 *)(iVar1 + 0x2c),1);
      }
    }
  }
  return in_r3;
}

