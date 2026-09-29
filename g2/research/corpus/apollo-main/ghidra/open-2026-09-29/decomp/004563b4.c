
undefined4 FUN_004563b4(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 in_r3;
  
  bVar1 = false;
  uVar3 = FUN_0048d654(0);
  puVar2 = DAT_00456570;
  if (uVar3 < *DAT_0045656c) {
    iVar4 = -1 - *DAT_0045656c;
  }
  else {
    iVar4 = -*DAT_0045656c;
  }
  uVar5 = uVar3 + iVar4;
  uVar6 = *DAT_00456570;
  iVar4 = uVar5 - *DAT_00456570 * (uVar5 / *DAT_00456570);
  *DAT_0045656c = uVar3 - iVar4;
  FUN_0048d670(0,*puVar2 - iVar4);
  ulSetInterruptMask();
  uVar3 = uVar5 / uVar6;
  while (uVar5 = uVar3 - 1, uVar3 != 0) {
    iVar4 = FUN_0045504c();
    uVar3 = uVar5;
    if (iVar4 != 0) {
      bVar1 = true;
    }
  }
  if (bVar1) {
    *DAT_00456574 = 0x10000000;
  }
  vClearInterruptMask(0);
  return in_r3;
}

