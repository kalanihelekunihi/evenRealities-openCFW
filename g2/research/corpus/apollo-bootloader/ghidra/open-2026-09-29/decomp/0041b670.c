
undefined4 FUN_0041b670(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  undefined4 in_r3;
  
  bVar1 = false;
  uVar3 = FUN_0041f424(0);
  puVar2 = DAT_0041b82c;
  if (uVar3 < *DAT_0041b828) {
    iVar4 = -1 - *DAT_0041b828;
  }
  else {
    iVar4 = -*DAT_0041b828;
  }
  uVar5 = uVar3 + iVar4;
  uVar6 = *DAT_0041b82c;
  iVar4 = uVar5 - *DAT_0041b82c * (uVar5 / *DAT_0041b82c);
  *DAT_0041b828 = uVar3 - iVar4;
  FUN_0041f440(0,*puVar2 - iVar4);
  FUN_0041b2f8();
  uVar3 = uVar5 / uVar6;
  while (uVar5 = uVar3 - 1, uVar3 != 0) {
    iVar4 = FUN_00418408();
    uVar3 = uVar5;
    if (iVar4 != 0) {
      bVar1 = true;
    }
  }
  if (bVar1) {
    *DAT_0041b830 = 0x10000000;
  }
  FUN_0041b30e(0);
  return in_r3;
}

