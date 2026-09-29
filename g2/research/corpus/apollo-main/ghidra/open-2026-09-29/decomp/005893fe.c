
void FUN_005893fe(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 in_r3;
  
  iVar1 = DAT_00589934;
  if (((*(char *)(DAT_00589934 + 0xc3) != '\0') && (*(int *)(DAT_00589934 + 0xcc) != 0)) &&
     (uVar2 = FUN_005893f0(*(undefined4 *)(DAT_00589934 + 200)), *(uint *)(iVar1 + 0xcc) < uVar2)) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar4 = FUN_005893f0(*(undefined4 *)(iVar1 + 200));
      FUN_0043d574(2,DAT_00589944,DAT_00589940,DAT_0058993c,0x3d,DAT_00589938,uVar4,
                   *(undefined4 *)(iVar1 + 0xcc),*(undefined1 *)(iVar1 + 0xc4),in_r3);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      uVar4 = FUN_005893f0(*(undefined4 *)(iVar1 + 200));
      compress_log_output(0x8c00000,DAT_00589948,DAT_00589948,uVar4,*(undefined4 *)(iVar1 + 0xcc),
                          *(undefined1 *)(iVar1 + 0xc4));
    }
    FUN_0058966c();
  }
  return;
}

